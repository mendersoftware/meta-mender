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

from fabric.api import *
from fabric.contrib.files import append
import fabric.network

from distutils.version import LooseVersion
import pytest
import os
import re
import subprocess
import time
import tempfile
import errno
import shutil
import signal

from contextlib import contextmanager

import conftest

def if_not_bbb(func):
    def func_wrapper():
        if pytest.config.getoption("bbb"):
            return
        else:
            func()
    return func_wrapper


class ProcessGroupPopen(subprocess.Popen):
    """Wrapper for subprocess.Popen that starts the underlying process in a
    separate process group. The wrapper overrides kill() and terminate() so
    that the corresponding SIGKILL/SIGTERM are sent to the whole process group
    and not just the forked process.

    Note that ProcessGroupPopen() constructor hijacks preexec_fn parameter.

    """

    def __init__(self, *args, **kwargs):
        def start_new_session():
            os.setsid()
        # for Python > 3.2 it's enough to set start_new_session=True
        super(ProcessGroupPopen, self).__init__(*args,
                                                preexec_fn=start_new_session,
                                                **kwargs)

    def __signal(self, sig):
        os.killpg(self.pid, sig)

    def terminate(self):
        self.__signal(signal.SIGTERM)

    def kill(self):
        self.__signal(signal.SIGKILL)


def start_qemu(qenv=None):
    """Start qemu and return a subprocess.Popen object corresponding to a running
    qemu process. `qenv` is a dict of environment variables that will be added
    to `subprocess.Popen(..,env=)`.

    Once qemu is stated, a connection over ssh will attempted, so the returned
    process is actually a qemu instance with fully booted guest os.

    The helper uses `meta-mender-qemu/scripts/mender-qemu` to start qemu, thus
    you can use `VEXPRESS_IMG`, `QEMU_DRIVE` and other environment variables to
    override the default behavior.
    """
    env = dict(os.environ)
    if qenv:
        env.update(qenv)

    proc = ProcessGroupPopen(["../../meta-mender-qemu/scripts/mender-qemu", "-snapshot"],
                             env=env)

    try:
        # make sure we are connected.
        execute(run_after_connect, "true", hosts = conftest.current_hosts())
        execute(qemu_prep_after_boot, hosts = conftest.current_hosts())
    except:
        # or do the necessary cleanup if we're not
        try:
            # qemu might have exited and this would raise an exception
            print('cleaning up qemu instance with pid {}'.format(proc.pid))
            proc.terminate()
        except:
            pass

        proc.wait()

        raise

    return proc


def start_qemu_sdimg(latest_sdimg):
    """Start qemu instance running *.sdimg"""
    if pytest.config.getoption("bbb"):
        return

    fh, img_path = tempfile.mkstemp(suffix=".sdimg", prefix="test-image")
    # don't need an open fd to temp file
    os.close(fh)

    # Make a disposable image.
    shutil.copy(latest_sdimg, img_path)

    # pass QEMU drive directly
    qenv = {}
    qenv["VEXPRESS_IMG"] = img_path
    qenv["MACHNE"] = "vexpress-qemu"

    try:
        qemu = start_qemu(qenv)
    except:
        os.remove(img_path)
        raise

    return qemu, img_path


def start_qemu_flash(latest_vexpress_nor):
    """Start qemu instance running *.vexpress-nor image"""

    print("qemu raw flash with image {}".format(latest_vexpress_nor))

    # make a temp file, make sure that it has .vexpress-nor suffix, so that
    # mender-qemu will know how to handle it
    fh, img_path = tempfile.mkstemp(suffix=".vexpress-nor", prefix="test-image")
    # don't need an open fd to temp file
    os.close(fh)

    # vexpress-nor is more complex than sdimg, inside it's compose of 2 raw
    # files that represent 2 separate flash banks (and each file is a 'drive'
    # passed to qemu). Because of this, we cannot directly apply qemu-img and
    # create a qcow2 image with backing file. Instead make a disposable copy of
    # flash image file.
    shutil.copyfile(latest_vexpress_nor, img_path)

    qenv = {}
    # pass QEMU drive directly
    qenv["VEXPRESS_IMG"] = img_path
    qenv["MACHINE"] = "vexpress-qemu-flash"

    try:
        qemu = start_qemu(qenv)
    except:
        os.remove(img_path)
        raise

    return qemu, img_path


@if_not_bbb
def is_qemu_running():
    while True:
        proc = subprocess.Popen(["pgrep", "qemu"], stdout=subprocess.PIPE)
        assert(proc)
        try:
            if proc.stdout.readlines() == []:
                return False
            else:
                return True
        finally:
            proc.wait()


def reboot(wait = 120):
    with settings(warn_only = True):
        run("reboot")

    # Make sure reboot has had time to take effect.
    time.sleep(5)

    fabric.network.disconnect_all()

    run_after_connect("true", wait)

    qemu_prep_after_boot()


