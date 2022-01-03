#!/usr/bin/python
# Copyright 2022 Northern.tech AS
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

import json
import os
import pytest
import subprocess
import sys
import tempfile
import time

from multiprocessing import Process

from mock_server import (
    cleanup_deployment_response,
    prepare_deployment_response,
    setup_mock_server,
    EXPIRATION_TIME,
    BOOT_EXPIRATION_TIME,
)
from utils.common import put_no_sftp, cleanup_mender_state

# Map UIDs. Randomly chosen, but used throughout for consistency.
MUID = "3702f9f0-b318-11eb-a7b6-c7aece07181e"
MUID2 = "3702f9f0-b318-11eb-a7b6-c7aece07181f"

BETWEEN_EXPIRATIONS = max(EXPIRATION_TIME, BOOT_EXPIRATION_TIME) - 5
FAIL_TIME = EXPIRATION_TIME + BOOT_EXPIRATION_TIME


def start_and_ready_mender_client(connection, second_connection):
    def dbus_monitor():
        second_connection.run(
            "dbus-monitor --system \"type='signal',interface='io.mender.Authentication1'\" > /tmp/dbus-monitor.log"
        )

    p = Process(target=dbus_monitor, daemon=True)
    p.start()
    time.sleep(0.5)
    try:
        connection.run("systemctl start mender-client")

        timeout = 120
        now = time.time()
        while time.time() - now < timeout:
            time.sleep(1)
            output = connection.run("cat /tmp/dbus-monitor.log")
            if "JwtTokenStateChange" in output.stdout.strip():
                break
        else:
            assert (
                False
            ), "Mender client did not broadcast JwtTokenStateChange as expected."
    finally:
        p.terminate()
        connection.run("rm -f cat /tmp/dbus-monitor.log")


def set_update_control_map(connection, m, warn=False):
    output = connection.run(
        "dbus-send --system --dest=io.mender.UpdateManager --print-reply /io/mender/UpdateManager io.mender.Update1.SetUpdateControlMap string:'%s'"
        % json.dumps(m),
        warn=warn,
    )
    assert "int32 %d" % (EXPIRATION_TIME / 2) in output.stdout


def clear_update_control_maps(connection):
    connection.run(
        (
            "for uid in %s %s; do "
            + "    for priority in `seq -10 10`; do "
            + """        dbus-send --system --dest=io.mender.UpdateManager --print-reply /io/mender/UpdateManager io.mender.Update1.SetUpdateControlMap string:'{"id":"'$uid'","priority":'$priority'}';"""
            + "    done;"
            + "done"
        )
        % (MUID, MUID2),
        warn=True,
    )


# Deliberately not using a constant for deployment_id. If you want something
# known, you have to pass it in yourself.
def make_and_deploy_artifact(
    connection,
    device_type,
    deployment_id="7e49d892-d5a0-11eb-a6ff-23a7bacac256",
    update_control_map=None,
):
    with tempfile.NamedTemporaryFile(suffix=".mender") as artifact_file:
        artifact_name = os.path.basename(artifact_file.name)[:-7]

        subprocess.check_call(
            [
                "mender-artifact",
                "write",
                "module-image",
                "-t",
                device_type,
                "-T",
                "logger-update-module",
                "-n",
                artifact_name,
                "-o",
                artifact_file.name,
            ]
        )
        prepare_deployment_response(
            connection,
            artifact_file.name,
            device_type,
            artifact_name=artifact_name,
            deployment_id=deployment_id,
            update_control_map=update_control_map,
        )


def wait_for_state(connection, state_to_wait_for):
    log = []
    attempts = 10
    while attempts > 0:
        output = connection.run(
            "cat /data/logger-update-module.log 2>/dev/null || true"
        ).stdout.strip()
        log = [line.split()[1] for line in output.split("\n") if len(line) > 0]

        if state_to_wait_for in log:
            break

        time.sleep(6)

        attempts -= 1
    else:
        pytest.fail(f"Could not find {state_to_wait_for} in log")
    return log


