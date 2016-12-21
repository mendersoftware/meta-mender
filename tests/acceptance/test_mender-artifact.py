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

class TestMenderArtifact:
    def test_order(self, latest_mender_image):
        """Test that order of components inside update is correct."""

        output = subprocess.Popen(["tar", "tf", latest_mender_image], stdout=subprocess.PIPE)
        line_no = 1
        for line in output.stdout:
            line = line.rstrip('\n\r')
            if line_no == 1:
                assert(line == "version")
            elif line_no == 2:
                assert(line == "header.tar.gz")
            elif line_no == 3:
                assert(line == "data/0000.tar.gz")

            assert(line_no <= 3)

            line_no = line_no + 1

        output.wait()

        assert(line_no == 4)

        output = subprocess.Popen(["tar xOf " + latest_mender_image + " header.tar.gz | tar tz"],
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

            elif (line.startswith("headers/0000/checksums/") or
                line.startswith("headers/0000/signatures/") or
                line.startswith("headers/0000/scripts/")):
                assert(type_info_found)

            else:
                assert(False), "Unrecognized line: %s" % line

            line_no = line_no + 1

        output.wait()

        assert(meta_data_found)


    def test_files_list_integrity(self, latest_mender_image):
        """Test that the 'files' list in the json is the same as the actual
        file list."""

        output = subprocess.Popen(["tar xOf " + latest_mender_image +
                                   " header.tar.gz | tar xzO headers/0000/files"],
                                  stdout=subprocess.PIPE, shell=True)
        loaded_json = json.load(output.stdout)
        json_list = loaded_json["files"]
        output.wait()

        output = subprocess.Popen(["tar xOf " + latest_mender_image + " data/0000.tar.gz | tar tz"],
                                  stdout=subprocess.PIPE, shell=True)
        tar_list = []
        for line in output.stdout:
            line = line.rstrip('\n\r')
            tar_list.append(line)
        output.wait()

        assert(sorted(json_list) == sorted(tar_list))


    def test_files_checksum_integrity(self, latest_mender_image):
        """Test that the checksum of each file is correct."""

        output = subprocess.Popen(["tar xOf " + latest_mender_image +
                                   " header.tar.gz | tar xzO headers/0000/files"],
                                  stdout=subprocess.PIPE, shell=True)
        loaded_json = json.load(output.stdout)
        json_list = loaded_json["files"]
        output.wait()

        for file in json_list:
            output = subprocess.Popen(["tar xOf " + latest_mender_image +
                                       " data/0000.tar.gz | tar xzO " + file],
                                      stdout=subprocess.PIPE, shell=True)
            hasher = hashlib.sha256()
            while True:
                block = output.stdout.read(4096)
                hasher.update(block)
                if len(block) < 4096:
                    break
            output.wait()

            output = subprocess.Popen(["tar xOf " + latest_mender_image +
                                       " header.tar.gz | tar xzO headers/0000/checksums/" +
                                       file + ".sha256sum"],
                                      stdout=subprocess.PIPE, shell=True)
            lines = output.stdout.readlines()
            assert(len(lines) == 1)
            output.wait()

            assert(hasher.hexdigest() == lines[0].rstrip('\n\r'))


    def test_artifacts_validation(self, latest_mender_image, bitbake_path):
        """Test that the mender-artifact tool validates the update successfully."""

        subprocess.check_call(["mender-artifact", "validate", latest_mender_image])
