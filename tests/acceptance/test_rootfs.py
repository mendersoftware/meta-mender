#!/usr/bin/python
# Copyright 2016 Mender Software AS
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
import re

# Make sure common is imported after fabric, because we override some functions.
from common import *

e2cp_installed = subprocess.call(["which", "e2cp"]) == 0

class TestRootfs:
    @pytest.mark.skipif(not e2cp_installed, reason="Needs e2tools to be installed")
    def test_artifact_info(self, latest_rootfs, bitbake_variables):
        """Test that artifact_info file is correctly embedded."""

        try:
            subprocess.check_call(["e2cp", "-p", "%s:/etc/mender/artifact_info" % latest_rootfs, "."])
            fd = open("artifact_info")
            lines = fd.readlines()
            assert(len(lines) == 1)
            line = lines[0]
            line = line.rstrip('\n\r')
            var = line.split('=', 2)
            assert(len(var) == 2)

            var = [entry.strip() for entry in var]

            assert(var[0] == "artifact_name")
            assert(var[1] == bitbake_variables["MENDER_ARTIFACT_NAME"])

            fd.close()

            assert(os.stat("artifact_info").st_mode & 0777 == 0644)

        except:
            subprocess.call(["ls", "-l", "artifact_info"])
            print("Contents of artifact_info:")
            subprocess.call(["cat", "artifact_info"])
            raise

        finally:
            try:
                os.remove("artifact_info")
            except:
                pass
