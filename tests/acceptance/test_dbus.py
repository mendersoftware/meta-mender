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

from multiprocessing import Process

from utils.common import put_no_sftp

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


MENDER_STATE_FILES = (
    "/var/lib/mender/mender-agent.pem",
    "/var/lib/mender/mender-store",
    "/var/lib/mender/mender-store-lock",
)


@pytest.fixture
def setup_mender_client_dbus(request, bitbake_variables, connection):
    conffile = "/data/etc/mender/mender.conf"
    backup = f"{conffile}.backup"
    bdir = os.path.dirname(backup)
    result = connection.run(
        f"mkdir -p {bdir} && if [ -e {conffile} ]; then cp {conffile} {backup}; fi"
    )
    assert result.exited == 0

    tf = tempfile.NamedTemporaryFile()
    with open(tf.name, "w") as fd:
        fd.write(MENDER_CONF)

    put_no_sftp(tf.name, connection, remote=conffile)

    def fin():
        connection.run(
            f"if [ -e {backup} ]; then dd if={backup} of=$(realpath {conffile}); fi"
        )

    request.addfinalizer(fin)


@pytest.mark.usefixtures("setup_board", "bitbake_path")
@pytest.mark.not_for_machine("vexpress-qemu-flash")
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
    def test_dbus_non_root_access(self, bitbake_variables, connection):
        """Test that only root user can access Mender DBus API."""

        # This is the command that is expected to fail for non-root user
        dbus_send_command = "dbus-send --system --dest=io.mender.AuthenticationManager --print-reply /io/mender/AuthenticationManager io.mender.Authentication1.GetJwtToken"

        try:
            connection.run("mender bootstrap", warn=True)
            connection.run("systemctl start mender-client")

            # Wait one state machine cycle for the D-Bus API to be available
            for _ in range(12):
                result = connection.run("journalctl -u mender-client")
                if "Authorize failed:" in result.stdout:
                    break
                time.sleep(5)
            else:
                pytest.fail("failed to detect a full state machine cycle")

            result = connection.run(dbus_send_command)
            assert "string" in result.stdout, result.stdout

            result = connection.run(
                "sudo -u mender-ci-tester %s" % dbus_send_command, warn=True
            )
            assert result.exited == 1
            assert (
                "Error org.freedesktop.DBus.Error.AccessDenied" in result.stderr
            ), result.stderr

        finally:
            connection.run("systemctl stop mender-client")
            connection.run("rm -f %s" % " ".join(MENDER_STATE_FILES))

    @pytest.mark.min_mender_version("2.5.0")
    def test_dbus_get_jwt_token(
        self, bitbake_variables, connection, setup_mender_client_dbus
    ):
        """Test the JWT token can be retrieved using D-Bus."""

        try:
            # bootstrap the client
            result = connection.run("mender bootstrap --forcebootstrap")
            assert result.exited == 0

            # start the mender-client service
            result = connection.run("systemctl start mender-client")
            assert result.exited == 0

            # get the JWT token via D-Bus
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
            connection.run("rm -f %s" % " ".join(MENDER_STATE_FILES))

    @pytest.mark.min_mender_version("2.5.0")
    def test_dbus_fetch_jwt_token(
        self, bitbake_variables, connection, second_connection, setup_mender_client_dbus
    ):
        """Test the JWT token can be fetched using D-Bus."""

        # start monitoring the D-Bus
        def dbus_monitor():
            second_connection.run(
                "dbus-monitor --system \"type='signal',interface='io.mender.Authentication1'\" > /tmp/dbus-monitor.log"
            )

        p = Process(target=dbus_monitor, daemon=True)
        p.start()

        # get the JWT token via D-Bus
        try:
            # bootstrap the client
            result = connection.run("mender bootstrap --forcebootstrap")
            assert result.exited == 0

            # start the mender-client service
            result = connection.run("systemctl start mender-client")
            assert result.exited == 0

            # fetch the JWT token
            fetched = False
            for i in range(12):
                result = connection.run(
                    "dbus-send --system --dest=io.mender.AuthenticationManager --print-reply /io/mender/AuthenticationManager io.mender.Authentication1.FetchJwtToken || true"
                )
                if "true" in result.stdout:
                    fetched = True
                    break
                time.sleep(5)

            # fetch was successful
            assert fetched

            # verify we received the D-Bus signal JwtTokenStateChange and that it contains the JWT token
            found = False
            output = ""
            for i in range(12):
                output = connection.run("cat /tmp/dbus-monitor.log").stdout.strip()
                if (
                    "path=/io/mender/AuthenticationManager; interface=io.mender.Authentication1; member=JwtTokenStateChange"
                    in output
                ):
                    found = True
                    break
                time.sleep(5)
            assert found, output
            assert f'string "{self.JWT_TOKEN}' in output

            # token is now available also via GetJwtToken
            # Disabled due to MEN-4294
            # result = connection.run(
            #     "dbus-send --system --dest=io.mender.AuthenticationManager --print-reply /io/mender/AuthenticationManager io.mender.Authentication1.GetJwtToken"
            # )
            # assert result.exited == 0

            # output = result.stdout.strip()
            # assert f'string "{self.JWT_TOKEN}' in output
        finally:
            p.terminate()
            connection.run("systemctl stop mender-client")
            connection.run("rm -f %s" % " ".join(MENDER_STATE_FILES))
            connection.run("rm -f /tmp/dbus-monitor.log")
