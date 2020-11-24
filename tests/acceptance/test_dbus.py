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
import pytest
import time

from common import put_no_sftp


@pytest.mark.usefixtures("setup_board", "bitbake_path")
class TestDBUS:
    @pytest.mark.min_mender_version("2.6.0")
    def test_dbus_system_configuration_file(self, bitbake_variables, connection):
        """Test that DBus configuration file is correctly installed."""

        output = connection.run(
            "cat /usr/share/dbus-1/system.d/io.mender.AuthenticationManager.conf"
        ).stdout.strip()
        assert "io.mender.AuthenticationManager" in output

    @pytest.mark.min_mender_version("2.6.0")
    def test_dbus_get_jwt_token(self, bitbake_variables, connection):
        """Test JWT token can be retrieved using DBus."""
        conffile = "/data/etc/mender/mender.conf"
        backup = "%s.backup" % conffile
        bdir = os.path.dirname(backup)
        connection.run(
            "mkdir -p %s && if [ -e %s ]; then cp %s %s; fi"
            % (bdir, conffile, conffile, backup)
        )

        with open("tmpfile", "w") as fd:
            fd.write(
                """{
    "ClientProtocol": "https",
    "HttpsClient": {
        "SkipVerify": true
    },
    "InventoryPollIntervalSeconds": 5,
    "RetryPollIntervalSeconds": 5,
    "ServerCertificate": "/usr/share/doc/mender-client/examples/demo.crt",
    "SkipVerify": true,
    "ServerURL": "https://localhost:8443",
    "DBus": {
        "Enabled": true
    }
}
"""
            )
        try:
            put_no_sftp("tmpfile", connection, remote=conffile)
        finally:
            os.remove("tmpfile")

        result = connection.run("mender bootstrap --forcebootstrap")
        assert result.exited == 0

        result = connection.run("systemctl start mender-client")
        assert result.exited == 0

        # this is a portion of the JWT token served by the Mender mock server:
        # see: meta-mender-ci/recipes-testing/mender-mock-server/mender-mock-server.py
        token = "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9."

        try:
            output = ""
            for i in range(60):
                result = connection.run(
                    "dbus-send --system --dest=io.mender.AuthenticationManager --print-reply /io/mender/AuthenticationManager io.mender.Authentication1.GetJwtToken || true"
                )
                if result.exited == 0 and token in result.stdout:
                    output = result.stdout
                    break
                # sleep one second before retrying
                time.sleep(1)

            assert token in output
        finally:
            result = connection.run("systemctl stop mender-client")
            assert result.exited == 0

            connection.run(
                "if [ -e %s ]; then dd if=%s of=$(realpath %s); fi"
                % (backup, backup, conffile)
            )
