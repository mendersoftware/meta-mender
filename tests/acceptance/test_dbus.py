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
import tempfile
import time

from fabric import Connection
from multiprocessing import Process
from paramiko.client import WarningPolicy

from common import put_no_sftp

MENDER_CONF = """{
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


@pytest.fixture
def setup_mender_client_dbus(bitbake_variables, connection):
    conffile = "/data/etc/mender/mender.conf"
    backup = f"{conffile}.backup"
    bdir = os.path.dirname(backup)
    connection.run(
        f"mkdir -p {bdir} && if [ -e {conffile} ]; then cp {conffile} {backup}; fi"
    )

    tf = tempfile.NamedTemporaryFile()
    with open(tf.name, "w") as fd:
        fd.write(MENDER_CONF)

    put_no_sftp(tf.name, connection, remote=conffile)

    try:
        yield True
    finally:
        connection.run(
            f"if [ -e {backup} ]; then dd if={backup} of=$(realpath {conffile}); fi"
        )


@pytest.mark.usefixtures("setup_board", "bitbake_path")
class TestDBus:
    # this is a portion of the JWT token served by the Mender mock server:
    # see: meta-mender-ci/recipes-testing/mender-mock-server/mender-mock-server.py
    JWT_TOKEN = "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9."

    @pytest.mark.min_mender_version("2.5.0")
    def test_dbus_system_configuration_file(self, bitbake_variables, connection):
        """Test that D-Bus configuration file is correctly installed."""

        output = connection.run(
            "cat /usr/share/dbus-1/system.d/io.mender.AuthenticationManager.conf"
        ).stdout.strip()
        assert "io.mender.AuthenticationManager" in output

    @pytest.mark.min_mender_version("2.5.0")
    def test_dbus_get_jwt_token(
        self, bitbake_variables, connection, setup_mender_client_dbus
    ):
        """Test the JWT token can be retrieved using D-Bus."""

        # bootstrap the client
        connection.run("mender bootstrap --forcebootstrap")

        # start the mender-client service
        connection.run("systemctl start mender-client")

        # get the JWT token via D-Bus
        try:
            output = ""
            for i in range(12):
                result = connection.run(
                    "dbus-send --system --dest=io.mender.AuthenticationManager --print-reply /io/mender/AuthenticationManager io.mender.Authentication1.GetJwtToken || true"
                )
                if self.JWT_TOKEN in result.stdout:
                    output = result.stdout
                    break
                time.sleep(5)

            assert f'string "{self.JWT_TOKEN}' in output
        finally:
            connection.run("systemctl stop mender-client")

    @pytest.mark.min_mender_version("2.5.0")
    def test_dbus_fetch_jwt_token(
        self, bitbake_variables, connection, second_connection, setup_mender_client_dbus
    ):
        """Test the JWT token can be fetched using D-Bus."""

        # bootstrap the client
        connection.run("mender bootstrap --forcebootstrap")

        # start the mender-client service
        connection.run("systemctl start mender-client")

        # start monitoring the D-Bus
        def dbus_monitor():
            second_connection.run(
                "dbus-monitor --system \"type='signal',interface='io.mender.Authentication1'\" > /tmp/dbus-monitor.log"
            )

        p = Process(target=dbus_monitor, daemon=True)
        p.start()

        # get the JWT token via D-Bus
        try:
            # fetch the JWT token
            fetched = False
            for i in range(30):
                result = connection.run(
                    "dbus-send --system --dest=io.mender.AuthenticationManager --print-reply /io/mender/AuthenticationManager io.mender.Authentication1.FetchJwtToken || true"
                )
                if "true" in result.stdout:
                    fetched = True
                    break

            # fetch was successful
            assert fetched

            # verify we received the D-Bus signal ValidJwtTokenAvailable
            found = False
            output = ""
            for i in range(12):
                output = connection.run("cat /tmp/dbus-monitor.log").stdout.strip()
                if (
                    "path=/io/mender/AuthenticationManager; interface=io.mender.Authentication1; member=ValidJwtTokenAvailable"
                    in output
                ):
                    found = True
                    break
                time.sleep(5)
            assert found, output

            # token is now available
            result = connection.run(
                "dbus-send --system --dest=io.mender.AuthenticationManager --print-reply /io/mender/AuthenticationManager io.mender.Authentication1.GetJwtToken"
            )
            output = result.stdout.strip()
            assert f'string "{self.JWT_TOKEN}' in output
        finally:
            p.terminate()
            connection.run("systemctl stop mender-client")
            connection.run("rm -f /tmp/dbus-monitor.log")
