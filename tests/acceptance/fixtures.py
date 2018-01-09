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

from common import *

@pytest.fixture(scope="session")
def setup_board(request, clean_image, bitbake_variables):
    bt = pytest.config.getoption("--board-type")

    print('board type:', bt)
    if "qemu" in bt:
        return qemu_running(request, clean_image)
    elif bt == "beagleboneblack":
        return setup_bbb(request)
    elif bt == "raspberrypi3":
        return setup_rpi3(request)
    elif bt == "colibri-imx7":
        return setup_colibri_imx7(request, clean_image)
    else:
        pytest.fail('unsupported board type {}'.format(bt))


@pytest.fixture(scope="session")
def setup_colibri_imx7(request, clean_image):
    latest_uboot = latest_build_artifact(clean_image['build_dir'], "u-boot-nand.imx")
    latest_ubimg = latest_build_artifact(clean_image['build_dir'], ".ubimg")

    if not latest_uboot:
        pytest.fail('failed to find U-Boot binary')

    if not latest_ubimg:
        pytest.failed('failed to find latest ubimg for the board')

    def board_setup():
        common_board_setup(files=[latest_ubimg, latest_uboot],
                           remote_path='/tmp',
                           image_file=os.path.basename(latest_ubimg))

    execute(board_setup, hosts=conftest.current_hosts())

    def board_cleanup():
        def board_cleanup_impl():
            common_board_cleanup()
        execute(board_cleanup_impl, hosts=conftest.current_hosts())

    request.addfinalizer(board_cleanup)

@pytest.fixture(scope="session")
def setup_bbb(request):
    def board_cleanup():
        execute(common_board_cleanup, hosts=conftest.current_hosts())

    execute(common_boot_from_internal, hosts=conftest.current_hosts())
    request.addfinalizer(board_cleanup)

@pytest.fixture(scope="session")
def setup_rpi3(request):
    def board_cleanup():
        execute(common_board_cleanup, hosts=conftest.current_hosts())

    execute(common_boot_from_internal, hosts=conftest.current_hosts())
    request.addfinalizer(board_cleanup)

@pytest.fixture(scope="module")
def qemu_running(request, clean_image):
    latest_sdimg = latest_build_artifact(clean_image['build_dir'], ".sdimg")
    latest_vexpress_nor = latest_build_artifact(clean_image['build_dir'], ".vexpress-nor")

    print("sdimg: {} vexpress-nor: {}".format(latest_sdimg, latest_vexpress_nor))

    if latest_sdimg:
        qemu, img_path = start_qemu_sdimg(latest_sdimg)
    elif latest_vexpress_nor:
        qemu, img_path = start_qemu_flash(latest_vexpress_nor)
    else:
        pytest.fail("cannot find a suitable image type")

    print("qemu started with pid {}, image {}".format(qemu.pid, img_path))

    # Make sure we revert to the first root partition on next reboot, makes test
    # cases more predictable.
    def qemu_finalizer():
        def qemu_finalizer_impl():
            try:
                manual_uboot_commit()
                run("halt")
                halt_time = time.time()
                # Wait up to 30 seconds for shutdown.
                while halt_time + 30 > time.time() and qemu.poll() is None:
                    time.sleep(1)
            except:
                # Nothing we can do about that.
                pass

            # kill qemu
            try:
                qemu.terminate()
            except OSError as oserr:
                # qemu might have exited before we reached this place
                if oserr.errno == errno.ESRCH:
                    pass
                else:
                    raise

            qemu.wait()
            os.remove(img_path)

        execute(qemu_finalizer_impl, hosts=conftest.current_hosts())

    request.addfinalizer(qemu_finalizer)

    execute(qemu_prep_fresh_host, hosts=conftest.current_hosts())


@pytest.fixture(scope="function")
def no_image_file(setup_board):
    """Make sure 'image.dat' is not present on the device."""
    execute(no_image_file_impl, hosts=conftest.current_hosts())


def no_image_file_impl():
    run("rm -f image.dat")
