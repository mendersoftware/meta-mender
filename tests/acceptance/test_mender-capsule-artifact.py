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

import re

import pytest

from utils.common import (
    build_image,
    latest_build_artifact,
    get_bitbake_variables,
    run_verbose,
    signing_key,
    versions_of_recipe,
    get_local_conf_path,
    get_local_conf_orig_path,
    make_tempdir,
    version_is_minimum,
    reset_build_conf,
)


class TestCapsuleArtifact:
    class BuildDependsProvides(object):
        """
        BuildDependsProvides is a utility class for handling the depends and
        provides parameters of a Mender Artifact build
        """

        def __init__(
            self, depends={}, provides={}, clear_provides=[],
        ):
            self.provides = provides
            self.depends = depends
            self.clear_provides = clear_provides

        def __str__(self):
            string_output = ""

            if self.provides:
                provides = list(self.provides.keys())
                for name_string, version_string in zip(provides[0::2], provides[1::2]):
                    guid = name_string[
                        name_string.find("uefi-firmware.")
                        + len("uefi-firmware.") : name_string.rfind(".")
                    ]
                    name = self.provides[name_string]
                    version = self.provides[version_string]
                    string_output += 'MENDER_ARTIFACT_CAPSULE_PROVIDES[{0}] = "{1}:{2}"\n'.format(
                        guid, name, version
                    )

            if self.depends:
                for item in self.depends:
                    guid = item[
                        version_string.find("uefi-firmware.")
                        + len("uefi-firmware.") : item.rfind(".")
                    ]
                    version = self.depends[item]
                    string_output += 'MENDER_ARTIFACT_CAPSULE_DEPENDS[{0}] = "{1}"\n'.format(
                        guid, version
                    )

            return string_output

        @staticmethod
        def parse(output):
            """
            Parses the output from Mender Capsule Artifact read
            into a BuildDependsProvides instance
            """
            d = TestCapsuleArtifact.BuildDependsProvides()
            lines = output.split("\n")
            for i in range(len(lines)):
                line = lines[i]

                # Precede with two spaces to avoid matching "Clears Provides:".
                if "  Provides:" in line:
                    k = i + 1
                    tmp = {}
                    # Parse all provides on the following lines
                    while True:
                        if "Depends:" in lines[k]:
                            break
                        l = [s.strip() for s in lines[k].split(": ")]
                        assert len(l) == 2, "Line should only contain a key value pair"
                        key, val = l[0], l[1]
                        tmp[key] = val
                        k += 1
                    d.provides = tmp

                if "Depends:" in line:
                    k = i + 1
                    tmp = {}
                    # Parse all depends on the following lines
                    while True:
                        if "Metadata:" in lines[k] or "Clears Provides:" in lines[k]:
                            break
                        l = [s.strip() for s in lines[k].split(": ")]
                        assert len(l) == 2, "Line should only contain a key value pair"
                        key, val = l[0], l[1]
                        tmp[key] = val
                        k += 1
                    d.depends = tmp

                if "Clears Provides:" in line:
                    if "[]" not in line:
                        clear_provides = line[
                            line.index("[") + 1 : line.index("]")
                        ].split()
                        clear_provides = [
                            word.replace(",", "") for word in clear_provides
                        ]
                        clear_provides = [
                            word.replace('"', "") for word in clear_provides
                        ]
                        if clear_provides:
                            d.clear_provides = clear_provides

            return d

    test_cases = [
        BuildDependsProvides(
            provides={
                "uefi-firmware.e2bb9c06-70e9-4b14-97a3-5a7913176111.name": "tfa",
                "uefi-firmware.e2bb9c06-70e9-4b14-97a3-5a7913176111.version": "3",
                "uefi-firmware.e2bb9c06-70e9-4b14-97a3-5a7913176222.name": "edk2",
                "uefi-firmware.e2bb9c06-70e9-4b14-97a3-5a7913176222.version": "3",
            },
            depends={
                "uefi-firmware.e2bb9c06-70e9-4b14-97a3-5a7913176111.version": "2",
                "uefi-firmware.e2bb9c06-70e9-4b14-97a3-5a7913176222.version": "2",
            },
            clear_provides=[
                "uefi-firmware.e2bb9c06-70e9-4b14-97a3-5a7913176111.version",
                "uefi-firmware.e2bb9c06-70e9-4b14-97a3-5a7913176222.version",
            ],
        ),
        BuildDependsProvides(
            provides={
                "uefi-firmware.e2bb9c06-70e9-4b14-97a3-5a7913176111.name": "tfa",
                "uefi-firmware.e2bb9c06-70e9-4b14-97a3-5a7913176111.version": "3",
                "uefi-firmware.e2bb9c06-70e9-4b14-97a3-5a7913176222.name": "edk2",
                "uefi-firmware.e2bb9c06-70e9-4b14-97a3-5a7913176222.version": "3",
            },
            clear_provides=[
                "uefi-firmware.e2bb9c06-70e9-4b14-97a3-5a7913176111.version",
                "uefi-firmware.e2bb9c06-70e9-4b14-97a3-5a7913176222.version",
            ],
        ),
        BuildDependsProvides(
            provides={
                "uefi-firmware.e2bb9c06-70e9-4b14-97a3-5a7913176111.name": "tfa",
                "uefi-firmware.e2bb9c06-70e9-4b14-97a3-5a7913176111.version": "3",
            },
            depends={
                "uefi-firmware.e2bb9c06-70e9-4b14-97a3-5a7913176111.version": "2",
                "uefi-firmware.e2bb9c06-70e9-4b14-97a3-5a7913176222.version": "2",
            },
            clear_provides=[
                "uefi-firmware.e2bb9c06-70e9-4b14-97a3-5a7913176111.version"
            ],
        ),
    ]

    @pytest.mark.min_mender_version("2.3.0")
    @pytest.mark.parametrize("dependsprovides", test_cases)
    def test_capsule_artifact_depends_and_provides(
        self, request, prepared_test_build, bitbake_image, bitbake_path, dependsprovides
    ):
        """Test whether a build with enabled Artifact Provides and Depends does
        indeed add the parameters to the built Artifact"""

        build_image(
            prepared_test_build["build_dir"],
            prepared_test_build["bitbake_corebase"],
            bitbake_image,
            [param for param in str(dependsprovides).splitlines()],
        )

        image = latest_build_artifact(
            request, prepared_test_build["build_dir"], "*-uefi-capsule.mender"
        )

        output = run_verbose("mender-artifact read %s" % image, capture=True).decode()
        other = TestCapsuleArtifact.BuildDependsProvides.parse(output)

        assert dependsprovides.__dict__ == other.__dict__
