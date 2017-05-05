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

import os
import pytest
import subprocess

# Make sure common is imported after fabric, because we override some functions.
from common import *

def run_verbose(cmd):
    print(cmd)
    return subprocess.check_call(cmd, shell=True, executable="/bin/bash")

def run_bitbake(prepared_test_build):
    run_verbose("%s && bitbake %s" % (prepared_test_build['env_setup'],
                                      prepared_test_build['image_name']))

class EmbeddedBootloader:
    loader = None
    offset = 0

    def __init__(self, bitbake_variables, loader_base, offset):
        loader_dir = bitbake_variables['DEPLOY_DIR_IMAGE']
        loader = None

        if loader_base is not None and loader_base != "":
            loader = os.path.join(loader_dir, file)

        self.loader = loader
        self.offset = offset


@pytest.fixture(scope="module")
def prepared_test_build_base(request, bitbake_variables, latest_sdimg):
    """Base fixture for prepared_test_build. Returns the same as that one."""

    build_dir = os.path.join(os.environ['BUILDDIR'], "test-build-tmp")

    def cleanup_test_build():
        run_verbose("rm -rf %s" % build_dir)

    cleanup_test_build()
    request.addfinalizer(cleanup_test_build)

    env_setup = "cd %s && . oe-init-build-env %s" % (bitbake_variables['COREBASE'], build_dir)

    run_verbose(env_setup)

    run_verbose("cp %s/conf/* %s/conf" % (os.environ['BUILDDIR'], build_dir))
    local_conf = os.path.join(build_dir, "conf", "local.conf")
    fd = open(local_conf, "a")
    fd.write('SSTATE_MIRRORS = " file://.* file://%s/sstate-cache/PATH"\n' % os.environ['BUILDDIR'])
    # The idea here is to append customizations, and then reset the file by
    # deleting everything below this line.
    fd.write('### TEST CUSTOMIZATIONS BELOW HERE ###\n')
    fd.close()

    os.symlink(os.path.join(os.environ['BUILDDIR'], "downloads"), os.path.join(build_dir, "downloads"))

    sdimg_base = os.path.basename(latest_sdimg)
    # Remove machine, date and suffix.
    image_name = re.sub("-%s(-[0-9]+)?\.sdimg$" % bitbake_variables['MACHINE'], "", sdimg_base)

    return {'build_dir': build_dir,
            'image_name': image_name,
            'env_setup': env_setup,
            'local_conf': local_conf
    }


@pytest.fixture(scope="function")
def prepared_test_build(prepared_test_build_base):
    """Prepares a separate test build directory where a custom build can be
    made, which reuses the sstate-cache. Returns a dictionary with:
    - build_path
    - image_name
    - env_setup (passed to some functions)
    - local_conf
    """

    old_file = prepared_test_build_base['local_conf']
    new_file = old_file + ".tmp"

    old = open(old_file)
    new = open(new_file, "w")

    # Reset "local.conf" by removing everything below the special line.
    for line in old:
        new.write(line)
        if line == "### TEST CUSTOMIZATIONS BELOW HERE ###\n":
            break

    old.close()
    new.close()
    os.rename(new_file, old_file)

    return prepared_test_build_base


def add_to_local_conf(prepared_test_build, string):
    """Add given string to local.conf before the build. Newline is added
    automatically."""

    fd = open(prepared_test_build['local_conf'], "a")
    fd.write("%s\n" % string)
    fd.close()


