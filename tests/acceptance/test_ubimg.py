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

import hashlib
import os
import shutil
import subprocess
import tempfile

import pytest

from utils.common import (
    build_image,
    latest_build_artifact,
    reset_build_conf,
    make_tempdir,
)


def extract_ubimg_files(path, outdir):
    """Extract ubi image to a directory inside `outdir`. Returns path to a the
    directory, where contents of each volume are in direct sub-directories.
    Sub-directories are named after volumes.
    """
    subprocess.check_call(
        "ubireader_extract_files -o {} {}".format(outdir, path), shell=True
    )
    # extract to the following directories:
    # /tmp/meta-mender-acceptance.xzkPVM/148052886/data
    # /tmp/meta-mender-acceptance.xzkPVM/148052886/rootfsa
    # /tmp/meta-mender-acceptance.xzkPVM/148052886/rootfsb
    volumes_root = os.path.join(outdir, os.listdir(outdir)[0])
    return volumes_root


def extract_ubimg_images(path, outdir):
    """Extract ubi image to a directory inside `outdir`. Returns path to a the
    directory with each image, named after volumes.
    """
    subprocess.check_call(
        "ubireader_extract_images -o {} {}".format(outdir, path), shell=True
    )
    # extract to the following files:
    # /tmp/tmpoJ1z_s/core-image-full-cmdline-vexpress-qemu-flash.ubimg/img-1823796814_vol-rootfsb.ubifs
    # /tmp/tmpoJ1z_s/core-image-full-cmdline-vexpress-qemu-flash.ubimg/img-1823796814_vol-rootfsa.ubifs
    # /tmp/tmpoJ1z_s/core-image-full-cmdline-vexpress-qemu-flash.ubimg/img-1823796814_vol-data.ubifs
    volumes_root = os.path.join(outdir, os.listdir(outdir)[0])
    return volumes_root


def extract_ubimg_info(path):

    output = subprocess.check_output(
        "ubireader_utils_info -r {}".format(path), shell=True
    ).decode()

    # Example output from ubireader_utils_info:
    #
    # Volume data
    #     alignment       -a 1
    #     default_compr   -x lzo
    #     fanout          -f 8
    #     image_seq       -Q 24735236
    #     key_hash        -k r5
    #     leb_size        -e 262016
    #     log_lebs        -l 4
    #     max_bud_bytes   -j 8388608
    #     max_leb_cnt     -c 1024
    #     min_io_size     -m 8
    #     name            -N data
    #     orph_lebs       -p 1
    #     peb_size        -p 262144
    #     sub_page_size   -s 64
    #     version         -x 1
    #     vid_hdr_offset  -O 64
    #     vol_id          -n 2
    #
    #     #ubinize.ini#
    #     [data]
    #     vol_name=data
    #     vol_size=17031040
    #     vol_flags=0
    #     vol_type=dynamic
    #     vol_alignment=1
    #     vol_id=2

    data = {}
    volume = None
    ubinize = None

    for line in output.split("\n"):
        line = line.strip()
        if not line:
            continue

        pieces = line.split()
        # print("pieces", pieces, line)

        if pieces[0] == "Volume":
            # reached 'Volume <volname>' banner

            # save old volume information
            if ubinize and volume:
                volume["ubinize"] = ubinize
            if volume:
                data[volume["name"]] = volume

            # start new volume and ubinize
            volume = {"name": pieces[1]}
            ubinize = None

        elif volume is not None:
            # inside volume

            if pieces[0] == "#ubinize.ini#":
                # reached '#ubinize.ini#' banner
                ubinize = {}

            elif ubinize is not None:
                # currently parsing ubninize.ini part

                if pieces[0] == "[{}]".format(volume["name"]):
                    # hit [<volname>] line
                    continue

                elif "=" in pieces[0]:
                    param, val = pieces[0].split("=")
                    ubinize[param] = val

            else:
                # currently parsing volume part
                if len(pieces) == 3:
                    volume[pieces[0]] = pieces[2]

    # parsing finished

    # save last parsed volume information
    if ubinize and not "ubinize" in volume:
        volume["ubinize"] = ubinize
    if volume and not volume["name"] in data:
        data[volume["name"]] = volume

    # print('volume data:', data)
    return data


@pytest.fixture(scope="function")
def ubimg_without_uboot_env(request, latest_ubimg, prepared_test_build, bitbake_image):
    """The ubireader_utils_info tool and friends don't support our UBI volumes
    that contain the U-Boot environment and hence not valid UBIFS structures.
    Therefore, make a new temporary image that doesn't contain U-Boot."""

    # The tests are marked with "only_with_image('ubimg')", but that is checked
    # using a function fixture, and this is a session fixture, which cannot
    # depend on that. So we need this check here to bail out if we don't find a
    # ubimg.
    if not latest_ubimg:
        pytest.skip("No ubimg found")

    reset_build_conf(prepared_test_build["build_dir"])
    build_image(
        prepared_test_build["build_dir"],
        prepared_test_build["bitbake_corebase"],
        bitbake_image,
        ['MENDER_FEATURES_DISABLE_append = " mender-uboot"'],
    )

    ubimg = latest_build_artifact(
        request, prepared_test_build["build_dir"], "core-image*.ubimg"
    )
    imgdir = tempfile.mkdtemp()
    tmpimg = os.path.join(imgdir, os.path.basename(ubimg))
    shutil.copyfile(ubimg, tmpimg)

    def remove_ubimg():
        os.unlink(tmpimg)

    request.addfinalizer(remove_ubimg)

    return tmpimg


