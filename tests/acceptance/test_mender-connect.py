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

import time
import os
from tempfile import NamedTemporaryFile

import pytest

from utils.common import (
    cleanup_mender_state,
    put_no_sftp,
    qemu_system_time,
    version_is_minimum,
)


@pytest.fixture(scope="class")
def with_mock_files(request, session_connection):
    mocks_dir = os.path.join(os.path.dirname(__file__), "mocks")
    put_no_sftp(
        os.path.join(mocks_dir, "mock_websocket_server.py"),
        session_connection,
        remote="/tmp/mock_websocket_server.py",
    )
    put_no_sftp(
        os.path.join(mocks_dir, "mock_dbus_server.py"),
        session_connection,
        remote="/tmp/mock_dbus_server.py",
    )

    def cleanup():
        session_connection.run(
            f"rm -f /tmp/mock_websocket_server.py /tmp/mock_dbus_server.py"
        )

    request.addfinalizer(cleanup)


class SshZombieProccess:
    """Starts a remote process in the background and captures its PID"""

    def __init__(self, connection, remote_command, unique_id) -> None:
        self._conn = connection
        self._pid_file = f"/tmp/{unique_id}.pid"
        self._sh_file = f"/tmp/{unique_id}.sh"

        wrapper = NamedTemporaryFile()
        wrapper.write(
            f"""
{remote_command} >/dev/null 2>&1 &
echo $! >{self._pid_file}
""".encode()
        )
        wrapper.flush()

        put_no_sftp(
            wrapper.name, connection, remote=self._sh_file,
        )
        connection.run(f"bash {self._sh_file}")
        result = connection.run(f"cat {self._pid_file}")

        self._pid = int(result.stdout)

    def _kill(self):
        return self._conn.run(f"kill {self._pid}", warn=True)

    def kill(self):
        """Kills the zombie process, expect to exist"""
        result = self._kill()
        assert result.exited == 0

    def terminate(self):
        """Kills the zombie process, do not error if it was already killed"""
        self._kill()
        self._conn.run(f"rm -f {self._sh_file} {self._pid_file}")


def wait_for_mock_dbus_server(connection):
    start = time.time()
    while time.time() < start + 60:
        result = connection.run(
            "dbus-send --print-reply --system "
            "--dest=io.mender.AuthenticationManager "
            "/io/mender/AuthenticationManager "
            "io.mender.Authentication1.FetchJwtToken ",
            warn=True,
        )

        if result.exited == 0 and "boolean true" in result.stdout:
            # The interface is ready
            break
        elif (
            "The name io.mender.AuthenticationManager was not provided by any .service files"
            in result.stderr
        ):
            # The interface is not ready, sleep and retry
            time.sleep(2)
        else:
            # Unexpected error, fail here
            pytest.fail("Unknown error '%s'" % result.stderr)
    else:
        pytest.fail(
            "Timed out waiting for io.mender.AuthenticationManager D-Bus interface"
        )


@pytest.fixture(scope="function")
def with_mock_servers(request, connection):
    proc_server_dbus = SshZombieProccess(
        connection, "python3 /tmp/mock_dbus_server.py", "mock_dbus_server"
    )
    proc_server_ws_one = SshZombieProccess(
        connection,
        f"python3 /tmp/mock_websocket_server.py 5000",
        f"mock_websocket_server_5000",
    )
    proc_server_ws_two = SshZombieProccess(
        connection,
        f"python3 /tmp/mock_websocket_server.py 6000",
        f"mock_websocket_server_6000",
    )

    def cleanup():
        proc_server_dbus.terminate()
        proc_server_ws_one.terminate()
        proc_server_ws_two.terminate()

    request.addfinalizer(cleanup)

    wait_for_mock_dbus_server(connection)

    return [proc_server_dbus, proc_server_ws_one, proc_server_ws_two]


def dbus_set_token_and_url(connection, token, server_url):
    connection.run(
        "dbus-send --print-reply --system "
        "--dest=io.mender.AuthenticationManager "
        "/io/mender/AuthenticationManager "
        "io.mender.Authentication1.MockSetJwtToken "
        f"string:'{token}' string:'{server_url}'"
    )


def dbus_set_token_and_url_and_emit_signal(connection, token, server_url):
    connection.run(
        "dbus-send --print-reply --system "
        "--dest=io.mender.AuthenticationManager "
        "/io/mender/AuthenticationManager "
        "io.mender.Authentication1.MockSetJwtTokenAndEmitSignal "
        f"string:'{token}' string:'{server_url}'"
    )


