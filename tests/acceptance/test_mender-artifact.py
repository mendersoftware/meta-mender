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
import json
import hashlib

# Make sure common is imported after fabric, because we override some functions.
from common import *

# The format of the artifact file which is tested here is documented at:
# https://github.com/mendersoftware/mender-artifact/blob/master/Documentation/artifact-format.md

LAST_BUILD_VERSION = None

# params is the versions we will test.
@pytest.fixture(scope="function", params=[1, 2])
def versioned_mender_image(request, prepared_test_build, latest_mender_image):
    """Gets the correct version of the artifact, whether it's the one we
    build by default, or one we have to produce ourselves.
    Returns a tuple of version and built image."""

    global LAST_BUILD_VERSION

    version = request.param

    if version is 2:
        # It's default, so skip the extra build.
        return (version, latest_mender_image)

    if LAST_BUILD_VERSION != version:
        # Run a separate build for this artifact. This doesn't conflict with the
        # above version because the non-default version ends up in a different
        # directory.
        add_to_local_conf(prepared_test_build, 'MENDER_ARTIFACT_EXTRA_ARGS = "-v %d"' % version)
        run_bitbake(prepared_test_build)
        LAST_BUILD_VERSION = version
    return (version, latest_build_artifact(prepared_test_build['build_dir'], ".mender"))

