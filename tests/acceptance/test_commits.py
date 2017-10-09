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

import pytest
import re
import subprocess

@pytest.mark.min_mender_version("1.0.0")
class TestCommits:
    def test_commits(self):
        # First find which range to check. Include HEAD and exclude all known
        # upstream branches.
        git_branch = subprocess.check_output(["git", "branch", "-r"])
        all_branches = [line.split()[0] for line in git_branch.strip().split('\n')]

        # Exclude all non-pull requests.
        commit_range = ["HEAD", "--not"]
        for branch in all_branches:
            # Include all non-origin branches.
            if not branch.startswith("origin/"):
                continue
            # Include branches that have slashes after "origin/" (pull requests).
            if re.match("^origin/.*/", branch):
                continue
            # Include branches that end with "patch-1" style text.
            if re.match("^origin/.*patch-[0-9]+$", branch):
                continue
            # Exclude if no matches above.
            commit_range.append(branch)

        try:
            output = subprocess.check_output(["3rdparty/mendertesting/check_commits.sh"] + commit_range,
                                             stderr=subprocess.STDOUT)
            # Print output, useful to make sure correct commit range is checked.
            print(output)
        except subprocess.CalledProcessError as e:
            pytest.fail(e.output)
