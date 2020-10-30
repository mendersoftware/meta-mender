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

import time

import pytest


class TestOsIntegration:
    @pytest.mark.min_mender_version("2.2.1")
    def test_syslogger(self, setup_board, connection):
        """Test that we log to syslog, and that we don't if we specify --no-syslog."""

        def is_mender_in_syslog_messages():
            now = time.time()
            while time.time() < now + 120:
                # Busybox syslog puts messages in /var/log/messages, whereas
                # syslogd puts them in /var/log/syslog.
                ret = connection.run(
                    r"egrep 'mender\[[0-9]+\]:' /var/log/messages /var/log/syslog",
                    warn=True,
                )
                if ret.stdout.strip() != "":
                    return True
                time.sleep(5)
            return False

        connection.run("rm -f /var/log/messages /var/log/syslog")
        connection.run("systemctl restart syslog")
        ret = connection.run("mender daemon >& /dev/null & echo $!")
        pid = ret.stdout.strip()
        try:
            assert (
                is_mender_in_syslog_messages()
            ), "Could not find mender output in syslog."
        finally:
            connection.run("kill -9 %s" % pid)

        # Now try with --no-syslog flag
        connection.run("rm -f /var/log/messages /var/log/syslog")
        connection.run("systemctl restart syslog")
        ret = connection.run("mender --no-syslog daemon >& /dev/null & echo $!")
        pid = ret.stdout.strip()
        try:
            assert not is_mender_in_syslog_messages(), "Found mender output in syslog."
        finally:
            connection.run("kill -9 %s" % pid)
