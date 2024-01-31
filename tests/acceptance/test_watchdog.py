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

import configparser
import io
import json
import os
import pytest
import redo
import tempfile
import time

from utils.common import put_no_sftp


@pytest.mark.cross_platform
@pytest.mark.usefixtures("setup_board", "bitbake_path")
@pytest.mark.min_mender_version("4.0.0")
class TestWatchdog:
    mender_updated_systemd_service_path = (
        "/data/etc/systemd/system/mender-updated.service.d/override.conf"
    )
    journalctl_cursor_file = "/tmp/journalctl-cursor"
    mender_conf_backup_file = "/data/etc/mender/mender.conf.bak"
    mender_conf_file = "/data/etc/mender/mender.conf"

    mender_updated_systemd_service_contents = """
[Service]
WatchdogSec=
WatchdogSec=10
            """

    def backup_conf_file(self, connection):
        connection.run(f"cp {self.mender_conf_file} {self.mender_conf_backup_file}")

    def restore_conf_file(self, connection):
        connection.run(f"cp {self.mender_conf_backup_file} {self.mender_conf_file}")

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

        try:
            self.backup_conf_file(connection)

            with tempfile.NamedTemporaryFile() as mender_conf:
                mender_conf.write(mender_conf_contents.encode())
                put_no_sftp(
                    mender_conf.name, connection, remote="/data/etc/mender/mender.conf",
                )

            with tempfile.NamedTemporaryFile() as mender_updated_systemd_service:
                mender_updated_systemd_service.write(
                    self.mender_updated_systemd_service_contents.encode()
                )
                mender_updated_systemd_service.flush()
                put_no_sftp(
                    mender_updated_systemd_service.name,
                    connection,
                    remote=self.mender_updated_systemd_service_path,
                )

            connection.run("systemctl daemon-reload")
            connection.run("systemctl restart mender-updated")

            def ensure_watchdog_killed_service():
                log_output = connection.run(
                    f"journalctl -u mender-updated --cursor-file={self.journalctl_cursor_file} --no-pager"
                ).stdout.strip()

                assert "Watchdog timeout" in log_output

            redo.retry(
                ensure_watchdog_killed_service, attempts=6, sleeptime=10,
            )

        finally:
            self.restore_conf_file(connection)
            connection.run(f"echo > {self.mender_updated_systemd_service_path}")
            connection.run("systemctl stop mender-updated")
            connection.run("systemctl daemon-reload")

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

        self.backup_conf_file(connection)

        mender_conf_contents = connection.run(
            "cat /etc/mender/mender.conf"
        ).stdout.strip()

        config = json.loads(mender_conf_contents)
        config["InventoryPollIntervalSeconds"] = 5
        config["UpdatePollIntervalSeconds"] = 5
        config["RetryPollIntervalSeconds"] = 2

        try:
            with tempfile.NamedTemporaryFile() as mender_conf:
                mender_conf.write(mender_conf_contents.encode())
                mender_conf.flush()
                put_no_sftp(
                    mender_conf.name, connection, remote=self.mender_conf_file,
                )

            with tempfile.NamedTemporaryFile() as mender_updated_systemd_service:
                mender_updated_systemd_service.write(
                    self.mender_updated_systemd_service_contents.encode()
                )
                mender_updated_systemd_service.flush()
                put_no_sftp(
                    mender_updated_systemd_service.name,
                    connection,
                    remote=self.mender_updated_systemd_service_path,
                )

            connection.run("systemctl daemon-reload")
            connection.run("systemctl restart mender-updated")

            # Set the journal cursor to the current position
            connection.run(
                f"journalctl -u mender-updated --cursor-file={self.journalctl_cursor_file} --no-pager"
            )

            time.sleep(60)

            # Get the log output from the sleep period
            log_output = connection.run(
                f"journalctl -u mender-updated --cursor-file={self.journalctl_cursor_file} --no-pager"
            ).stdout.strip()

            assert "Watchdog timeout" not in log_output
        finally:
            self.restore_conf_file(connection)
            connection.run(f"echo > {self.mender_updated_systemd_service_path}")
            connection.run("systemctl stop mender-updated")
            connection.run("systemctl daemon-reload")
