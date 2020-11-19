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

import subprocess
import re
import hashlib

import pytest

from utils.common import build_image, latest_build_artifact, version_is_minimum


# The format of the artifact file which is tested here is documented at:
# https://github.com/mendersoftware/mender-artifact/blob/master/Documentation/artifact-format.md

LAST_BUILD_VERSION = None

# params is the versions we will test.
@pytest.fixture(scope="function", params=[2, 3])
def versioned_mender_image(
    request, prepared_test_build, latest_mender_image, bitbake_variables, bitbake_image
):
    """Gets the correct version of the artifact, whether it's the one we
    build by default, or one we have to produce ourselves.
    Returns a tuple of version and built image."""

    global LAST_BUILD_VERSION

    version = request.param

    if version == 1:
        pytest.failNow()

    if (
        version >= 2
        and not version_is_minimum(bitbake_variables, "mender-artifact", "2.0.0")
    ) or (
        version >= 3
        and not version_is_minimum(bitbake_variables, "mender-artifact", "3.0.0")
    ):
        pytest.skip("Requires version %d of mender-artifact format." % version)

    if version_is_minimum(bitbake_variables, "mender-artifact", "3.0.0"):
        default_version = 3
    elif version_is_minimum(bitbake_variables, "mender-artifact", "2.0.0"):
        default_version = 2
    else:
        default_version = 2

    if LAST_BUILD_VERSION != version:
        # Run a separate build for this artifact. This doesn't conflict with the
        # above version because the non-default version ends up in a different
        # directory.
        if version != default_version:
            build_image(
                prepared_test_build["build_dir"],
                prepared_test_build["bitbake_corebase"],
                bitbake_image,
                ['MENDER_ARTIFACT_EXTRA_ARGS = "-v %d"' % version],
            )
        else:
            build_image(
                prepared_test_build["build_dir"],
                prepared_test_build["bitbake_corebase"],
                bitbake_image,
            )

        LAST_BUILD_VERSION = version
    return (
        version,
        latest_build_artifact(
            request, prepared_test_build["build_dir"], "core-image*.mender"
        ),
    )