@pytest.fixture(scope="session")
def latest_rootfs():
    assert(os.environ.get('BUILDDIR', False)), "BUILDDIR must be set"

    # Find latest built rootfs.
    return latest_build_artifact(os.environ['BUILDDIR'], ".ext[234]")

@pytest.fixture(scope="session")
def latest_sdimg():
    assert(os.environ.get('BUILDDIR', False)), "BUILDDIR must be set"

    # Find latest built rootfs.
    return latest_build_artifact(os.environ['BUILDDIR'], ".sdimg")

@pytest.fixture(scope="session")
def latest_ubimg():
    assert(os.environ.get('BUILDDIR', False)), "BUILDDIR must be set"

    # Find latest built ubimg.
    return latest_build_artifact(os.environ['BUILDDIR'], ".ubimg")

@pytest.fixture(scope="session")
def latest_ubifs():
    assert(os.environ.get('BUILDDIR', False)), "BUILDDIR must be set"

    # Find latest built ubifs. NOTE: need to include *core-image* otherwise
    # we'll likely match data partition file - data.ubifs
    return latest_build_artifact(os.environ['BUILDDIR'], "*core-image*.ubifs")

@pytest.fixture(scope="session")
def latest_vexpress_nor():
    assert(os.environ.get('BUILDDIR', False)), "BUILDDIR must be set"

    # Find latest built ubifs. NOTE: need to include *core-image* otherwise
    # we'll likely match data partition file - data.ubifs
    return latest_build_artifact(os.environ['BUILDDIR'], ".vexpress-nor")

@pytest.fixture(scope="session")
def latest_mender_image():
    assert(os.environ.get('BUILDDIR', False)), "BUILDDIR must be set"

    # Find latest built rootfs.
    return latest_build_artifact(os.environ['BUILDDIR'], ".mender")

@pytest.fixture(scope="function")
def successful_image_update_mender(request, clean_image):
    """Provide a 'successful_image_update.mender' file in the current directory that
    contains the latest built update."""

    latest_mender_image = latest_build_artifact(clean_image['build_dir'], ".mender")

    if os.path.lexists("successful_image_update.mender"):
        print("Using existing 'successful_image_update.mender' in current directory")
        return "successful_image_update.mender"

    os.symlink(latest_mender_image, "successful_image_update.mender")

    print("Symlinking 'successful_image_update.mender' to '%s'" % latest_mender_image)

    def cleanup_image_dat():
        os.remove("successful_image_update.mender")

    request.addfinalizer(cleanup_image_dat)

    return "successful_image_update.mender"

@pytest.fixture(scope="session")
def bitbake_variables():
    """Returns a map of all bitbake variables active for the build."""

    assert(os.environ.get('BUILDDIR', False)), "BUILDDIR must be set"

    return get_bitbake_variables("core-image-minimal")

@pytest.fixture(scope="session")
def bitbake_path_string():
    """Fixture that returns the PATH we need for our testing tools"""

    assert(os.environ.get('BUILDDIR', False)), "BUILDDIR must be set"

    current_dir = os.open(".", os.O_RDONLY)
    os.chdir(os.environ['BUILDDIR'])

    # See the recipe for details about this call.
    subprocess.check_output(["bitbake", "-c", "prepare_recipe_sysroot", "mender-test-dependencies"])

    os.fchdir(current_dir)

    bb_testing_variables = get_bitbake_variables("mender-test-dependencies")

    return bb_testing_variables['PATH'] + ":" + os.environ['PATH']

@pytest.fixture(scope="function")
def bitbake_path(request, bitbake_path_string):
    """Fixture that enables the PATH we need for our testing tools."""

    old_path = os.environ['PATH']

    os.environ['PATH'] = bitbake_path_string

    def path_restore():
        os.environ['PATH'] = old_path

    request.addfinalizer(path_restore)

    return os.environ['PATH']

@pytest.fixture(scope="session")
def clean_image(request, prepared_test_build_base):
    add_to_local_conf(prepared_test_build_base,
                      'SYSTEMD_AUTO_ENABLE_pn-mender = "disable"')
    add_to_local_conf(prepared_test_build_base,
                      'EXTRA_IMAGE_FEATURES_append = " ssh-server-openssh"')
    run_bitbake(prepared_test_build_base)
    return prepared_test_build_base


