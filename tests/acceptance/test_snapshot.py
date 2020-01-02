#!/usr/bin/python
# Copyright 2019 Northern.tech AS
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

import pytest

from common import *


@pytest.mark.usefixtures("setup_board", "bitbake_path")
class TestSnapshot:
    @pytest.mark.min_mender_version("2.2.0")
    @pytest.mark.only_with_image("uefiimg", "sdimg", "biosimg", "gptimg")
    def test_basic_snapshot(self, bitbake_variables, connection):
        try:
            (active, passive) = determine_active_passive_part(
                bitbake_variables, connection
            )

            # Wipe the inactive partition first.
            connection.run("dd if=/dev/zero of=%s bs=1M count=100" % passive)

            # Dump what we currently have to the inactive partition.
            connection.run("mender snapshot dump > %s" % passive)

            # Make sure this looks like a sane filesystem.
            connection.run("fsck.ext4 -p %s" % passive)

            # And that it can be mounted with actual content.
            connection.run("mount %s /mnt" % passive)
            connection.run("test -f /mnt/etc/passwd")

        finally:
            connection.run("umount /mnt || true")
