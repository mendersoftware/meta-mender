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
from fabric.contrib.files import append
import fabric.network

import pytest
import os
import re
import subprocess
import time
import conftest

def if_not_bbb(func):
    def func_wrapper():
        if pytest.config.getoption("bbb"):
            return
        else:
            func()
    return func_wrapper


# Return Popen object
@if_not_bbb
def start_qemu():
    proc = subprocess.Popen("../../meta-mender-qemu/scripts/mender-qemu")
    # Make sure we are connected.
    execute(run_after_connect, "true", hosts = conftest.current_hosts())
    execute(qemu_prep_after_boot, hosts = conftest.current_hosts())
    return proc

@if_not_bbb
def kill_qemu():
    os.system("pkill qemu-system-arm")
    time.sleep(1)

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


def run_after_connect(cmd, wait = 120):
    output = ""
    start_time = time.time()
    # Use shorter timeout to get a faster cycle.
    with settings(timeout = 5, abort_exception = Exception):
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
                    time.sleep(5 - (now - attempt_time))
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
def qemu_running(request):
    if pytest.config.getoption("--bbb"):
        return

    kill_qemu()

    # Make sure we revert to the first root partition on next reboot, makes test
    # cases more predictable.
    def qemu_finalizer():
        def qemu_finalizer_impl():
            try:
                manual_uboot_commit()
                sudo("halt")
                halt_time = time.time()
                # Wait up to 30 seconds for shutdown.
                while halt_time + 30 > time.time() and is_qemu_running():
                    time.sleep(1)
            except:
                # Nothing we can do about that.
                pass
            kill_qemu()
        execute(qemu_finalizer_impl, hosts=conftest.current_hosts())

    request.addfinalizer(qemu_finalizer)

    start_qemu()
    execute(qemu_prep_fresh_host, hosts=conftest.current_hosts())


@pytest.fixture(scope="function")
def no_image_file(qemu_running):
    """Make sure 'image.dat' is not present on the device."""
    execute(no_image_file_impl, hosts=conftest.current_hosts())


def no_image_file_impl():
    run("rm -f image.dat")

def latest_build_artifact(extension):
    if not os.environ.get('BUILDDIR', False):
        raise Exception("BUILDDIR needs to be defined")

    output = subprocess.check_output(["sh", "-c", "ls -t $BUILDDIR/tmp*/deploy/images/*/*%s | head -n 1" % extension])
    output = output.rstrip('\r\n')
    print("Found latest image of type '%s' to be: %s" % (extension, output))
    return output

@pytest.fixture(scope="session")
def latest_rootfs():
    # Find latest built rootfs.
    return latest_build_artifact(".ext[234]")

@pytest.fixture(scope="session")
def latest_sdimg():
    # Find latest built rootfs.
    return latest_build_artifact(".sdimg")

@pytest.fixture(scope="session")
def latest_mender_image():
    # Find latest built rootfs.
    return latest_build_artifact(".mender")

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

@pytest.fixture(scope="session")
def bitbake_variables():
    """Returns a map of all bitbake variables active for the build."""

    assert(os.environ.get('BUILDDIR', False)), "BUILDDIR must be set"

    current_dir = os.open(".", os.O_RDONLY)
    os.chdir(os.environ['BUILDDIR'])

    output = subprocess.Popen(["bitbake", "-e", "core-image-minimal"], stdout=subprocess.PIPE)
    matcher = re.compile('^(?:export )?([A-Za-z][^=]*)="(.*)"$')
    ret = {}
    for line in output.stdout:
        line = line.strip()
        match = matcher.match(line)
        if match is not None:
            ret[match.group(1)] = match.group(2)

    output.wait()
    os.fchdir(current_dir)

    return ret

@pytest.fixture(scope="function")
def bitbake_path(request, bitbake_variables):
    """Fixture that enables the same PATH as bitbake does when it builds for the
    test that invokes it."""

    old_path = os.environ['PATH']

    os.environ['PATH'] = bitbake_variables['PATH']

    def path_restore():
        os.environ['PATH'] = old_path

    request.addfinalizer(path_restore)

    return os.environ['PATH']
