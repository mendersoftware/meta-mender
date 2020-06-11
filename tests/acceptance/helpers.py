#!/usr/bin/python
# Copyright 2020 Northern.tech AS
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

import os
import re
import subprocess
import requests

from common import *


class Helpers:
    @staticmethod
    def upload_to_s3(artifact):
        subprocess.call(
            ["s3cmd", "--follow-symlinks", "put", artifact, "s3://mender/temp/"]
        )
        subprocess.call(
            ["s3cmd", "setacl", "s3://mender/temp/%s" % artifact, "--acl-public"]
        )

    @staticmethod
    def get_env_offsets(bitbake_variables):
        offsets = [0, 0]

        alignment = int(bitbake_variables["MENDER_PARTITION_ALIGNMENT"])
        env_size = os.stat(
            os.path.join(bitbake_variables["DEPLOY_DIR_IMAGE"], "uboot.env")
        ).st_size
        offsets[0] = int(bitbake_variables["MENDER_UBOOT_ENV_STORAGE_DEVICE_OFFSET"])
        offsets[1] = offsets[0] + int(env_size / 2)

        assert offsets[0] % alignment == 0
        assert offsets[1] % alignment == 0

        return offsets

    @staticmethod
    def get_env_checksums(bitbake_variables, connection):
        checksums = [0, 0]

        offsets = Helpers.get_env_offsets(bitbake_variables)
        dev = bitbake_variables["MENDER_STORAGE_DEVICE"]

        connection.run(
            "dd if=%s of=/data/env1.tmp bs=1 count=4 skip=%d" % (dev, offsets[0])
        )
        connection.run(
            "dd if=%s of=/data/env2.tmp bs=1 count=4 skip=%d" % (dev, offsets[1])
        )

        get_no_sftp("/data/env1.tmp", connection)
        get_no_sftp("/data/env2.tmp", connection)
        connection.run("rm -f /data/env1.tmp /data/env2.tmp")

        env = open("env1.tmp", "rb")
        checksums[0] = env.read()
        env.close()
        env = open("env2.tmp", "rb")
        checksums[1] = env.read()
        env.close()

        os.remove("env1.tmp")
        os.remove("env2.tmp")

        return checksums

    @staticmethod
    def corrupt_middle_byte(fd):
        # Corrupt the middle byte in the contents.
        middle = int(os.fstat(fd.fileno()).st_size / 2)
        fd.seek(middle)
        middle_byte = int(fd.read(1).encode().hex(), base=16)
        fd.seek(middle)
        # Flip lowest bit.
        fd.write("%c" % (middle_byte ^ 0x1))

    @staticmethod
    def get_file_flag(bitbake_variables):
        if version_is_minimum(bitbake_variables, "mender-artifact", "3.0.0"):
            return "-f"
        else:
            return "-u"

    @staticmethod
    def get_install_flag(connection):
        output = connection.run("mender --help 2>&1", warn=True).stdout
        if re.search(r"^\s*install(\s|$)", output, flags=re.MULTILINE):
            return "install"
        elif re.search(r"^\s*-install(\s|$)", output, flags=re.MULTILINE):
            return "-install"
        else:
            return "-rootfs"

    @staticmethod
    def install_update(image, conn, http_server, board_type, use_s3, s3_address):
        # We want `image` to be in the current directory because we use Python's
        # `http.server`. If it isn't, make a symlink, and relaunch.
        if os.path.dirname(os.path.abspath(image)) != os.getcwd():
            os.symlink(image, "temp-artifact.mender")
            try:
                return Helpers.install_update(
                    "temp-artifact.mender",
                    conn,
                    http_server,
                    board_type,
                    use_s3,
                    s3_address,
                )
            finally:
                os.unlink("temp-artifact.mender")

        http_server_location = http_server
        install_flag = Helpers.get_install_flag(conn)

        http_server = None
        if "qemu" not in board_type or use_s3:
            Helpers.upload_to_s3(image)
            http_server_location = "{}/mender/temp".format(s3_address)
        else:
            http_server = subprocess.Popen(["python3", "-m", "http.server"])
            assert http_server
            time.sleep(1)
            assert (
                requests.head("http://localhost:8000/%s" % (image)).status_code == 200
            )

        try:
            output = conn.run(
                "mender %s http://%s/%s" % (install_flag, http_server_location, image)
            )
            print("output from rootfs update: ", output.stdout)
        finally:
            if http_server:
                try:
                    status_code = requests.head(
                        "http://localhost:8000/%s" % (image)
                    ).status_code
                    if status_code != 200:
                        print(
                            "warning: http server is not accessible, status code %d"
                            % (status_code)
                        )
                except Exception as e:
                    print("Exception during request" + str(e))
                http_server.terminate()