def run_after_connect(cmd, wait=360):
    output = ""
    start_time = time.time()

    with settings(timeout=30, abort_exception=Exception):
        while True:
            attempt_time = time.time()
            try:
                output = run(cmd)
                break
            except BaseException as e:
                print("Could not connect to host %s: %s" % (env.host_string, e))
                if attempt_time >= start_time + wait:
                    raise Exception("Could not reconnect to host")
                now = time.time()
                if now - attempt_time < 5:
                    time.sleep(60)
                continue
    return output


def ssh_prep_args():
    return ssh_prep_args_impl("ssh")


def scp_prep_args():
    return ssh_prep_args_impl("scp")


def ssh_prep_args_impl(tool):
    if not env.host_string:
        raise Exception("get()/put() called outside of execute()")

    cmd = ("%s -C -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null" %
           tool)

    host_parts = env.host_string.split(":")
    host = ""
    port = ""
    port_flag = "-p"
    if tool == "scp":
        port_flag = "-P"
    if len(host_parts) == 2:
        host = host_parts[0]
        port = "%s%s" % (port_flag, host_parts[1])
    elif len(host_parts) == 1:
        host = host_parts[0]
        port = ""
    else:
        raise Exception("Malformed host string")

    return (cmd, host, port)


def determine_active_passive_part(bitbake_variables):
    """Given the output from mount, determine the currently active and passive
    partitions, returning them as a pair in that order."""

    mount_output = run("mount")
    a = bitbake_variables["MENDER_ROOTFS_PART_A"]
    b = bitbake_variables["MENDER_ROOTFS_PART_B"]

    if mount_output.find(a) >= 0:
        return (a, b)
    elif mount_output.find(b) >= 0:
        return (b, a)
    else:
        raise Exception("Could not determine active partition. Mount output:\n {}" \
                        "\nwas looking for {}".format(mount_output, (a, b)))


# Yocto build SSH is lacking SFTP, let's override and use regular SCP instead.
def put(file, local_path = ".", remote_path = "."):
    (scp, host, port) = scp_prep_args()

    local("%s %s %s/%s %s@%s:%s" %
          (scp, port, local_path, file, env.user, host, remote_path))


# See comment for put().
def get(file, local_path = ".", remote_path = "."):
    (scp, host, port) = scp_prep_args()

    local("%s %s %s@%s:%s/%s %s" %
          (scp, port, env.user, host, remote_path, file, local_path))


def qemu_prep_after_boot():
    # Nothing needed ATM.
    pass


def qemu_prep_fresh_host():
    # Nothing needed ATM.
    pass


def manual_uboot_commit():
    run("fw_setenv upgrade_available 0")
    run("fw_setenv bootcount 0")


def setup_bbb_sdcard():
    local_sdimg = pytest.config.getoption("--sdimg-location")
    put("core-image-base-beaglebone-modified-testing.sdimg",
        local_path=local_sdimg,
        remote_path="/opt/")
    run("chmod +x /root/install-new-image.sh")

    #easier to keep the followinf in a bash script
    run("/root/install-new-image.sh")
    reboot()

def boot_from_internal():
    bootline = """uenvcmd=load mmc 1:1 ${loadaddr} /boot/vmlinuz-4.1.18-ti-r56; \
                  load mmc 1:1 ${fdtaddr} /boot/dtbs/4.1.18-ti-r56/am335x-boneblack.dtb; \
                  setenv bootargs console=tty0 console=${console} root=/dev/mmcblk1p1; \
                  bootz ${loadaddr} - ${fdtaddr}"""

    if "yocto" in run("uname -a"):
        with settings(warn_only=True):
            run("sed '/uenvcmd/d' -i /uboot/uEnv.txt")
        append("/uboot/uEnv.txt", bootline)
        reboot()

@pytest.fixture(scope="session")
def setup_board(request, clean_image, bitbake_variables):
    bt = pytest.config.getoption("--board-type")

    print('board type:', bt)
    if bt == "qemu":
        return qemu_running(request, clean_image)
    elif bt == "bbb":
        return setup_bbb(request)
    elif bt == "rpi3":
        return setup_rpi3(request)
    elif bt == "colibri-imx7":
        return setup_colibri_imx7(request, clean_image)
    else:
        pytest.fail('unsupported board type {}'.format(bt))


def common_board_setup(files=None, remote_path='/tmp', image_file=None):
    """
    Deploy and activate an image to a board that usese mender-qa tools.

    :param image_file: IMAGE_FILE as passed to deploy-test-image, can be None
    :param remote_path: where files will be stored in the remote system
    :param files: list of files to deploy
    """
    for f in files:
        put(os.path.basename(f), local_path=os.path.dirname(f),
            remote_path=remote_path)

    env_overrides = {}
    if image_file:
        env_overrides['IMAGE_FILE'] = image_file

    run("{} mender-qa deploy-test-image".format(' '.join(
        ['{}={}'.format(k, v) for k, v in env_overrides.items()])))

    with settings(warn_only=True):
        sudo("mender-qa activate-test-image")