@pytest.fixture(scope="session")
def prepared_test_build_base(request, bitbake_variables):
    """Base fixture for prepared_test_build. Returns the same as that one."""

    build_dir = tempfile.mkdtemp(prefix="test-build-", dir=os.environ['BUILDDIR'])

    def cleanup_test_build():
        if not pytest.config.getoption('--keep-build-dir'):
            run_verbose("rm -rf %s" % build_dir)

    cleanup_test_build()
    request.addfinalizer(cleanup_test_build)

    env_setup = "cd %s && . oe-init-build-env %s" % (bitbake_variables['COREBASE'], build_dir)

    run_verbose(env_setup)

    run_verbose("cp %s/conf/* %s/conf" % (os.environ['BUILDDIR'], build_dir))
    local_conf = os.path.join(build_dir, "conf", "local.conf")
    local_conf_orig = local_conf + ".orig"
    with open(local_conf, "a") as fd:
        fd.write('SSTATE_MIRRORS = " file://.* file://%s/sstate-cache/PATH"\n' % os.environ['BUILDDIR'])
    run_verbose("cp %s %s" % (local_conf, local_conf_orig))

    os.symlink(os.path.join(os.environ['BUILDDIR'], "downloads"), os.path.join(build_dir, "downloads"))

    image_name = pytest.config.getoption("--bitbake-image")

    return {'build_dir': build_dir,
            'image_name': image_name,
            'env_setup': env_setup,
            'local_conf': local_conf,
            'local_conf_orig': local_conf_orig,
    }


@pytest.fixture(scope="function")
def prepared_test_build(prepared_test_build_base):
    """Prepares a separate test build directory where a custom build can be
    made, which reuses the sstate-cache. Returns a dictionary with:
    - build_dir
    - image_name
    - env_setup (passed to some functions)
    - local_conf
    """

    reset_local_conf(prepared_test_build_base)

    return prepared_test_build_base



@pytest.fixture(autouse=True)
def min_mender_version(request, bitbake_variables):
    version_mark = request.node.get_marker("min_mender_version")
    if version_mark is None:
        pytest.fail(('%s must be marked with @pytest.mark.min_mender_version("<VERSION>") to '
                     + 'indicate lowest Mender version for which the test will work.')
                    % str(request.node))

    test_version = version_mark.args[0]
    mender_version = bitbake_variables.get('PREFERRED_VERSION_pn-mender')
    if mender_version is None:
        mender_version = bitbake_variables.get('PREFERRED_VERSION_mender')
    if mender_version is None:
        mender_version = "master"
    if LooseVersion(test_version) > LooseVersion(mender_version):
        pytest.skip("Test for Mender client %s and newer cannot run with Mender client %s"
                    % (test_version, mender_version))

@pytest.fixture(autouse=True)
def only_for_machine(request, bitbake_variables):
    """Fixture that enables use of `only_for_machine(machine-name)` mark.
    Example::

       @pytest.mark.only_for_machine('vexpress-qemu')
       def test_foo():
           # executes only if building for vexpress-qemu
           pass

    """
    mach_mark = request.node.get_marker('only_for_machine')
    if mach_mark is not None:
        machines = mach_mark.args
        current = bitbake_variables.get('MACHINE', None)
        if  current not in machines:
            pytest.skip('incompatible machine {} ' \
                        '(required {})'.format(current if not None else '(none)',
                                               ', '.join(machines)))


@pytest.fixture(autouse=True)
def only_with_image(request, bitbake_variables):
    """Fixture that enables use of `only_with_image(img1, img2)` mark.
    Example::

       @pytest.mark.only_with_image('ext4')
       def test_foo():
           # executes only if ext4 image is enabled
           pass

    """
    mark = request.node.get_marker('only_with_image')
    if mark is not None:
        images = mark.args
        current = bitbake_variables.get('IMAGE_FSTYPES', '').strip().split(' ')
        if not any([img in current for img in images]):
            pytest.skip('no supported filesystem in {} ' \
                        '(supports {})'.format(', '.join(current),
                                               ', '.join(images)))
