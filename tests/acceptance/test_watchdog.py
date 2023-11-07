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
#

import json
import os
import pytest
import redo
import tempfile
import time

# from tests.acceptance.image-tests.tests.utils.common.common import put_no_sftp


@pytest.mark.cross_platform
@pytest.mark.usefixtures("setup_board", "bitbake_path")
@pytest.mark.min_mender_version("4.0.0")
class TestWatchdog:
    mender_updated_systemd_service_path = "/lib/systemd/system/mender-updated.service"

    def test_watchdog_kill(self, connection):
        """Test that the watchdog implemented by systemd works, and restarts our
        service if it is not kicked within the given interval

        This sets the

        * InventoryPollIntervalSeconds
        * UpdatePollIntervalSeconds
        * RetryPollIntervalSeconds

        to `60` seconds, and the watchdog interval to `10` seconds, which should
        trigger the watchdog, and we can see in the systemd log how many times it
        has been restarted.

        """

        connection.run("systemctl stop mender-updated")

        mender_conf_contents = connection.run(
            "cat /etc/mender/mender.conf"
        ).stdout.strip()

        config = json.loads(mender_conf_contents)
        config["InventoryPollIntervalSeconds"] = 60
        config["UpdatePollIntervalSeconds"] = 60
        config["RetryPollIntervalSeconds"] = 60

        with tempfile.NamedTemporaryFile() as mender_conf:
            mender_conf.write(mender_conf_contents)
            put_no_sftp(
                mender_conf.name,
                connection,
                remote="/etc/mender/mender.conf",
            )

        mender_updated_systemd_service_contents = connection.run(
            "cat " + mender_updated_systemd_service_path
        ).stdout.strip()
        mender_updated_systemd_service_contents.replace(
            "WatchdogSec=86400", "WatchdogSec=10"
        )

        with tempfile.NamedTemporaryFile() as mender_updated_systemd_service:
            fd.write(mender_updated_systemd_service_contents)
            put_no_sftp(
                mender_updated_systemd_service.name,
                connection,
                remote=mender_updated_systemd_service_path,
            )

        connection.run("systemctl daemon-reload")
        connection.run("systemctl restart mender-updated")

        def ensure_watchdog_killed_service():
            log_output = connection.run(
                "journalctl -u mender-updated | cat"
            ).stdout.strip()
            assert "Watchdog timeout" in log_output

        redo.retry(
            ensure_watchdog_killed_service,
            attempts=6,
            sleeptime=10,
        )

        assert "Watchdog timeout" in log_output

    def test_watchdog_kick(self, connection):
        """Test that the watchdog implemented by systemd works, and _does not_
        restart our service if it _is kicked_ within the given interval

        This sets the

        * InventoryPollIntervalSeconds
        * UpdatePollIntervalSeconds
        * RetryPollIntervalSeconds

        to `5` seconds, and the watchdog interval to `60` seconds, which should
        then _not_ trigger the watchdog, and we can see in the systemd log that
        it has _not_ been restarted.

        """
        connection.run("systemctl stop mender-updated")

        mender_conf_contents = connection.run(
            "cat /etc/mender/mender.conf"
        ).stdout.strip()

        config = json.loads(mender_conf_contents)
        config["InventoryPollIntervalSeconds"] = 5
        config["UpdatePollIntervalSeconds"] = 5
        config["RetryPollIntervalSeconds"] = 2

        with tempfile.NamedTemporaryFile() as mender_conf:
            mender_conf.write(mender_conf_contents)
            put_no_sftp(
                mender_conf.name,
                connection,
                remote="/etc/mender/mender.conf",
            )

        mender_updated_systemd_service_contents = connection.run(
            "cat " + mender_updated_systemd_service_path
        ).stdout.strip()
        # TODO - Maybe we should do a regexp replace instead
        mender_updated_systemd_service_contents.replace(
            "WatchdogSec=86400", "WatchdogSec=60"
        )

        with tempfile.NamedTemporaryFile() as mender_updated_systemd_service:
            fd.write(mender_updated_systemd_service_contents)
            put_no_sftp(
                mender_updated_systemd_service.name,
                connection,
                remote=mender_updated_systemd_service_path,
            )

        connection.run("systemctl daemon-reload")
        connection.run("systemctl restart mender-updated")

        time.sleep(120)

        log_output = connection.run("journalctl -u mender-updated | cat").stdout.strip()

        assert "Watchdog timeout" not in log_output
