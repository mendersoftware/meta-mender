#!/usr/bin/env python3
# Copyright 2025 Northern.tech AS
#
#    Licensed under the Apache License, Version 2.0 (the "License");
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.

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
    parser.add_argument("--server-ip", help="Server IP to add to /etc/hosts pointing to Server host. Requires --server-url.")
    parser.add_argument("--verify-key", help="Key used to verify signed image")
    parser.add_argument("--mender-gateway-conffile", help="Configuration file to be copied to /etc/mender/mender-gateway.conf")
    args = parser.parse_args()

    if len(sys.argv) == 1:
        parser.print_help()
        return

    # Extract ext4 image from img.
    rootfs = "%s.ext4" % args.img
    extract_ext4(img=args.img, rootfs=rootfs)

    get(local_path="mender.conf",
        remote_path="/etc/mender/mender.conf",
        rootfs=rootfs)
    with open("mender.conf") as fd:
        conf = json.load(fd)
        write_config = False

    if args.tenant_token:
        conf['TenantToken'] = args.tenant_token
        write_config = True

    if args.server_crt:
        put(local_path=args.server_crt,
            remote_path="/etc/mender/server.crt",
            rootfs=rootfs)

    if args.server_url:
        conf['ServerURL'] = args.server_url
        write_config = True

    if args.server_ip:
        if not args.server_url:
            print("Error: --server-ip requires --server-url")
            sys.exit(1)
        get(local_path="hosts",
            remote_path="/etc/hosts",
            rootfs=rootfs)
        with open("hosts", "a") as fd:
            fd.write("\n")
            fd.write("# Added by setup-mender-configuration.py\n")
            server_host = args.server_url.removeprefix("http://").removeprefix("https://")
            fd.write(f"{args.server_ip} {server_host}\n")
        put(local_path="hosts",
            remote_path="/etc/hosts",
            rootfs=rootfs)
        os.unlink("hosts")

    if args.verify_key:
        key_img_location = "/etc/mender/artifact-verify-key.pem"
        if not os.path.exists(args.verify_key):
            raise SystemExit("failed to load file: " + args.verify_key)
        put(local_path=args.verify_key,
            remote_path=key_img_location,
            rootfs=rootfs)
        conf['ArtifactVerifyKey'] = key_img_location
        write_config = True

    if args.docker_ip:
        with open("mender-inventory-docker-ip", "w") as fd:
            fd.write("""#!/bin/sh
cat <<EOF
network_interfaces=docker
%s
EOF
""" % "\n".join(["ipv4_docker=%s" % ip for ip in args.docker_ip.split()]))
        os.chmod("mender-inventory-docker-ip", stat.S_IRWXU|stat.S_IRGRP|stat.S_IXGRP|stat.S_IROTH|stat.S_IXOTH)
        put(local_path="mender-inventory-docker-ip",
            remote_path="/usr/share/mender/inventory/mender-inventory-docker-ip",
            rootfs=rootfs)
        os.unlink("mender-inventory-docker-ip")

    if write_config:
        with open("mender.conf", "w") as fd:
            json.dump(conf, fd, indent=4, sort_keys=True)
            fd.write("\n")
        put(local_path="mender.conf",
            remote_path="/etc/mender/mender.conf",
            rootfs=rootfs)
        os.unlink("mender.conf")

    if args.mender_gateway_conffile:
        put(local_path=args.mender_gateway_conffile,
            remote_path="/etc/mender/mender-gateway.conf",
            rootfs=rootfs)

    # Put back ext4 image into img.
    insert_ext4(img=args.img, rootfs=rootfs)
    os.unlink(rootfs)

if __name__ == "__main__":
    main()
