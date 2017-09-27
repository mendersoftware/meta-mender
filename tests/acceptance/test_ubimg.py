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

# Make sure common is imported after fabric, because we override some functions.
from common import *

def extract_ubimg(path, outdir):
    """Extract ubi image to a directory inside `outdir`. Returns path to a the
    directory, where contents of each volume are in direct sub-directories.
    Sub-directories are named after volumes.
    """
    subprocess.check_call("ubireader_extract_files -o {} {}".format(outdir, path),
                          shell=True)
    # extract to the following directories:
    # /tmp/meta-mender-acceptance.xzkPVM/148052886/data
    # /tmp/meta-mender-acceptance.xzkPVM/148052886/rootfsa
    # /tmp/meta-mender-acceptance.xzkPVM/148052886/rootfsb
    volumes_root = os.path.join(outdir, os.listdir(outdir)[0])
    return volumes_root


def extract_ubimg_info(path):

    output = subprocess.check_output("ubireader_utils_info -r {}".format(path), shell=True)

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

    for line in output.split('\n'):
        line = line.strip()
        if not line:
            continue

        pieces = line.split()
        # print("pieces", pieces, line)

        if pieces[0] == 'Volume':
            # reached 'Volume <volname>' banner

            # save old volume information
            if ubinize and volume:
                volume['ubinize'] = ubinize
            if volume:
                data[volume['name']] = volume

            # start new volume and ubinize
            volume = {'name': pieces[1]}
            ubinize = None

        elif volume is not None:
            # inside volume

            if pieces[0] == '#ubinize.ini#':
                # reached '#ubinize.ini#' banner
                ubinize = {}

            elif ubinize is not None:
                # currently parsing ubninize.ini part

                if pieces[0] == '[{}]'.format(volume['name']):
                    # hit [<volname>] line
                    continue

                elif '=' in pieces[0]:
                    param, val = pieces[0].split('=')
                    ubinize[param] = val

            else:
                # currently parsing volume part
                if len(pieces) == 3:
                    volume[pieces[0]] = pieces[2]

    # parsing finished

    # save last parsed volume information
    if ubinize and not 'ubinize' in volume:
        volume['ubinize'] = ubinize
    if volume and not volume['name'] in data:
        data[volume['name']] = volume

    # print('volume data:', data)
    return data


@pytest.mark.only_with_image('ubimg')
@pytest.mark.min_mender_version('1.2.0')
class TestUbimg:
    def test_total_size(self, bitbake_variables, latest_ubimg):
        """Test that the size of the ubimg and its volumes are correct."""

        total_size_file = os.stat(latest_ubimg).st_size
        total_size_max_expected = int(bitbake_variables['MENDER_STORAGE_TOTAL_SIZE_MB']) * 1024 * 1024

        assert total_size_file <= total_size_max_expected

        data_size = int(bitbake_variables['MENDER_DATA_PART_SIZE_MB']) * 1024 * 1024
        # rootfs size is in kB
        rootfs_size = int(bitbake_variables['MENDER_CALC_ROOTFS_SIZE']) * 1024

        expected_total = data_size + rootfs_size * 2

        # NOTE: ubifs employs compression so the actual ubi image file size
        # will be less than what we calculated
        assert total_size_file < expected_total

        if rootfs_size < 100*1024*1024:
            # assume the image will not be less than 30% of expected size, but
            # only if calculated rootfs is of modest size
            assert total_size_file > 0.3 * expected_total
        else:
            # if rootfs is large, say 150-200MB and not heavily packed, the 30%
            # image size check will fail because UBIFS does not store empty
            # blocks, just check that the image has some reasonable size, eg.
            # 10% of rootfs size
            assert total_size_file >= 0.1 * expected_total

    def test_volumes(self, bitbake_variables, latest_ubimg):
        """Test that ubimg has correnct number of volumes, each with correct size &
        config"""

        ubinfo = extract_ubimg_info(latest_ubimg)

        # we're expecting 3 volumes, rootfsa, rootfsb and data
        assert len(ubinfo) == 3
        assert all([volname in ubinfo for volname in ['rootfsa', 'rootfsb', 'data']])

        data_size = int(bitbake_variables['MENDER_DATA_PART_SIZE_MB']) * 1024 * 1024
        # rootfs size is in kB
        rootfs_size = int(bitbake_variables['MENDER_CALC_ROOTFS_SIZE']) * 1024

        # UBI adds overhead, so the actual volume size will be slightly more
        # than what requested. add 2% for overhead
        assert int(ubinfo['data']['ubinize']['vol_size']) <= 1.02 * data_size
        assert int(ubinfo['rootfsa']['ubinize']['vol_size']) <= 1.02 * rootfs_size
        assert int(ubinfo['rootfsb']['ubinize']['vol_size']) <= 1.02 * rootfs_size

    def test_volume_contents(self, bitbake_variables, latest_ubimg):
        """Test that data volume has correct contents"""

        with make_tempdir() as tmpdir:
            rootdir = extract_ubimg(latest_ubimg, tmpdir)

            assert os.path.exists(os.path.join(rootdir, 'rootfsa/usr/bin/mender'))
            assert os.path.exists(os.path.join(rootdir, 'rootfsb/usr/bin/mender'))
            # TODO: verify contents of data partition
