#!/usr/bin/python
# Copyright 2023 Northern.tech AS
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

from mock_server import setup_mock_server

from utils.common import (
    cleanup_mender_state,
    version_is_minimum,
)


@pytest.mark.cross_platform
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
    def test_dbus_non_root_access(
        self,
        request,
        bitbake_variables,
        connection,
        mender_auth_binary,
        mender_auth_service,
    ):
        """Test that only root user can access Mender DBus API."""

        # This is the command that is expected to fail for non-root user
        dbus_send_command = "dbus-send --system --dest=io.mender.AuthenticationManager --print-reply /io/mender/AuthenticationManager io.mender.Authentication1.GetJwtToken"

        try:
            connection.run(f"{mender_auth_binary} bootstrap", warn=True)
            connection.run(f"systemctl start {mender_auth_service}")

            # Wait one state machine cycle for the D-Bus API to be available
            for _ in range(60):
                result = connection.run(f"journalctl --unit {mender_auth_service}")
                if (
                    "Authorize failed:" in result.stdout
                    or "Failed to authorize" in result.stdout
                    or "The authentication daemon is now ready to accept incoming authentication request"
                    in result.stdout
                ):
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
            connection.run(f"systemctl stop {mender_auth_service}")
            cleanup_mender_state(request, connection)

    @pytest.mark.min_mender_version("2.5.0")
    def test_dbus_fetch_jwt_token(
        self,
        request,
        bitbake_variables,
        connection,
        setup_mock_server,
        mender_auth_binary,
        mender_auth_service,
    ):
        """Test that the JWT token can be fetched using D-Bus."""

        # bootstrap the auth service
        result = connection.run(f"{mender_auth_binary} bootstrap --forcebootstrap")
        assert result.exited == 0

        try:
            # start monitoring the D-Bus
            p = connection.run(
                "dbus-monitor --system \"type='signal',interface='io.mender.Authentication1'\" > /tmp/dbus-monitor.log",
                popen=True,
            )

            # get the JWT token via D-Bus
            try:
                # start the mender-auth service
                result = connection.run(f"systemctl start {mender_auth_service}")
                assert result.exited == 0

                # fetch the JWT token
                fetched = False
                for i in range(60):
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
                for i in range(60):
                    output = connection.run("cat /tmp/dbus-monitor.log").stdout.strip()
                    if (
                        "path=/io/mender/AuthenticationManager; interface=io.mender.Authentication1; member=JwtTokenStateChange"
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
                assert result.exited == 0

                output = result.stdout.strip()
                assert f'string "{self.JWT_TOKEN}' in output
                if version_is_minimum(bitbake_variables, "mender-client", "3.3.1"):
                    assert 'string "http://127.0.0.1:' in output
                else:
                    assert 'string "http://localhost:' in output

            finally:
                p.terminate()
                connection.run(f"systemctl stop {mender_auth_service}")
                connection.run("rm -f /tmp/dbus-monitor.log")

        finally:
            cleanup_mender_state(request, connection)
