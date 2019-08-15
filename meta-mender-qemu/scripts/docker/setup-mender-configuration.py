#!/usr/bin/env python3

import argparse
import json
import os
import stat
import sys

from ext4_manipulator import get, put, extract_ext4, insert_ext4

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--img", help="Img to modify", required=True)
    parser.add_argument("--docker-ip", help="IP (in IP/netmask format) to report as Docker IP")
    parser.add_argument("--tenant-token", help="tenant token to use by client")
    parser.add_argument("--server-crt", help="server.crt file to put in image")
    parser.add_argument("--server-url", help="Server address to put in configuration")
    parser.add_argument("--verify-key", help="Key used to verify signed image")
    args = parser.parse_args()

    if len(sys.argv) == 1:
        parser.print_help()
        return

    # Extract ext4 image from img.
    rootfs = "%s.ext4" % args.img
    extract_ext4(img=args.img, rootfs=rootfs)

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
        key_img_location = "/etc/mender/artifact-verify-key.pem"
        if not os.path.exists(args.verify_key):
            raise SystemExit("failed to load file: " + args.verify_key)
        get(local_path="mender.conf",
            remote_path="/etc/mender/mender.conf",
            rootfs=rootfs)
        put(local_path=args.verify_key,
            remote_path=key_img_location,
            rootfs=rootfs)
        with open("mender.conf") as fd:
            conf = json.load(fd)
            conf['ArtifactVerifyKey'] = key_img_location
        with open("mender.conf", "w") as fd:
            json.dump(conf, fd, indent=4, sort_keys=True)
        put(local_path="mender.conf",
            remote_path="/etc/mender/mender.conf",
            rootfs=rootfs)
        os.unlink("mender.conf")

    if args.docker_ip:
        with open("mender-inventory-docker-ip", "w") as fd:
            fd.write("""#!/bin/sh
cat <<EOF
network_interfaces=docker
ipv4_docker=%s
EOF
""" % args.docker_ip)
        os.chmod("mender-inventory-docker-ip", stat.S_IRWXU|stat.S_IRGRP|stat.S_IXGRP|stat.S_IROTH|stat.S_IXOTH)
        put(local_path="mender-inventory-docker-ip",
            remote_path="/usr/share/mender/inventory/mender-inventory-docker-ip",
            rootfs=rootfs)
        os.unlink("mender-inventory-docker-ip")


    # Put back ext4 image into img.
    insert_ext4(img=args.img, rootfs=rootfs)
    os.unlink(rootfs)

if __name__ == "__main__":
    main()