def wait_for_string_in_log(connection, since, timeout, search_string):
    output = ""
    while qemu_system_time(connection) < since + timeout:
        print("Searching for '%s' in mender-connect's journal:" % search_string)
        output = connection.run(
            "journalctl --unit mender-connect --since '%s'"
            % time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime(since)),
        ).stdout
        if search_string in output:
            break
        time.sleep(2)
    else:
        pytest.fail("Timed out waiting for '%s'" % search_string)

    return output


@pytest.mark.cross_platform
@pytest.mark.usefixtures("setup_board", "bitbake_path")
@pytest.mark.not_for_machine("vexpress-qemu-flash")
class TestMenderConnect:
    @pytest.mark.min_mender_version("2.5.0")
    def test_mender_connect_auth_changes(
        self, request, connection, with_mock_files, with_mock_servers,
    ):
        """Test that mender-connect can re-establish the connection on D-Bus signals"""

        try:
            dbus_set_token_and_url(connection, "token1", "http://localhost:5000")

            # start the mender-connect service
            startup_time = qemu_system_time(connection)
            connection.run(
                "systemctl --job-mode=ignore-dependencies start mender-connect"
            )

            # wait for first connect
            _ = wait_for_string_in_log(
                connection,
                startup_time,
                30,
                "Connection established with http://localhost:5000",
            )

            # 1. Change token
            signal_time = qemu_system_time(connection)
            dbus_set_token_and_url_and_emit_signal(
                connection, "token2", "http://localhost:5000"
            )
            _ = wait_for_string_in_log(
                connection,
                signal_time,
                30,
                "Connection established with http://localhost:5000",
            )

            # 2. Change url
            signal_time = qemu_system_time(connection)
            dbus_set_token_and_url_and_emit_signal(
                connection, "token2", "http://localhost:6000"
            )
            _ = wait_for_string_in_log(
                connection,
                signal_time,
                30,
                "Connection established with http://localhost:6000",
            )

            # 3. Change token and url
            signal_time = qemu_system_time(connection)
            dbus_set_token_and_url_and_emit_signal(
                connection, "token3", "http://localhost:5000"
            )
            _ = wait_for_string_in_log(
                connection,
                signal_time,
                30,
                "Connection established with http://localhost:5000",
            )

            # 4. Unauthorize and re-authorize
            signal_time = qemu_system_time(connection)
            dbus_set_token_and_url_and_emit_signal(connection, "", "")
            _ = wait_for_string_in_log(
                connection,
                signal_time,
                30,
                "dbusEventLoop terminated 0 sessions, 0 shells",
            )
            dbus_set_token_and_url_and_emit_signal(
                connection, "token4", "http://localhost:6000"
            )
            _ = wait_for_string_in_log(
                connection,
                signal_time,
                30,
                "Connection established with http://localhost:6000",
            )

        except:
            connection.run("journalctl --unit mender-connect --output cat")

        finally:
            connection.run(
                "systemctl --job-mode=ignore-dependencies stop mender-connect || true"
            )
            cleanup_mender_state(request, connection)

    @pytest.mark.min_mender_version("2.5.0")
    def test_mender_connect_reconnect(
        self, request, connection, with_mock_files, with_mock_servers, bitbake_variables
    ):
        """Test that mender-connect can re-establish the connection on remote errors"""

        try:
            dbus_set_token_and_url(connection, "badtoken", "http://localhost:12345")

            # start the mender-connect service
            startup_time = qemu_system_time(connection)
            connection.run(
                "systemctl --job-mode=ignore-dependencies start mender-connect"
            )

            # wait for error
            if version_is_minimum(bitbake_variables, "mender-connect", "2.3.0"):
                error_message = "connection manager failed to connect"
            else:
                error_message = "eventLoop: error reconnecting: failed to connect after max number of retries"
            _ = wait_for_string_in_log(connection, startup_time, 300, error_message)

            # Set correct parameters
            signal_time = qemu_system_time(connection)
            dbus_set_token_and_url_and_emit_signal(
                connection, "goodtoken", "http://localhost:5000"
            )
            _ = wait_for_string_in_log(
                connection,
                signal_time,
                300,
                "Connection established with http://localhost:5000",
            )

            dbus_set_token_and_url(connection, "", "")
            kill_time = qemu_system_time(connection)
            # kill the server and wait for error
            with_mock_servers[1].kill()
            _ = wait_for_string_in_log(
                connection, kill_time, 300, "error reconnecting:",
            )

            # Signal the other server
            signal_time = qemu_system_time(connection)
            dbus_set_token_and_url_and_emit_signal(
                connection, "goodtoken", "http://localhost:6000"
            )
            _ = wait_for_string_in_log(
                connection,
                signal_time,
                300,
                "Connection established with http://localhost:6000",
            )

        finally:
            connection.run(
                "systemctl --job-mode=ignore-dependencies stop mender-connect || true"
            )
            cleanup_mender_state(request, connection)