def common_board_cleanup():
    with settings(warn_only=True):
        sudo("mender-qa activate-test-image off")

    execute(run_after_connect, "true", hosts = conftest.current_hosts())

def common_boot_from_internal():
    with settings(warn_only=True):
        sudo("mender-qa activate-test-image on")

    execute(run_after_connect, "true", hosts = conftest.current_hosts())

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
    if pytest.config.getoption("--bbb"):
        return

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

def latest_build_artifact(builddir, extension):
    output = subprocess.check_output(["sh", "-c", "ls -t %s/tmp*/deploy/images/*/*%s | head -n 1" % (builddir, extension)])
    output = output.rstrip('\r\n')
    print("Found latest image of type '%s' to be: %s" % (extension, output))
    return output

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

def get_bitbake_variables(target, env_setup="true"):
    current_dir = os.open(".", os.O_RDONLY)
    os.chdir(os.environ['BUILDDIR'])

    output = subprocess.Popen("%s && bitbake -e %s" % (env_setup, target),
                              stdout=subprocess.PIPE,
                              shell=True,
                              executable="/bin/bash")
    matcher = re.compile('^(?:export )?([A-Za-z][^=]*)="(.*)"$')
    ret = {}
    for line in output.stdout:
        line = line.strip()
        match = matcher.match(line)
        if match is not None:
            ret[match.group(1)] = match.group(2)

    output.wait()
    os.fchdir(current_dir)

    # For some unknown reason, 'MACHINE' is not included in the above list. Add
    # it automagically by looking in environment and local.conf, in that order,
    # if it doesn't exist already.
    if ret.get('MACHINE') is None:
        if os.environ.get('MACHINE'):
            ret['MACHINE'] = os.environ.get('MACHINE')
        else:
            local_fd = open(os.path.join(os.environ['BUILDDIR'], "conf", "local.conf"))
            for line in local_fd:
                match = re.match('^ *MACHINE *\?*= *"([^"]*)" *$', line)
                if match is not None:
                    ret['MACHINE'] = match.group(1)
            local_fd.close()

    return ret

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

def signing_key(key_type):
    # RSA pregenerated using these.
    #   openssl genrsa -out files/test-private-RSA.pem 2048
    #   openssl rsa -in files/test-private-RSA.pem -outform PEM -pubout -out files/test-public-RSA.pem

    # EC pregenerated using these.
    #   openssl ecparam -genkey -name prime256v1 -out /tmp/private-and-params.pem
    #   openssl ec -in /tmp/private-and-params.pem -out files/test-private-EC.pem
    #   openssl ec -in files/test-private-EC.pem -pubout -out files/test-public-EC.pem

    class KeyPair:
        if key_type == "EC":
            private = "files/test-private-EC.pem"
            public = "files/test-public-EC.pem"
        else:
            private = "files/test-private-RSA.pem"
            public = "files/test-public-RSA.pem"

    return KeyPair()

def run_verbose(cmd, capture=False):
    if capture:
        print("subprocess.check_output(\"%s\")" % cmd)
        return subprocess.check_output(cmd, shell=True, executable="/bin/bash",
                                       stderr=subprocess.STDOUT)
    else:
        print(cmd)
        return subprocess.check_call(cmd, shell=True, executable="/bin/bash")

def run_bitbake(prepared_test_build, target=None, capture=False):
    if target is None:
        target = prepared_test_build['image_name']
    run_verbose("%s && bitbake %s" % (prepared_test_build['env_setup'],
                                      target),
                capture=capture)


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


def add_to_local_conf(prepared_test_build, string):
    """Add given string to local.conf before the build. Newline is added
    automatically."""

    with open(prepared_test_build['local_conf'], "a") as fd:
        fd.write('\n## ADDED BY TEST\n')
        fd.write("%s\n" % string)

def reset_local_conf(prepared_test_build):
    new_file = prepared_test_build['local_conf']
    old_file = prepared_test_build['local_conf_orig']

    # Restore original local.conf
    run_verbose("cp %s %s" % (old_file, new_file))



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

def versions_of_recipe(recipe):
    """Returns a list of all the versions we have of the given recipe, excluding
    git recipes."""

    versions = []
    for entry in os.listdir("../../meta-mender-core/recipes-mender/%s/" % recipe):
        match = re.match(r"^%s_([1-9][0-9]*\.[0-9]+\.[0-9]+[^.]*)\.bb" % recipe, entry)
        if match is not None:
            versions.append(match.group(1))
    return versions

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


@contextmanager
def make_tempdir(delete=True):
    """context manager for temporary directories"""
    tdir = tempfile.mkdtemp(prefix='meta-mender-acceptance.')
    print('created dir', tdir)
    try:
        yield tdir
    finally:
        if delete:
            shutil.rmtree(tdir)
