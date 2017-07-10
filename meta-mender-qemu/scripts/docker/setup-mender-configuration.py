#!/usr/bin/env python3

import argparse
import json
import os
import subprocess
import sys

def get(remote_path, local_path, rootfs):
    subprocess.check_call(["debugfs", "-R", "dump -p %s %s" % (remote_path, local_path), rootfs],
                          stderr=subprocess.STDOUT)

def put(local_path, remote_path, rootfs):
    proc = subprocess.Popen(["debugfs", "-w", rootfs], stdin=subprocess.PIPE,
                            stderr=subprocess.STDOUT)
    proc.stdin.write(("cd %s\n" % os.path.dirname(remote_path)).encode())
    proc.stdin.write(("rm %s\n" % os.path.basename(remote_path)).encode())
    proc.stdin.write(("write %s %s\n" % (local_path, os.path.basename(remote_path))).encode())
    proc.stdin.close()
    ret = proc.wait()
    assert ret == 0

def extract_ext4(sdimg, rootfs):
    return manipulate_ext4(sdimg=sdimg, rootfs=rootfs, write=False)

def insert_ext4(sdimg, rootfs):
    return manipulate_ext4(sdimg=sdimg, rootfs=rootfs, write=True)

def manipulate_ext4(sdimg, rootfs, write):
    # calls partx with --show --bytes --noheadings, sample output:
    #
    # $ partx -sbg core-image-full-cmdline-vexpress-qemu.sdimg
    # NR  START    END SECTORS      SIZE NAME UUID  <-- NOTE: this is not shown
    # 1  49152  81919   32768  16777216      a38e337d-01
    # 2  81920 294911  212992 109051904      a38e337d-02
    # 3 294912 507903  212992 109051904      a38e337d-03
    # 4 507904 770047  262144 134217728      a38e337d-04
    output = subprocess.check_output(["partx", "-sbg", sdimg])
    for line in output.decode().split('\n'):
        columns = line.split()
        # This blindly assumes that rootfs is on partition 2.
        if columns[0] == "2":
            if write:
                subprocess.check_call(["dd", "if=%s" % rootfs, "of=%s" % sdimg,
                                       "seek=%s" % columns[1],
                                       "count=%d" % (int(columns[3])),
                                       "conv=notrunc"],
                                      stderr=subprocess.STDOUT)
            else:
                subprocess.check_call(["dd", "if=%s" % sdimg, "of=%s" % rootfs,
                                       "skip=%s" % columns[1],
                                       "count=%d" % (int(columns[3]))],
                                      stderr=subprocess.STDOUT)
            break
    else:
        raise Exception("%s not found in fdisk output: %s" % (sdimg, output))

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--sdimg", help="Sdimg to modify", required=True)
    parser.add_argument("--tenant-token", help="tenant token to use by client")
    parser.add_argument("--server-crt", help="server.crt file to put in image")
    parser.add_argument("--server-url", help="Server address to put in configuration")
    parser.add_argument("--verify-key", help="Key used to verify signed image")
    args = parser.parse_args()

    if len(sys.argv) == 1:
        parser.print_help()
        return

    # Extract ext4 image from sdimg.
    rootfs = "%s.ext4" % args.sdimg
    extract_ext4(sdimg=args.sdimg, rootfs=rootfs)

    if args.tenant_token:
        get(local_path="mender.conf",
            remote_path="/etc/mender/mender.conf",
            rootfs=rootfs)
        with open("mender.conf") as fd:
            conf = json.load(fd)
        conf['TenantToken'] = args.tenant_token
        with open("mender.conf", "w") as fd:
            json.dump(conf, fd, indent=4, sort_keys=True)
        put(local_path="mender.conf",
            remote_path="/etc/mender/mender.conf",
            rootfs=rootfs)
        os.unlink("mender.conf")

    if args.server_crt:
        put(local_path=args.server_crt,
            remote_path="/etc/mender/server.crt",
            rootfs=rootfs)

    if args.server_url:
        get(local_path="mender.conf",
            remote_path="/etc/mender/mender.conf",
            rootfs=rootfs)
        with open("mender.conf") as fd:
            conf = json.load(fd)
        conf['ServerURL'] = args.server_url
        with open("mender.conf", "w") as fd:
            json.dump(conf, fd, indent=4, sort_keys=True)
        put(local_path="mender.conf",
            remote_path="/etc/mender/mender.conf",
            rootfs=rootfs)
        os.unlink("mender.conf")

    if args.verify_key:
        key_sdimg_location = "/etc/mender/artifact-verify-key.pem"
        if not os.path.exists(args.verify_key):
            raise SystemExit("failed to load file: " + args.verify_key)
        get(local_path="mender.conf",
            remote_path="/etc/mender/mender.conf",
            rootfs=rootfs)
        put(local_path=args.verify_key,
            remote_path=key_sdimg_location,
            rootfs=rootfs)
        with open("mender.conf") as fd:
            conf = json.load(fd)
            conf['ArtifactVerifyKey'] = key_sdimg_location
        with open("mender.conf", "w") as fd:
            json.dump(conf, fd, indent=4, sort_keys=True)
        put(local_path="mender.conf",
            remote_path="/etc/mender/mender.conf",
            rootfs=rootfs)
        os.unlink("mender.conf")


    # Put back ext4 image into sdimg.
    insert_ext4(sdimg=args.sdimg, rootfs=rootfs)
    os.unlink(rootfs)

main()