@pytest.mark.only_with_image("ubimg")
@pytest.mark.min_mender_version("1.2.0")
class TestUbimg:
    def test_total_size(self, bitbake_variables, ubimg_without_uboot_env):
        """Test that the size of the ubimg and its volumes are correct."""

        total_size_file = os.stat(ubimg_without_uboot_env).st_size
        total_size_max_expected = (
            int(bitbake_variables["MENDER_STORAGE_TOTAL_SIZE_MB"]) * 1024 * 1024
        )

        assert total_size_file <= total_size_max_expected

        data_size = int(bitbake_variables["MENDER_DATA_PART_SIZE_MB"]) * 1024 * 1024
        # rootfs size is in kB
        rootfs_size = int(bitbake_variables["MENDER_CALC_ROOTFS_SIZE"]) * 1024

        expected_total = data_size + rootfs_size * 2

        # NOTE: ubifs employs compression so the actual ubi image file size
        # will be less than what we calculated
        assert total_size_file < expected_total

        if rootfs_size < 100 * 1024 * 1024:
            # assume the image will not be less than 30% of expected size, but
            # only if calculated rootfs is of modest size
            assert total_size_file > 0.3 * expected_total
        else:
            # if rootfs is large, say 150-200MB and not heavily packed, the 30%
            # image size check will fail because UBIFS does not store empty
            # blocks, just check that the image has some reasonable size, eg.
            # 10% of rootfs size
            assert total_size_file >= 0.1 * expected_total

    def test_volumes(self, bitbake_variables, ubimg_without_uboot_env):
        """Test that ubimg has correnct number of volumes, each with correct size &
        config"""

        ubinfo = extract_ubimg_info(ubimg_without_uboot_env)

        # we're expecting 3 volumes, rootfsa, rootfsb and data
        assert len(ubinfo) == 3
        assert all([volname in ubinfo for volname in ["rootfsa", "rootfsb", "data"]])

        data_size = int(bitbake_variables["MENDER_DATA_PART_SIZE_MB"]) * 1024 * 1024
        # rootfs size is in kB
        rootfs_size = int(bitbake_variables["MENDER_CALC_ROOTFS_SIZE"]) * 1024

        # UBI adds overhead, so the actual volume size will be slightly more
        # than what requested. add 2% for overhead
        assert int(ubinfo["data"]["ubinize"]["vol_size"]) <= 1.02 * data_size
        assert int(ubinfo["rootfsa"]["ubinize"]["vol_size"]) <= 1.02 * rootfs_size
        assert int(ubinfo["rootfsb"]["ubinize"]["vol_size"]) <= 1.02 * rootfs_size

    def test_volume_contents(self, bitbake_variables, ubimg_without_uboot_env):
        """Test that data volume has correct contents"""

        with make_tempdir() as tmpdir:
            rootdir = extract_ubimg_files(ubimg_without_uboot_env, tmpdir)

            assert os.path.exists(os.path.join(rootdir, "rootfsa/usr/bin/mender"))
            assert os.path.exists(os.path.join(rootdir, "rootfsb/usr/bin/mender"))
            # TODO: verify contents of data partition

    @pytest.mark.min_yocto_version("warrior")
    def test_equal_checksum_ubimg_and_artifact(
        self, request, prepared_test_build, bitbake_image
    ):

        # See ubimg_without_uboot_env() for why this is needed. We need to do it
        # explicitly here because we need both the artifact and the ubimg.

        build_image(
            prepared_test_build["build_dir"],
            prepared_test_build["bitbake_corebase"],
            bitbake_image,
            ['MENDER_FEATURES_DISABLE_append = " mender-uboot"'],
        )

        bufsize = 1048576  # 1MiB
        with tempfile.NamedTemporaryFile() as tmp_artifact:
            latest_mender_image = latest_build_artifact(
                request, prepared_test_build["build_dir"], "*.mender"
            )
            subprocess.check_call(
                "tar xOf %s data/0000.tar.gz | tar xzO > %s"
                % (latest_mender_image, tmp_artifact.name),
                shell=True,
            )
            size = os.stat(tmp_artifact.name).st_size
            hash = hashlib.md5()
            while True:
                buf = tmp_artifact.read(bufsize)
                if len(buf) == 0:
                    break
                hash.update(buf)
            artifact_hash = hash.hexdigest()
            artifact_info = subprocess.check_output(
                ["ubireader_display_info", tmp_artifact.name]
            )
            artifact_ls = subprocess.check_output(["ls", "-l", tmp_artifact.name])

        tmpdir = tempfile.mkdtemp()
        try:
            ubifsdir = extract_ubimg_images(
                latest_build_artifact(
                    request, prepared_test_build["build_dir"], "*.ubimg"
                ),
                tmpdir,
            )
            rootfsa = os.path.join(
                ubifsdir, [img for img in os.listdir(ubifsdir) if "rootfsa" in img][0]
            )
            bytes_read = 0
            hash = hashlib.md5()
            with open(rootfsa, "rb") as fd:
                while bytes_read < size:
                    buf = fd.read(min(size - bytes_read, bufsize))
                    if len(buf) == 0:
                        break
                    bytes_read += len(buf)
                    hash.update(buf)
                image_hash = hash.hexdigest()
            image_info = subprocess.check_output(["ubireader_display_info", rootfsa])
            image_ls = subprocess.check_output(["ls", "-l", rootfsa])
        finally:
            shutil.rmtree(tmpdir)

        assert artifact_info == image_info
        assert artifact_hash == image_hash, "Artifact:\n%s\nImage:\n%s" % (
            artifact_ls,
            image_ls,
        )
