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

import os
import pytest
import sys
import traceback

sys.path.append(os.path.join(os.path.dirname(__file__), "image-tests", "tests"))

# Load the parser option flags from the shared module
pytest_plugins = "utils.parseropts.parseropts"

from utils.fixtures import *


def pytest_collection_modifyitems(session, config, items):
    """Ugly hack to make sure the bootstrap Artifact test is always run first

    This is needed, because the bootstrap Artifact test is the only test which
    does not rely on the client running in qemu under the full session scope.

    """

    test_index = None

    # Add the bootstrap Artifact test first
    for index, test in enumerate(items):
        if test.name == "test_bootstrap_artifact_install":
            test_index = index
            break
    if test_index:
        items.insert(0, items.pop(test_index))


def pytest_sessionfinish(session, exitstatus):
    """
    At the end of the test run, collect journal logs from the machine under test
    and copy them over to CI WORKSPACE /tmp so they can be collected as artifacts.
    """
    log_path = "/tmp/journalctl.log"
    try:
        connection.run(f"journalctl --no-pager > {log_path}")
        get_no_sftp(log_path, connection, local=log_path)
    except Exception:
        # it might fail for some board types but that's okay the collection is best effort
        print("\n\n!!!! Failed to retrieve journal logs from the device. This is non-fatal.")
        traceback.print_exc()
        print("!!!! End of non-fatal error.\n")
