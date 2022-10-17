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
