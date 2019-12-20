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

import os
import subprocess
from fixtures import *

from common import configuration


def pytest_addoption(parser):
    parser.addoption(
        "--host",
        action="store",
        default="localhost:8822",
        help="""IP to connect to, with optional port. Defaults
                     to localhost:8822, which is what the QEMU script sets up.""",
    )
    parser.addoption(
        "--user",
        action="store",
        default="root",
        help="user to log into remote hosts with (default is root)",
    )
    parser.addoption(
        "--http-server",
        action="store",
        default="10.0.2.2:8000",
        help="Remote HTTP server containing update image",
    )
    parser.addoption(
        "--sdimg-location",
        action="store",
        default=os.getcwd(),
        help="location to the sdimg you want to install on the bbb",
    )
    parser.addoption(
        "--bitbake-image",
        action="store",
        default="core-image-full-cmdline",
        help="image to build during the tests",
    )
    parser.addoption(
        "--no-tmp-build-dir",
        action="store_true",
        default=False,
        help="Do not use a temporary build directory. Faster, but may mess with your build directory.",
    )
    parser.addoption(
        "--no-pull",
        action="store_true",
        default=False,
        help="Do not pull submodules. Handy if debugging something locally.",
    )
    parser.addoption(
        "--board-type",
        action="store",
        default="qemu",
        help="type of board to use in testing, supported types: qemu, bbb, colibri-imx7",
    )
    parser.addoption(
        "--use-s3",
        action="store_true",
        default=False,
        help="use S3 for transferring images under test to target boards",
    )
    parser.addoption(
        "--s3-address",
        action="store",
        default="s3.amazonaws.com",
        help="address of S3 server, defaults to AWS, override when using minio",
    )
    parser.addoption(
        "--test-conversion",
        action="store_true",
        default=False,
        help="""conduct testing of .sdimg image built with mender-convert tool""",
    )
    parser.addoption(
        "--test-variables",
        action="store",
        default="default",
        help="configuration file holding settings for dedicated platform",
    )
    parser.addoption(
        "--mender-image",
        action="store",
        default="default",
        help="Mender compliant raw disk image",
    )
    parser.addoption(
        "--commercial-tests",
        action="store_true",
        help="Enable tests of commercial features",
    )


def pytest_configure(config):
    if not config.getoption("--no-pull"):
        print("Automatically pulling submodules. Use --no-pull to disable")
        subprocess.check_call("git submodule update --init --remote", shell=True)

    # ugly hack to access cli parameters inside common.py functions
    global configuration

    if config.getoption("--test-conversion"):
        configuration["conversion"] = True
    if config.getoption("--test-variables"):
        configuration["test_variables"] = config.getoption("--test-variables")


@pytest.fixture(scope="session")
def host(request):
    return request.config.getoption("--host")


@pytest.fixture(scope="session")
def user(request):
    return request.config.getoption("--user")


@pytest.fixture(scope="session")
def http_server(request):
    return request.config.getoption("--http-server")


@pytest.fixture(scope="session")
def board_type(request):
    return request.config.getoption("--board-type")


@pytest.fixture(scope="session")
def sdimg_location(request):
    return request.config.getoption("--sdimg-location")


@pytest.fixture(scope="session")
def mender_image(request):
    return request.config.getoption("--mender-image")


@pytest.fixture(scope="session")
def bitbake_image(request):
    return request.config.getoption("--bitbake-image")


@pytest.fixture(scope="session")
def conversion(request):
    return request.config.getoption("--test-conversion")


@pytest.fixture(scope="session")
def use_s3(request):
    return request.config.getoption("--use-s3")


@pytest.fixture(scope="session")
def s3_address(request):
    return request.config.getoption("--s3-address")


@pytest.fixture(scope="session")
def no_tmp_build_dir(request):
    return request.config.getoption("--no-tmp-build-dir")


@pytest.fixture(scope="session")
def test_variables(request):
    return request.config.getoption("--test-variables")


@pytest.fixture(autouse=True)
def commercial_test(request, bitbake_variables):
    mark = request.node.get_closest_marker("commercial")
    if mark is not None and not request.config.getoption("--commercial-tests"):
        pytest.skip("Tests of commercial features are disabled.")


def pytest_collection_modifyitems(config, items):
    if config.getoption("--test-conversion"):
        # --test-conversion given so do not skip conversion tests
        return
    skip_conversion = pytest.mark.skip(
        reason="conversion tests not yet working in Yocto"
    )
    for item in items:
        if "conversion" in item.keywords:
            item.add_marker(skip_conversion)