class TestBuild:
    # List of pairs consisting of file that should be checksummed, and file that
    # should contain that checksum.
    @pytest.mark.parametrize("file_sums", [("../../meta-mender-demo/recipes-mender/mender/files/server.crt",
                                            "../../meta-mender-core/recipes-mender/mender/mender.inc"),
                                           ("../../meta-mender-demo/recipes-mender/mender/files/artifact-verify-key.pem",
                                            "../../meta-mender-core/recipes-mender/mender/mender.inc"),
    ])
    def test_hardcoded_md5sums(self, file_sums):
        """Test that the md5sums we have on record matches the ones we have hardcoded in
        the layer. This makes sure the warnings about these are correct.

        """

        output = subprocess.check_output(["md5sum", file_sums[0]])

        # Crude check, just make sure it occurs in the build file.
        subprocess.check_call(["fgrep", "-q", output.split()[0], file_sums[1]])


    def test_bootloader_embed(self, prepared_test_build):
        """Test that IMAGE_BOOTLOADER_FILE causes the bootloader to be embedded
        correctly in the resulting sdimg."""

        loader_file = "bootloader.bin"
        loader_offset = 4
        add_to_local_conf(prepared_test_build, 'IMAGE_BOOTLOADER_FILE = "%s"' % loader_file)
        add_to_local_conf(prepared_test_build, 'IMAGE_BOOTLOADER_BOOTSECTOR_OFFSET = "%d"' % loader_offset)

        new_bb_vars = get_bitbake_variables("core-image-minimal", prepared_test_build['env_setup'])

        loader_dir = new_bb_vars['DEPLOY_DIR_IMAGE']
        loader_path = os.path.join(loader_dir, loader_file)

        run_verbose("mkdir -p %s" % os.path.dirname(loader_path))
        run_verbose("cp /etc/os-release %s" % loader_path)

        run_bitbake(prepared_test_build)

        built_sdimg = latest_build_artifact(prepared_test_build['build_dir'], ".sdimg")

        original = os.open(loader_path, os.O_RDONLY)
        embedded = os.open(built_sdimg, os.O_RDONLY)
        os.lseek(embedded, loader_offset * 512, 0)

        checked = 0
        block_size = 4096
        while True:
            org_read = os.read(original, block_size)
            org_read_size = len(org_read)
            emb_read = os.read(embedded, org_read_size)

            assert(org_read == emb_read), "Embedded bootloader is not identical to the file specified in IMAGE_BOOTLOADER_FILE"

            if org_read_size < block_size:
                break

        os.close(original)
        os.close(embedded)


    def test_image_rootfs_extra_space(self, prepared_test_build, bitbake_variables):
        """Test that setting IMAGE_ROOTFS_EXTRA_SPACE to arbitrary values does
        not break the build."""

        add_to_local_conf(prepared_test_build, 'IMAGE_EXTRA_ROOTFS_SPACE_append = " + 640 - 222 + 900"')

        run_bitbake(prepared_test_build)

        built_rootfs = latest_build_artifact(prepared_test_build['build_dir'], ".ext4")

        assert(os.stat(built_rootfs).st_size == int(bitbake_variables['MENDER_CALC_ROOTFS_SIZE']) * 1024)


    def test_artifact_signing_keys(self, prepared_test_build, bitbake_variables, bitbake_path, signing_key):
        """Test that MENDER_ARTIFACT_SIGNING_KEY and MENDER_ARTIFACT_VERIFY_KEY
        works correctly."""

        # Either of the two keys may be specified already if we're using the
        # demo layer.
        if bitbake_variables.get('MENDER_ARTIFACT_SIGNING_KEY') is None:
            add_to_local_conf(prepared_test_build, 'MENDER_ARTIFACT_SIGNING_KEY = "%s"'
                              % os.path.join(os.getcwd(), signing_key.private))
        if (bitbake_variables.get('MENDER_ARTIFACT_VERIFY_KEY') is None
            and "artifact-verify-key.pem" not in get_bitbake_variables('mender').get('SRC_URI')):
            add_to_local_conf(prepared_test_build, 'MENDER_ARTIFACT_VERIFY_KEY = "%s"'
                              % os.path.join(os.getcwd(), signing_key.public))

        run_bitbake(prepared_test_build)

        built_rootfs = latest_build_artifact(prepared_test_build['build_dir'], ".ext[234]")
        # Copy out the key we just added from the image and use that to
        # verify instead of the original, just to be sure.
        subprocess.check_call(["debugfs", "-R",
                               "dump -p /etc/mender/artifact-verify-key.pem artifact-verify-key.pem",
                               built_rootfs])
        try:
            built_artifact = latest_build_artifact(prepared_test_build['build_dir'], ".mender")
            output = subprocess.check_output(["mender-artifact", "read", "-k",
                                              os.path.join(os.getcwd(), "artifact-verify-key.pem"),
                                              built_artifact])
            assert(output.find("Signature: signed and verified correctly") >= 0)

        finally:
            os.remove("artifact-verify-key.pem")