class TestUpdateControl:
    test_update_control_maps_cases = [
        {"name": "Empty map", "case": {"maps": [{"id": MUID,}], "success": True,},},
        {
            "name": "Fail in ArtifactInstall_Enter",
            "case": {
                "maps": [
                    {
                        "id": MUID,
                        "states": {"ArtifactInstall_Enter": {"action": "fail",},},
                    }
                ],
                "success": False,
                "last_successful_state": "Download",
            },
        },
        {
            "name": "Fail in ArtifactReboot_Enter",
            "case": {
                "maps": [
                    {
                        "id": MUID,
                        "states": {"ArtifactReboot_Enter": {"action": "fail",},},
                    }
                ],
                "success": False,
                "last_successful_state": "ArtifactInstall",
            },
        },
        {
            "name": "Fail in ArtifactCommit_Enter",
            "case": {
                "maps": [
                    {
                        "id": MUID,
                        "states": {"ArtifactCommit_Enter": {"action": "fail",},},
                    }
                ],
                "success": False,
                "last_successful_state": "ArtifactVerifyReboot",
            },
        },
        {
            "name": "Pause in ArtifactInstall_Enter",
            "case": {
                "maps": [
                    {
                        "id": MUID,
                        "states": {"ArtifactInstall_Enter": {"action": "pause",},},
                    }
                ],
                "success": True,
                "state_before_pause": "Download",
                "continue_map": {
                    "id": MUID,
                    "states": {"ArtifactInstall_Enter": {"action": "continue",},},
                },
                "last_successful_state": "ArtifactCommit",
            },
        },
        {
            "name": "Pause in ArtifactReboot_Enter",
            "case": {
                "maps": [
                    {
                        "id": MUID,
                        "states": {"ArtifactReboot_Enter": {"action": "pause",},},
                    }
                ],
                "success": True,
                "state_before_pause": "ArtifactInstall",
                "continue_map": {
                    "id": MUID,
                    "states": {"ArtifactReboot_Enter": {"action": "continue",},},
                },
                "last_successful_state": "ArtifactCommit",
            },
        },
        {
            "name": "Pause in ArtifactCommit_Enter",
            "case": {
                "maps": [
                    {
                        "id": MUID,
                        "states": {"ArtifactCommit_Enter": {"action": "pause",},},
                    }
                ],
                "success": True,
                "state_before_pause": "ArtifactVerifyReboot",
                "continue_map": {
                    "id": MUID,
                    "states": {"ArtifactCommit_Enter": {"action": "continue",},},
                },
                "last_successful_state": "ArtifactCommit",
            },
        },
        {
            "name": "Expire in ArtifactInstall_Enter",
            "case": {
                "maps": [
                    {
                        "id": MUID,
                        "states": {
                            "ArtifactInstall_Enter": {
                                "action": "pause",
                                "on_map_expire": "continue",
                            },
                        },
                    }
                ],
                "take_at_least": EXPIRATION_TIME,
                "success": True,
                "last_successful_state": "ArtifactCommit",
            },
        },
        {
            "name": "Reboot and expire in ArtifactInstall_Enter",
            "case": {
                "maps": [
                    {
                        "id": MUID,
                        "states": {
                            "ArtifactInstall_Enter": {
                                "action": "pause",
                                "on_map_expire": "continue",
                            },
                        },
                    }
                ],
                "restart_client": True,
                "fail_after": BETWEEN_EXPIRATIONS,
                "success": True,
                "last_successful_state": "ArtifactCommit",
            },
        },
        {
            "name": "Continue, then fail in ArtifactInstall_Enter",
            "case": {
                "maps": [
                    {
                        "id": MUID,
                        "states": {
                            "ArtifactInstall_Enter": {
                                "action": "continue",
                                "on_action_executed": "fail",
                            },
                        },
                    }
                ],
                "second_deployment": True,
                "success": False,
                "last_successful_state": "Download",
            },
        },
        {
            "name": "continue with higher priority",
            "case": {
                "maps": [
                    {
                        "id": MUID,
                        "states": {"ArtifactInstall_Enter": {"action": "fail",},},
                    },
                    {
                        "id": MUID2,
                        "states": {"ArtifactInstall_Enter": {"action": "continue",},},
                        "priority": 1,
                    },
                ],
                # "continue" has lowest precedence, even if the priority is
                # higher.
                "success": False,
                "last_successful_state": "Download",
            },
        },
        {
            "name": "force_continue with higher priority",
            "case": {
                "maps": [
                    {
                        "id": MUID,
                        "states": {"ArtifactInstall_Enter": {"action": "pause",},},
                    },
                    {
                        "id": MUID2,
                        "states": {
                            "ArtifactInstall_Enter": {"action": "force_continue",},
                        },
                        "priority": 1,
                    },
                ],
                "success": True,
                "last_successful_state": "ArtifactCommit",
            },
        },
        {
            "name": "force_continue with lower priority",
            "case": {
                "maps": [
                    {
                        "id": MUID,
                        "states": {"ArtifactCommit_Enter": {"action": "fail",},},
                    },
                    {
                        "id": MUID2,
                        "states": {
                            "ArtifactCommit_Enter": {"action": "force_continue",},
                        },
                        "priority": -1,
                    },
                ],
                "success": False,
                "last_successful_state": "ArtifactVerifyReboot",
            },
        },
        {
            "name": "Expired and purged map",
            "case": {
                "maps": [
                    {
                        "id": MUID,
                        "states": {
                            # Install a map which succeeds, but sets up for failure afterwards.
                            "ArtifactInstall_Enter": {
                                "action": "continue",
                                "on_action_executed": "fail",
                            },
                            # Then expire the map.
                            "ArtifactCommit_Enter": {
                                "action": "pause",
                                "on_map_expire": "continue",
                            },
                        },
                    }
                ],
                # The second deployment should succeed despite the "fail" above,
                # because expired maps are purged between deployments.
                "second_deployment": True,
                "take_at_least": EXPIRATION_TIME,
                "success": True,
                "last_successful_state": "ArtifactCommit",
            },
        },
    ]

    @pytest.mark.min_mender_version("2.7.0")
    @pytest.mark.parametrize(
        "case_name,case",
        [(case["name"], case["case"]) for case in test_update_control_maps_cases],
    )
    def test_update_control_maps(
        self,
        case_name,
        case,
        setup_board,
        connection,
        second_connection,
        setup_mock_server,
        bitbake_variables,
        bitbake_path,
    ):
        try:
            start_and_ready_mender_client(connection, second_connection)

            for m in case["maps"]:
                set_update_control_map(connection, m)

            if case.get("restart_client"):
                # Restart client after map insertion in order to trigger the
                # boot expiration mechanism.
                connection.run("systemctl restart mender-client")

            now = time.time()

            make_and_deploy_artifact(
                connection, bitbake_variables["MENDER_DEVICE_TYPE"]
            )

            connection.run("mender check-update")

            log = []
            pause_state_observed = 0
            continue_map_inserted = False
            second_deployment_done = False
            PAUSE_STATE_OBSERVE_COUNT = 2
            while time.time() - now <= case.get("fail_after", FAIL_TIME):
                output = connection.run(
                    "cat /data/logger-update-module.log 2>/dev/null || true"
                ).stdout.strip()
                log = [line.split()[1] for line in output.split("\n") if len(line) > 0]

                # Check for the state before the pause state, and verify it's
                # the last state (meaning the client is currently waiting before
                # the next state).
                if (
                    not continue_map_inserted
                    and case.get("state_before_pause")
                    and len(log) > 0
                    and log[-1] == case["state_before_pause"]
                ):
                    pause_state_observed += 1
                    # Verify that it stays in paused mode.
                    if pause_state_observed >= PAUSE_STATE_OBSERVE_COUNT:
                        # Now insert the map to unblock the pause.
                        set_update_control_map(connection, case["continue_map"])
                        continue_map_inserted = True

                # Cleanup is the last state of a deployment
                if "Cleanup" in log:
                    if case.get("second_deployment") and not second_deployment_done:
                        # When making two deployments, we assume the first one
                        # is successful.
                        assert "ArtifactFailure" not in log

                        connection.run("rm -f /data/logger-update-module.log")
                        make_and_deploy_artifact(
                            connection, bitbake_variables["MENDER_DEVICE_TYPE"]
                        )
                        connection.run("mender check-update")
                        second_deployment_done = True
                    else:
                        break

                time.sleep(5)
            else:
                pytest.fail("Could not find Cleanup in log, did deployment not finish?")

            if case.get("take_at_least"):
                assert (
                    time.time() - now >= case["take_at_least"]
                ), "Deployment finished before it was supposed to!"

            if case["success"]:
                assert "ArtifactFailure" not in log
            else:
                assert "ArtifactFailure" in log
                assert (
                    log[log.index("ArtifactFailure") - 1]
                    == case["last_successful_state"]
                )

            if case.get("state_before_pause"):
                assert (
                    pause_state_observed >= PAUSE_STATE_OBSERVE_COUNT
                ), "Looks like the client did not pause!"

        except:
            connection.run("journalctl --unit mender-client | cat")
            connection.run("journalctl --unit mender-mock-server | cat")
            raise

        finally:
            cleanup_deployment_response(connection)
            # Reset update control maps.
            clear_update_control_maps(connection)
            connection.run("systemctl stop mender-client")
            cleanup_mender_state(connection)
            connection.run("rm -f /data/logger-update-module.log")

    @pytest.mark.min_mender_version("2.7.0")
    def test_invalid_update_control_map(
        self, setup_board, connection, second_connection, setup_mock_server
    ):
        try:
            start_and_ready_mender_client(connection, second_connection)

            status = connection.run(
                """dbus-send --system --dest=io.mender.UpdateManager --print-reply /io/mender/UpdateManager io.mender.Update1.SetUpdateControlMap string:'{"not-a":"valid-map"}'""",
                warn=True,
            )
            assert status.return_code != 0
        finally:
            connection.run("systemctl stop mender-client")
            cleanup_mender_state(connection)

    test_update_control_maps_cleanup_cases = [
        {
            "name": "Cleanup after success",
            "case": {
                "pause_map": {
                    "priority": 0,
                    "states": {"ArtifactCommit_Enter": {"action": "pause",},},
                },
                "pause_state": "ArtifactVerifyReboot",
                "continue_map": {
                    "id": MUID,
                    "priority": 10,
                    "states": {
                        "ArtifactInstall_Enter": {"action": "fail",},
                        "ArtifactCommit_Enter": {"action": "force_continue",},
                    },
                },
                "expect_failure": False,
            },
        },
        {
            "name": "Cleanup after failure",
            "case": {
                "pause_map": {
                    "priority": 0,
                    "states": {"ArtifactCommit_Enter": {"action": "pause",},},
                },
                "pause_state": "ArtifactVerifyReboot",
                "continue_map": {
                    "id": MUID,
                    "priority": 10,
                    "states": {
                        "ArtifactInstall_Enter": {"action": "fail",},
                        "ArtifactCommit_Enter": {"action": "fail",},
                    },
                },
                "expect_failure": True,
            },
        },
    ]

    @pytest.mark.min_mender_version("2.7.0")
    @pytest.mark.parametrize(
        "case_name,case",
        [
            (case["name"], case["case"])
            for case in test_update_control_maps_cleanup_cases
        ],
    )
    def test_update_control_map_cleanup(
        self,
        case_name,
        case,
        setup_board,
        connection,
        second_connection,
        setup_mock_server,
        bitbake_variables,
        bitbake_path,
    ):
        try:
            start_and_ready_mender_client(connection, second_connection)

            # First deployment sends the "pause" control map via Server API with the
            # update; then once the client is paused, the map is overridden via DBus API.
            # The deployment shall succeed or fail dependending of the test case
            make_and_deploy_artifact(
                connection,
                bitbake_variables["MENDER_DEVICE_TYPE"],
                deployment_id=MUID,
                update_control_map=case["pause_map"],
            )
            connection.run("mender check-update")
            wait_for_state(connection, case["pause_state"])
            set_update_control_map(connection, case["continue_map"])
            log = wait_for_state(connection, "Cleanup")
            if case["expect_failure"]:
                assert "ArtifactFailure" in log
            else:
                assert "ArtifactFailure" not in log

            # Second deployment shall succeed
            connection.run("rm -f /data/logger-update-module.log")
            cleanup_deployment_response(connection)
            make_and_deploy_artifact(
                connection,
                bitbake_variables["MENDER_DEVICE_TYPE"],
                deployment_id=MUID2,
                update_control_map=None,
            )
            connection.run("mender check-update")
            log = wait_for_state(connection, "Cleanup")
            assert "ArtifactFailure" not in log

        except:
            connection.run("journalctl --unit mender-client | cat")
            connection.run("journalctl --unit mender-mock-server | cat")
            raise

        finally:
            cleanup_deployment_response(connection)
            clear_update_control_maps(connection)
            connection.run("systemctl stop mender-client")
            cleanup_mender_state(connection)
            connection.run("rm -f /data/logger-update-module.log")

    @pytest.mark.min_mender_version("2.7.0")
    def test_many_state_transitions_with_update_control(
        self,
        setup_board,
        connection,
        second_connection,
        setup_mock_server,
        bitbake_variables,
        bitbake_path,
    ):
        """Test whether we can make many state transitions with update control without
        triggering the "too many state transitions" error."""

        try:
            start_and_ready_mender_client(connection, second_connection)

            ucm = (
                """{
    "ID": "%s",
    "states": {
        "ArtifactInstall_Enter": {
            "action": "pause"
        }
    }
}"""
                % MUID
            )

            with tempfile.TemporaryDirectory() as tmpdir:
                script = os.path.join(tmpdir, "map-insert.sh")
                with open(script, "w") as fd:
                    fd.write(
                        """#!/bin/sh
while sleep 0.2; do
    dbus-send --system --dest=io.mender.UpdateManager --print-reply /io/mender/UpdateManager io.mender.Update1.SetUpdateControlMap string:'%s'
done
"""
                        % ucm
                    )
                put_no_sftp(script, connection, remote="/data/map-insert.sh")

            # Constantly reinsert map over and over in the background, to force
            # state transitions.
            connection.run("systemd-run sh /data/map-insert.sh")

            now = time.time()

            make_and_deploy_artifact(
                connection, bitbake_variables["MENDER_DEVICE_TYPE"]
            )

            connection.run("mender check-update")

            timeout = now + 300
            # Wait until we have received 100 state transitions, which is way
            # more than would cause a failure.
            while time.time() < timeout:
                output = connection.run(
                    "journalctl --unit mender-client --since '%s' | grep 'State transition: mender-update-control '"
                    % time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime(now)),
                    warn=True,
                ).stdout
                if len(output.split("\n")) >= 100:
                    break
            else:
                pytest.fail(
                    "Timed out without reaching the required number of state transitions."
                )

            # Just double check that we are indeed paused, as we expect.
            log = wait_for_state(connection, "Download")
            assert "Cleanup" not in log

            # Force it to continue.
            set_update_control_map(
                connection,
                {
                    "ID": MUID2,
                    "priority": 10,
                    "states": {"ArtifactInstall_Enter": {"action": "force_continue"}},
                },
            )

            # Rest of deployment should finish successfully.
            log = wait_for_state(connection, "Cleanup")
            assert "ArtifactFailure" not in log

        except:
            connection.run("journalctl --unit mender-client | cat")
            connection.run("journalctl --unit mender-mock-server | cat")
            raise

        finally:
            connection.run("pkill -f map-insert.sh", warn=True)
            cleanup_deployment_response(connection)
            # Reset update control maps.
            clear_update_control_maps(connection)
            connection.run("systemctl stop mender-client")
            cleanup_mender_state(connection)
            connection.run("rm -f /data/logger-update-module.log")
