#!/usr/bin/python
# Copyright 2017 Northern.tech AS
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

from fabric.api import *

import pytest
import subprocess
import os
import tempfile
import stat

# Make sure common is imported after fabric, because we override some functions.
from common import *


class TestRootfs:

    @staticmethod
    def verify_artifact_info_data(data, artifact_name):
        lines = data.split()
        assert(len(lines) == 1)
        line = lines[0]
        line = line.rstrip('\n\r')
        var = line.split('=', 2)
        assert(len(var) == 2)

        var = [entry.strip() for entry in var]

        assert(var[0] == "artifact_name")
        assert(var[1] == artifact_name)

    @staticmethod
    def verify_fstab(data):
        lines = data.split('\n')

        occurred = {}

        # No entry should occur twice.
        for line in lines:
            cols = line.split()
            if len(line) == 0 or line[0] == '#' or len(cols) < 2:
                continue
            assert occurred.get(cols[1]) is None, "%s appeared twice in fstab:\n%s" % (cols[1], data)
            occurred[cols[1]] = True

    @pytest.mark.only_with_image('ext4', 'ext3', 'ext2')
    @pytest.mark.min_mender_version("1.0.0")
    def test_expected_files_ext234(self, latest_rootfs, bitbake_variables, bitbake_path):
        """Test that artifact_info file is correctly embedded."""

        with make_tempdir() as tmpdir:
            try:
                subprocess.check_call(["debugfs", "-R", "dump -p /etc/mender/artifact_info artifact_info",
                                       latest_rootfs], cwd=tmpdir)
                with open(os.path.join(tmpdir, "artifact_info")) as fd:
                    data = fd.read()
                TestRootfs.verify_artifact_info_data(data, bitbake_variables["MENDER_ARTIFACT_NAME"])
                assert(os.stat(os.path.join(tmpdir, "artifact_info")).st_mode & 0777 == 0644)

                subprocess.check_call(["debugfs", "-R", "dump -p /etc/fstab fstab",
                                       latest_rootfs], cwd=tmpdir)
                with open(os.path.join(tmpdir, "fstab")) as fd:
                    data = fd.read()
                TestRootfs.verify_fstab(data)

            except:
                subprocess.call(["ls", "-l", "artifact_info"])
                print("Contents of artifact_info:")
                subprocess.call(["cat", "artifact_info"])
                raise

    @pytest.mark.only_with_image('ubifs')
    @pytest.mark.min_mender_version("1.2.0")
    def test_expected_files_ubifs(self, latest_ubifs, bitbake_variables, bitbake_path):
        """Test that artifact_info file is correctly embedded."""

        with make_tempdir() as tmpdir:
            # NOTE: ubireader_extract_files can keep permissions only if
            # running as root, which we won't do
            subprocess.check_call("ubireader_extract_files -o {outdir} {ubifs}".format(outdir=tmpdir,
                                                                                       ubifs=latest_ubifs),
                                  shell=True)

            path = os.path.join(tmpdir, "etc/mender/artifact_info")
            with open(path) as fd:
                data = fd.read()
            TestRootfs.verify_artifact_info_data(data, bitbake_variables["MENDER_ARTIFACT_NAME"])

            path = os.path.join(tmpdir, "etc/fstab")
            with open(path) as fd:
                data = fd.read()
            TestRootfs.verify_fstab(data)
