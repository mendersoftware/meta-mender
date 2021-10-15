#!/usr/bin/env python3

from subprocess import check_call

import hashlib
import shutil
import struct
import sys
import os
import re

# 6 bytes header + 2*256*2 paths UTF16LE
AB_SIZE = 1030
AB_FORMAT = "6B512s512s"

# 256 bits -> 256/8 = 32 bytes
SHA256_SIZE = 32

ROOTFS_OFFSET = 1

def try_read_file(path, length):
    """Try to read the designated file with the specified length. Fill with
       zeroes if it does not exist."""
    try:
        with open(path, "rb") as f:
            bytes = f.read()

            # If the file was as long as expected, return its contents
            if len(bytes) == length:
                return bytes
    except FileNotFoundError:
        pass

    # Otherwise return zeroes
    return bytearray(length)

def write_file(path, contents):
    with open(path, "wb") as f:
        f.write(contents)

def write_config(esp_base, config):
    """Commit the specified config to disk."""
    config_hash = hashlib.sha256(config).digest()

    os.makedirs("{}/loader/main".format(esp_base), exist_ok=True)
    write_file("{}/loader/main/config".format(esp_base), config)
    write_file("{}/loader/main/config.sha256".format(esp_base), config_hash)

    os.makedirs("{}/loader/backup".format(esp_base), exist_ok=True)
    write_file("{}/loader/backup/config".format(esp_base), config)
    write_file("{}/loader/backup/config.sha256".format(esp_base), config_hash)

def get_config(esp_base):
    """Get a config object from disk, (re-)creating if it does not yet exist
       or is invalid."""
    config_a = try_read_file("{}/loader/main/config".format(esp_base), AB_SIZE)
    config_b = try_read_file("{}/loader/backup/config".format(esp_base), AB_SIZE)

    sum_a = try_read_file("{}/loader/main/config.sha256".format(esp_base), SHA256_SIZE)
    sum_b = try_read_file("{}/loader/backup/config.sha256".format(esp_base), SHA256_SIZE)

    hash_a = hashlib.sha256(config_a).digest()
    hash_b = hashlib.sha256(config_b).digest()

    a_valid = sum_a == hash_a
    b_valid = sum_b == hash_b

    # Can happen if a commit was interrupted
    # Assume A is the intended configuration and use that
    if a_valid and b_valid and config_a != config_b:
        b_valid = False

    if a_valid and not b_valid:
        # Recover config B from A
        write_config(esp_base, config_a)
        return config_a

    if b_valid and not a_valid:
        # Recover config A from B
        write_config(esp_base, config_b)
        return config_b

    if not a_valid and not b_valid:
        # A and B configs invalid, use defaults
        write_config(esp_base, default_config())
        return default_config()

    # Both valid, return A
    return config_a

def parse_config(config):
    _, pending, boot_count, max_boot_count, active_slot, _, a_efi, b_efi = struct.unpack(AB_FORMAT, config)

    active_slot = active_slot & 0x1
    max_boot_count = max_boot_count

    return {
        "pending": pending,
        "boot_count": boot_count,
        "max_boot_count": max_boot_count,
        "active_slot": active_slot,
        "a_efi": a_efi.decode("UTF-16LE").rstrip("\x00"),
        "b_efi": b_efi.decode("UTF-16LE").rstrip("\x00")
    }

def serialize_config(config):

    return struct.pack(
        AB_FORMAT,
        0x1,
        config["pending"],
        config["boot_count"], 
        config["max_boot_count"],
        config["active_slot"] & 0x1,
        0x0,
        config["a_efi"].encode("UTF-16LE"),
        config["b_efi"].encode("UTF-16LE")
    )

def default_config():
    config = {}

    config["pending"] = 0
    config["boot_count"] = 0
    config["max_boot_count"] = 1
    config["active_slot"] = 0
    config["a_efi"] = "\\EFI\\Linux\\bootx64_a.efi"
    config["b_efi"] = "\\EFI\\Linux\\bootx64_b.efi"

    return serialize_config(config)

def root_device():
    mounts = None

    # /dev/sda2 / ext4 rw,relatime,errors=remount-ro 0 0
    with open("/proc/mounts", "r") as f:
        mounts = f.readlines()

    # /dev/sda2 /
    mounts = [m.split(" ")[0:2] for m in mounts]
    mounts = [m[0] for m in mounts if m[1] == "/"]

    # /dev/sda
    return re.sub("\d+$", "", mounts[0])

def extract_kernel(esp_base, config, slot):
    # Set up pick from inactive slot
    slot_name = "a" if slot == 0 else "b"
    partition_name = "{}{}".format(root_device(), slot + ROOTFS_OFFSET)
    inactive_base = "/mnt/inactive"

    source_kernel_path = "{}/bin/bootx64_{}.efi".format(inactive_base, slot_name)
    target_kernel_path = "{}{}".format(esp_base, config["{}_efi".format(slot_name)].replace("\\", "/"))

    # Mount inactive slot and extract file
    os.makedirs(inactive_base, exist_ok=True)
    check_call(["mount", partition_name, inactive_base])

    shutil.copyfile(source_kernel_path, target_kernel_path);

    check_call(["umount", inactive_base])
    os.rmdir(inactive_base)
    os.sync()

def set_mender_key(esp_base, config, key, value):
    if key == "mender_boot_part":
        v = int(value) - ROOTFS_OFFSET
        config["active_slot"] = v
        extract_kernel(esp_base, config, v)
    elif key == "upgrade_available":
        config["pending"] = int(value)
        config["boot_count"] = 0
    elif key == "bootcount":
        config["boot_count"] = int(value)

def get_mender_key(config, key):
    if key == "mender_boot_part" or key == "mender_boot_part_hex":
        return config["active_slot"] + ROOTFS_OFFSET
    elif key == "mender_uboot_separator":
        return "1"
    elif key == "upgrade_available":
        return config["pending"]
    elif key == "bootcount":
        return config["boot_count"]
    else:
        return ""

def to_kv(attributes):
    if len(attributes) == 2:
        return [a.strip() for a in attributes]
    else:
        return [attributes[0].strip(), None]

def set_mender_keys(esp_base, config, attributes):
    kvs = [to_kv(re.split("=| ", kv, 1)) for kv in attributes]

    for key, value in kvs:
        set_mender_key(esp_base, config, key, value)

def print_mender_keys(config, keys):
    for key in keys:
        print("{}={}".format(key, get_mender_key(config, key)))

def fw_printenv(config):
    if len(sys.argv[1:]) > 0:
        keys = sys.argv[1:]
    else:
        keys = ["mender_boot_part", "upgrade_available", "bootcount"]
    print_mender_keys(config, keys)

def fw_setenv(esp_base, config):
    lines = sys.stdin.readlines()
    set_mender_keys(esp_base, config, lines)
    write_config(esp_base, serialize_config(config))

def fw_init(path):
    write_config(path, default_config())

def fw_cmd():
    cmd = sys.argv[1] if len(sys.argv) > 1 else ''

    if cmd in "init":
        if len(sys.argv) == 3:
            fw_init(sys.argv[2])
            sys.exit(0)

    sys.exit(1)

if __name__ == "__main__":
    progname = sys.argv[0]
    if not (progname.endswith("fw_printenv") or progname.endswith("fw_setenv")):
        fw_cmd()

    esp_base = "/boot"
    config = parse_config(get_config(esp_base))

    if "fw_printenv" in progname:
        fw_printenv(config)
    elif "fw_setenv" in progname:
        fw_setenv(esp_base, config)
    else:
        sys.exit(1)