class TestMenderArtifact:
    def test_order(self, versioned_mender_image):
        """Test that order of components inside update is correct."""

        version = versioned_mender_image[0]
        mender_image = versioned_mender_image[1]

        output = subprocess.Popen(["tar", "tf", mender_image], stdout=subprocess.PIPE)
        line_no = 1
        for line in output.stdout:
            line = line.rstrip('\n\r')
            if line_no == 1:
                assert(line == "version")
            elif line_no == 2:
                if version == 1:
                    assert(line == "header.tar.gz")
                else:
                    assert(line == "manifest")
            elif line_no == 3:
                if version == 1:
                    assert(line == "data/0000.tar.gz")
                else:
                    assert(line == "header.tar.gz")
            elif line_no == 3:
                if version != 1:
                    assert(line == "data/0000.tar.gz")

            if version == 1:
                assert(line_no <= 3)
            else:
                assert(line_no <= 4)

            line_no = line_no + 1

        output.wait()

        if version == 1:
            assert(line_no == 4)
        else:
            assert(line_no == 5)

        output = subprocess.Popen(["tar xOf " + mender_image + " header.tar.gz | tar tz"],
                                  stdout=subprocess.PIPE, shell=True)
        line_no = 1
        type_info_found = False
        meta_data_found = False
        for line in output.stdout:
            line = line.rstrip('\n\r')
            if line_no == 1:
                assert(line == "header-info")
            elif line_no == 2:
                assert(line == "headers/0000/files")

            elif line == "headers/0000/type-info":
                type_info_found = True

            elif line == "headers/0000/meta-data":
                assert(type_info_found)
                meta_data_found = True

            elif ((version == 1 and (line.startswith("headers/0000/checksums/") or
                                     line.startswith("headers/0000/signatures/"))) or
                  line.startswith("headers/0000/scripts/")):
                assert(type_info_found)

            else:
                assert(False), "Unrecognized line: %s" % line

            line_no = line_no + 1

        output.wait()

        assert(meta_data_found)


    def test_files_list_integrity(self, versioned_mender_image):
        """Test that the list of files in the manifest is the same as the actual
        file list."""

        version = versioned_mender_image[0]
        mender_image = versioned_mender_image[1]

        if version == 1:
            output = subprocess.Popen(["tar xOf " + mender_image +
                                       " header.tar.gz | tar xzO headers/0000/files"],
                                      stdout=subprocess.PIPE, shell=True)
            loaded_json = json.load(output.stdout)
            manifest_list = loaded_json["files"]
            output.wait()
        else:
            output = subprocess.check_output(["tar", "xOf", mender_image, "manifest"])
            manifest_list = [line.split()[1] for line in output.strip().split('\n')]

        if version == 1:
            tar_list = []
        else:
            # By now we know this is present, and superfluous files are tested
            # for elsewhere.
            tar_list = ["header.tar.gz"]
        output = subprocess.Popen(["tar xOf " + mender_image + " data/0000.tar.gz | tar tz"],
                                  stdout=subprocess.PIPE, shell=True)
        for line in output.stdout:
            line = line.rstrip('\n\r')
            if version == 1:
                tar_list.append(line)
            else:
                tar_list.append("data/0000/" + line)
        output.wait()

        assert(sorted(manifest_list) == sorted(tar_list))


    def test_files_checksum_integrity(self, versioned_mender_image):
        """Test that the checksum of each file is correct."""

        version = versioned_mender_image[0]
        mender_image = versioned_mender_image[1]

        if version == 1:
            output = subprocess.Popen(["tar xOf " + mender_image +
                                       " header.tar.gz | tar xzO headers/0000/files"],
                                      stdout=subprocess.PIPE, shell=True)
            loaded_json = json.load(output.stdout)
            manifest_list = loaded_json["files"]
            output.wait()
        else:
            output = subprocess.check_output(["tar", "xOf", mender_image, "manifest"])
            manifest_list = []
            hash_map = {}
            for line in output.strip().split('\n'):
                manifest_list.append(line.split()[1])
                hash_map[line.split()[1]] = line.split()[0]

        for file in manifest_list:
            if version == 1:
                output = subprocess.Popen(["tar xOf " + mender_image +
                                           " data/0000.tar.gz | tar xzO " + file],
                                          stdout=subprocess.PIPE, shell=True)
            else:
                if file.startswith("data/0000/"):
                    # Data file, we need to look inside sub-tar.
                    output = subprocess.Popen(["tar xOf " + mender_image +
                                               " data/0000.tar.gz | tar xzO " + file[len("data/0000/"):]],
                                              stdout=subprocess.PIPE, shell=True)
                else:
                    # Header file, we look in outer tar.
                    output = subprocess.Popen(["tar", "xOf", mender_image, file],
                                              stdout=subprocess.PIPE)
            hasher = hashlib.sha256()
            while True:
                block = output.stdout.read(4096)
                hasher.update(block)
                if len(block) < 4096:
                    break
            output.wait()

            if version == 1:
                output = subprocess.Popen(["tar xOf " + mender_image +
                                           " header.tar.gz | tar xzO headers/0000/checksums/" +
                                           file + ".sha256sum"],
                                          stdout=subprocess.PIPE, shell=True)
                lines = output.stdout.readlines()
                assert(len(lines) == 1)
                output.wait()
                recorded_hash = lines[0].rstrip('\n\r')
            else:
                recorded_hash = hash_map[file]

            assert hasher.hexdigest() == recorded_hash, "%s doesn't match" % file


    def test_artifacts_validation(self, versioned_mender_image, bitbake_path):
        """Test that the mender-artifact tool validates the update successfully."""

        mender_image = versioned_mender_image[1]

        subprocess.check_call(["mender-artifact", "validate", mender_image])


    def test_artifacts_rootfs_size(self, versioned_mender_image, bitbake_path, bitbake_variables):
        """Test that the rootfs has the expected size. This relies on
        IMAGE_ROOTFS_SIZE *not* being overridden in the build."""

        mender_image = versioned_mender_image[1]

        output = subprocess.check_output(["mender-artifact", "read", mender_image])

        match = re.search("^ *size: *([0-9]+) *$", output, flags=re.MULTILINE)
        assert(match is not None)
        size_from_artifact = int(match.group(1))
        size_from_build = int(bitbake_variables["MENDER_CALC_ROOTFS_SIZE"]) * 1024
        assert(size_from_artifact == size_from_build)