@pytest.mark.only_with_image("mender")
class TestMenderArtifact:
    @pytest.mark.min_mender_version("1.0.0")
    def test_order(self, versioned_mender_image):
        """Test that order of components inside update is correct."""

        version = versioned_mender_image[0]
        mender_image = versioned_mender_image[1]

        output = subprocess.Popen(["tar", "tf", mender_image], stdout=subprocess.PIPE)
        line_no = 1

        while True:
            line = output.stdout.readline().decode()
            if not line:
                break

            line = line.rstrip("\n\r")
            if line_no == 1:
                assert line == "version"
            elif line_no == 2:
                assert line == "manifest"
            elif line_no == 3:
                assert line == "header.tar.gz"
            elif line_no == 4:
                assert line == "data/0000.tar.gz"

            assert line_no <= 4

            line_no = line_no + 1

        output.wait()

        assert line_no == 5

        output = subprocess.Popen(
            ["tar xOf " + mender_image + " header.tar.gz | tar tz"],
            stdout=subprocess.PIPE,
            shell=True,
        )
        line_no = 1
        type_info_found = False
        meta_data_found = False

        while True:
            line = output.stdout.readline().decode()
            if not line:
                break
            line = line.rstrip("\n\r")
            if line_no == 1:
                assert line == "header-info"

            elif line_no == 2 and version < 3:
                assert line == "headers/0000/files"

            elif line == "headers/0000/type-info":
                type_info_found = True

            elif line == "headers/0000/meta-data":
                assert type_info_found
                meta_data_found = True

            else:
                assert False, "Unrecognized line: %s" % line

            line_no = line_no + 1

        output.wait()

        assert meta_data_found

    @pytest.mark.min_mender_version("1.0.0")
    def test_files_list_integrity(self, versioned_mender_image):
        """Test that the list of files in the manifest is the same as the actual
        file list."""

        version = versioned_mender_image[0]
        mender_image = versioned_mender_image[1]

        output = subprocess.check_output(["tar", "xOf", mender_image, "manifest"])
        manifest_list = [
            line.split()[1] for line in output.decode().strip().split("\n")
        ]

        # By now we know this is present, and superfluous files are tested
        # for elsewhere.
        tar_list = ["version", "header.tar.gz"]
        output = subprocess.Popen(
            ["tar xOf " + mender_image + " data/0000.tar.gz | tar tz"],
            stdout=subprocess.PIPE,
            shell=True,
        )
        while True:
            line = output.stdout.readline().decode()
            if not line:
                break

            line = line.rstrip("\n\r")
            tar_list.append("data/0000/" + line)
        output.wait()

        assert sorted(manifest_list) == sorted(tar_list)

    @pytest.mark.min_mender_version("1.0.0")
    def test_files_checksum_integrity(self, versioned_mender_image):
        """Test that the checksum of each file is correct."""

        version = versioned_mender_image[0]
        mender_image = versioned_mender_image[1]

        output = subprocess.check_output(["tar", "xOf", mender_image, "manifest"])
        manifest_list = []
        hash_map = {}

        for line in output.decode().strip().split("\n"):
            manifest_list.append(line.split()[1])
            hash_map[line.split()[1]] = line.split()[0]

        for file in manifest_list:
            if file.startswith("data/0000/"):
                # Data file, we need to look inside sub-tar.
                output = subprocess.Popen(
                    [
                        "tar xOf "
                        + mender_image
                        + " data/0000.tar.gz | tar xzO "
                        + file[len("data/0000/") :]
                    ],
                    stdout=subprocess.PIPE,
                    shell=True,
                )
            else:
                # Header file, we look in outer tar.
                output = subprocess.Popen(
                    ["tar", "xOf", mender_image, file], stdout=subprocess.PIPE
                )
            hasher = hashlib.sha256()
            while True:
                block = output.stdout.read(4096)
                hasher.update(block)
                if len(block) < 4096:
                    break
            output.wait()

            recorded_hash = hash_map[file]

            assert hasher.hexdigest() == recorded_hash, "%s doesn't match" % file

    @pytest.mark.min_mender_version("1.0.0")
    def test_artifacts_validation(self, versioned_mender_image, bitbake_path):
        """Test that the mender-artifact tool validates the update successfully."""

        mender_image = versioned_mender_image[1]

        subprocess.check_call(["mender-artifact", "validate", mender_image])

    @pytest.mark.min_mender_version("1.0.0")
    def test_artifacts_rootfs_size(
        self, versioned_mender_image, bitbake_path, bitbake_variables
    ):
        """Test that the rootfs has the expected size. This relies on
        IMAGE_ROOTFS_SIZE *not* being overridden in the build."""

        mender_image = versioned_mender_image[1]

        output = subprocess.check_output(["mender-artifact", "read", mender_image])

        match = re.search(
            r".*name:\s+(?P<image>[a-z-.0-9]+).*\n.*size:\s+(?P<size>[0-9]+)",
            output.decode(),
            flags=re.MULTILINE,
        )
        assert match

        gd = match.groupdict()
        assert "image" in gd and "size" in gd

        size_from_artifact = int(gd["size"])
        size_from_build = int(bitbake_variables["MENDER_CALC_ROOTFS_SIZE"]) * 1024

        print("matched:", gd)
        if re.match(r".*\.ubifs", gd["image"]):
            # some filesystems (eg. ubifs) may use compression or empty space may
            # not be a part of the image, in which case the image will be smaller
            # or equal to MENDER_CALC_ROOTFS_SIZE
            assert size_from_artifact <= size_from_build
            # assume that the compressed image will be not less than 30% of
            # allocated rootfs size size
            assert size_from_artifact >= 0.3 * size_from_build
        elif re.match(r".*\.ext[234]", gd["image"]):
            assert size_from_artifact == size_from_build
        else:
            pytest.skip("unsupported image artifact {}".format(gd["image"]))
