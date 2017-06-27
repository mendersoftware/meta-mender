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

import pytest
import os
import re
import subprocess
import time
import tempfile
import errno
import shutil

import conftest

def if_not_bbb(func):
    def func_wrapper():
        if pytest.config.getoption("bbb"):
            return
        else:
            func()
    return func_wrapper


# Return Popen object
def start_qemu(latest_sdimg):
    if pytest.config.getoption("bbb"):
        return

    fh, img_path = tempfile.mkstemp(suffix=".sdimg", prefix="test-image")
    # don't need an open fd to temp file
    os.close(fh)

    # Make a disposable image.
    shutil.copy(latest_sdimg, img_path)

    env = dict(os.environ)
    # *.sdimg is supported by mender-qemu and needs no special handling
    env["VEXPRESS_IMG"] = img_path
    # use snapshot mode
    proc = subprocess.Popen(["../../meta-mender-qemu/scripts/mender-qemu", "-snapshot"], env=env)

    try:
        # make sure we are connected.
        execute(run_after_connect, "true", hosts = conftest.current_hosts())
        execute(qemu_prep_after_boot, hosts = conftest.current_hosts())
    except:
        # or do the necessary cleanup if we're not
        try:
            # qemu might have exited and this would raise an exception
            print('cleaning up qemu instance with pid {}'.format(proc.pid))
            proc.kill()
        except:
            pass

        proc.wait()

        os.remove(img_path)

        raise

    return proc, img_path


@if_not_bbb
def kill_qemu():
    os.system("pkill qemu-system-arm")
    time.sleep(1)
    try:
        os.remove("test-image.qcow2")
    except:
        pass

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
        sudo("reboot")

    # Make sure reboot has had time to take effect.
    time.sleep(5)

    fabric.network.disconnect_all()

    run_after_connect("true", wait = wait)

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
            except Exception as e:
                print("Could not connect to host %s: %s" % (env.host_string, e))
                if attempt_time >= start_time + wait:
                    raise Exception("Could not reconnect to QEMU")
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
        raise Exception("Could not determine active partition. Mount output: %s"
                        % mount_output)


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
    sudo("fw_setenv upgrade_available 0")
    sudo("fw_setenv bootcount 0")


def setup_bbb_sdcard():
    local_sdimg = pytest.config.getoption("--sdimg-location")
    put("core-image-base-beaglebone-modified-testing.sdimg",
        local_path=local_sdimg,
        remote_path="/opt/")
    sudo("chmod +x /root/install-new-image.sh")

    #easier to keep the followinf in a bash script
    sudo("/root/install-new-image.sh")
    reboot()


def boot_from_internal():
    bootline = """uenvcmd=load mmc 1:1 ${loadaddr} /boot/vmlinuz-4.1.18-ti-r56; \
                  load mmc 1:1 ${fdtaddr} /boot/dtbs/4.1.18-ti-r56/am335x-boneblack.dtb; \
                  setenv bootargs console=tty0 console=${console} root=/dev/mmcblk1p1; \
                  bootz ${loadaddr} - ${fdtaddr}"""

    if "yocto" in sudo("uname -a"):
        with settings(warn_only=True):
            sudo("sed '/uenvcmd/d' -i /uboot/uEnv.txt")
        append("/uboot/uEnv.txt", bootline)
        reboot()

@pytest.fixture(scope="session")
def setup_bbb(request):
    if pytest.config.getoption("--bbb"):
        execute(boot_from_internal)
        execute(setup_bbb_sdcard, host=conftest.current_hosts())

        def bbb_finalizer():
            def bbb_finalizer_impl():
                    execute(boot_from_internal)
            execute(bbb_finalizer_impl, hosts=conftest.current_hosts())

        request.addfinalizer(bbb_finalizer)

@pytest.fixture(scope="module")
def qemu_running(request, clean_image):
    if pytest.config.getoption("--bbb"):
        return

    latest_sdimg = latest_build_artifact(clean_image['build_dir'], ".sdimg")

    qemu, img_path = start_qemu(latest_sdimg)
    print("qemu started with pid {}, image {}".format(qemu.pid, img_path))

    # Make sure we revert to the first root partition on next reboot, makes test
    # cases more predictable.
    def qemu_finalizer():
        def qemu_finalizer_impl():
            try:
                manual_uboot_commit()
                sudo("halt")
                halt_time = time.time()
                # Wait up to 30 seconds for shutdown.
                while halt_time + 30 > time.time() and qemu.poll() is None:
                    time.sleep(1)
            except:
                # Nothing we can do about that.
                pass

            # kill qemu
            try:
                qemu.kill()
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
def no_image_file(qemu_running):
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
def latest_mender_image():
    assert(os.environ.get('BUILDDIR', False)), "BUILDDIR must be set"

    # Find latest built rootfs.
    return latest_build_artifact(os.environ['BUILDDIR'], ".mender")

@pytest.fixture(scope="function")
def successful_image_update_mender(request, latest_mender_image):
    """Provide a 'successful_image_update.mender' file in the current directory that
    contains the latest built update."""

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

def run_verbose(cmd):
    print(cmd)
    return subprocess.check_call(cmd, shell=True, executable="/bin/bash")

def run_bitbake(prepared_test_build):
    run_verbose("%s && bitbake %s" % (prepared_test_build['env_setup'],
                                      prepared_test_build['image_name']))


@pytest.fixture(scope="module")
def clean_image(request, prepared_test_build_base):
    add_to_local_conf(prepared_test_build_base,
                      'SYSTEMD_AUTO_ENABLE_pn-mender = "disable"')
    run_bitbake(prepared_test_build_base)
    return prepared_test_build_base


@pytest.fixture(scope="session")
def prepared_test_build_base(request, bitbake_variables):
    """Base fixture for prepared_test_build. Returns the same as that one."""

    build_dir = tempfile.mkdtemp(prefix="test-build-", dir=os.environ['BUILDDIR'])

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

    image_name = pytest.config.getoption("--bitbake-image")

    return {'build_dir': build_dir,
            'image_name': image_name,
            'env_setup': env_setup,
            'local_conf': local_conf
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
