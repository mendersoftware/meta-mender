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

import pytest
import os
import time

from conftest import setup_qemu


from utils.common import (
    build_image,
    signing_key,
    reset_build_conf,
)


@pytest.fixture(scope="function")
def build_image_with_signed_bootstrap_artifact(
    request, conversion, prepared_test_build_base, bitbake_image
):
    """

    Simple override of the global build_image_fn fixture with signatures added,
    and the mender-client systemd service enabled.

    Due to the serial nature of the other tests, and the fact that they share
    the same QEMU instance, and we access the instance on `localhost`, this
    test, which is only function scoped, will have to be run first when all
    other tests are collected.

    See the `pytest_collections_modifyitems` hook override in `conftest.py` for
    more info.

    """

    def img_builder():
        if conversion:
            assert os.environ.get("BUILDDIR", False), "BUILDDIR must be set"
            return os.environ["BUILDDIR"]

        reset_build_conf(prepared_test_build_base["build_dir"])
        build_image(
            prepared_test_build_base["build_dir"],
            prepared_test_build_base["bitbake_corebase"],
            bitbake_image,
            [
                'MENDER_ARTIFACT_SIGNING_KEY = "%s"'
                % os.path.join(os.getcwd(), signing_key("RSA").private),
                'MENDER_ARTIFACT_VERIFY_KEY = "%s"'
                % os.path.join(os.getcwd(), signing_key("RSA").public),
                'SYSTEMD_AUTO_ENABLE_pn-mender-client = "enable"',
            ],
        )
        return prepared_test_build_base["build_dir"]

    return img_builder


@pytest.fixture(scope="function")
def boot_device_with_bootstrap_image(
    request,
    qemu_wrapper,
    session_connection,
    board_type,
    conversion,
    build_image_with_signed_bootstrap_artifact,
):

    """

    Simple override of the global setup_board fixture with 'function' local scope.

    This means that the board is booted, and brought down as a part of the same
    test function, as opposed to ran as a part of all the tests, as the global
    test fixture does.

    """

    print("board type: ", board_type)

    if "qemu" in board_type:
        image_dir = build_image_with_signed_bootstrap_artifact()
        return setup_qemu(request, qemu_wrapper, image_dir, session_connection)
    elif "raspberrypi4" in board_type and request.config.getoption(
        "--hardware-testing"
    ):
        return setup_hardware_test_board(request, session_connection)
    elif conversion:
        pytest.skip("Skip non-qemu platforms for mender-convert")
    else:
        pytest.fail("unsupported board type {}".format(board_type))

    # Make sure 'image.dat' is not present on the device
    session_connection.run("rm -f image.dat")


@pytest.mark.min_mender_version("3.4.0")
@pytest.mark.min_yocto_version("dunfell")
@pytest.mark.only_with_image("ext4", "ext3", "ext2")
def test_bootstrap_artifact_install(
    request, boot_device_with_bootstrap_image, connection,
):
    """Test that the Mender Bootstrap Artifact works correctly

    # 1. - Build an image with a signed bootstrap Artifact

    # 2. - Boot a device with the given image

    # 3. - Verify that the bootstrap artifact has populated the DB, and is deleted

    # 4. Bring the device down

    """

    # Give the client a little bit of time to install the Artifact
    for i in range(10):
        if "bootstrap.mender" not in connection.run("ls /data/mender/").stdout.split():
            break
        time.sleep(10)

    # Check for the presence of the bootstrap Artifact
    # This should not be present, if the client has installed it
    assert "bootstrap.mender" not in connection.run("ls /data/mender/").stdout.split()

    # Check that the database of the client has been populated
    device_provides = connection.run("mender show-provides").stdout.strip()
    assert "rootfs-image.checksum" in device_provides
    assert "rootfs-image.version" in device_provides
