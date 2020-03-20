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

from fabric import Connection
from paramiko import SSHException
from paramiko.ssh_exception import NoValidConnectionsError

from distutils.version import LooseVersion
import pytest
import os
import re
import subprocess
import time
import tempfile
import shutil
import signal
import sys

from contextlib import contextmanager
import traceback


# ugly hack to access cli parameters inside common.py functions
configuration = {}


def start_qemu(qenv=None, conn=None):
    """Start QEMU and return a subprocess.Popen object corresponding to a running
    qemu process. `qenv` is a dict of environment variables that will be added
    to `subprocess.Popen(..,env=)`.

    Once qemu is started, a connection over ssh will attempted, so the returned
    process is actually a QEMU instance with a fully booted guest OS.

    The helper uses `meta-mender-qemu/scripts/mender-qemu` to start qemu, thus
    you can use `VEXPRESS_IMG`, `QEMU_DRIVE` and other environment variables to
    override the default behavior.
    """
    env = dict(os.environ)
    if qenv:
        env.update(qenv)

    proc = subprocess.Popen(
        ["../../meta-mender-qemu/scripts/mender-qemu", "-snapshot"],
        env=env,
        start_new_session=True,
    )

    try:
        # make sure we are connected.
        run_after_connect("true", conn)
    except:
        # or do the necessary cleanup if we're not
        try:
            # qemu might have exited and this would raise an exception
            print("cleaning up qemu instance with pid {}".format(proc.pid))
            proc.terminate()
        except:
            pass

        proc.wait()
        raise

    return proc


def start_qemu_block_storage(latest_sdimg, suffix, conn):
    """Start qemu instance running block storage"""
    fh, img_path = tempfile.mkstemp(suffix=suffix, prefix="test-image")
    # don't need an open fd to temp file
    os.close(fh)

    # Make a disposable image.
    shutil.copy(latest_sdimg, img_path)

    # pass QEMU drive directly
    qenv = {}
    qenv["DISK_IMG"] = img_path

    try:
        qemu = start_qemu(qenv, conn)
    except:
        os.remove(img_path)
        raise

    return qemu, img_path


def start_qemu_flash(latest_vexpress_nor, conn):
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
    qenv["DISK_IMG"] = img_path
    qenv["MACHINE"] = "vexpress-qemu-flash"

    try:
        qemu = start_qemu(qenv, conn)
    except:
        os.remove(img_path)
        raise

    return qemu, img_path


def reboot(conn, wait=120):
    try:
        conn.run("reboot", warn=True)
    except:
        # qemux86-64 is so fast that sometimes the above call fails with
        # an exception because the connection was broken before we returned.
        # So catch everything, even though it might hide real errors (but
        # those will probably be caught below after the timeout).
        pass

    # Make sure reboot has had time to take effect.
    time.sleep(5)

    for attempt in range(5):
        try:
            conn.close()
            break
        except IOError:
            # Occasionally we get an IO error here because resource is temporarily
            # unavailable.
            time.sleep(5)
            continue

    run_after_connect("true", conn, wait=wait)


def run_after_connect(cmd, conn, wait=360):
    # override the Connection parameters
    orig_timeout = conn.connect_timeout
    conn.connect_timeout = 60
    timeout = time.time() + 60 * 3

    while time.time() < timeout:
        try:
            print("will try to connect to host", conn.host)
            result = conn.run(cmd, hide=True)
            return result.stdout
        except NoValidConnectionsError as e:
            print("Could not connect to host %s: %s" % (conn.host, e))
            time.sleep(30)
            continue
        except SSHException as e:
            print("Got SSH exception while connecting to host %s: %s" % (conn.host, e))
            if not (
                "Connection reset by peer" in str(e)
                or "Error reading SSH protocol banner" in str(e)
                or "No existing session" in str(e)
            ):
                raise e
            time.sleep(30)
            continue
        except OSError as e:
            # The OSError is happening while there is no QEMU instance initialized
            print(
                "Got OSError exception while connecting to host %s: %s" % (conn.host, e)
            )
            if not "Cannot assign requested address" in str(e):
                raise e
            time.sleep(30)
            continue
        except Exception as e:
            print(
                "Generic exception happened while connecting to host %s: %s"
                % (conn.host, e)
            )
            print(type(e))
            print(e.args)
            raise e
        finally:
            # Restore the original connection parameters
            conn.connect_timeout = orig_timeout


def determine_active_passive_part(bitbake_variables, conn):
    """Given the output from mount, determine the currently active and passive
    partitions, returning them as a pair in that order."""

    mount_output = conn.run("mount").stdout
    a = bitbake_variables["MENDER_ROOTFS_PART_A"]
    b = bitbake_variables["MENDER_ROOTFS_PART_B"]

    if mount_output.find(a) >= 0:
        return (a, b)
    elif mount_output.find(b) >= 0:
        return (b, a)
    else:
        raise Exception(
            "Could not determine active partition. Mount output:\n {}"
            "\nwas looking for {}".format(mount_output, (a, b))
        )


def get_ssh_common_args():
    return "-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null"


# Yocto build SSH is lacking SFTP, let's override and use regular SCP instead.
def put_no_sftp(file, conn, remote="."):
    cmd = "scp -C %s" % get_ssh_common_args()

    try:
        conn.local(
            "%s -P %s %s %s@%s:%s"
            % (cmd, conn.port, file, conn.user, conn.host, remote)
        )
    except Exception as e:
        print("exception while putting file: ", e)
        raise e


# Yocto build SSH is lacking SFTP, let's override and use regular SCP instead.
def get_no_sftp(file, conn, local="."):
    cmd = "scp -C %s" % get_ssh_common_args()
    conn.local(
        "%s -P %s %s@%s:%s %s" % (cmd, conn.port, conn.user, conn.host, file, local)
    )


def manual_uboot_commit(conn):
    conn.run("fw_setenv upgrade_available 0")
    conn.run("fw_setenv bootcount 0")


def common_board_setup(conn, files=None, remote_path="/tmp", image_file=None):
    """
    Deploy and activate an image to a board that uses mender-qa tools.

    :param image_file: IMAGE_FILE as passed to deploy-test-image, can be None
    :param remote_path: where files will be stored in the remote system
    :param files: list of files to deploy
    """
    for f in files:
        put_no_sftp(
            os.path.basename(f),
            conn,
            remote=os.path.join(remote_path, os.path.basename(f)),
        )

    env_overrides = {}
    if image_file:
        env_overrides["IMAGE_FILE"] = image_file

    conn.run(
        "{} mender-qa deploy-test-image".format(
            " ".join(["{}={}".format(k, v) for k, v in env_overrides.items()])
        )
    )

    conn.sudo("mender-qa activate-test-image")


def common_board_cleanup(conn):
    conn.sudo("mender-qa activate-test-image off")
    conn.sudo("reboot", warn=True)

    run_after_connect("true", conn)


def common_boot_from_internal(conn):
    conn.sudo("mender-qa activate-test-image on")
    conn.sudo("reboot", warn=True)

    run_after_connect("true", conn)


def latest_build_artifact(builddir, extension, sdimg_location=None):
    global configuration

    # Force the builddir to be an absolute path
    builddir = os.path.abspath(builddir)

    if configuration.get("conversion"):
        output = subprocess.check_output(
            [
                "sh",
                "-c",
                "ls -t %s/*%s | grep -v data*%s| head -n 1"
                % (builddir, extension, extension),
            ]
        )
    else:
        output = subprocess.check_output(
            [
                "sh",
                "-c",
                "ls -t %s/tmp*/deploy/images/*/*%s | grep -v data*%s| head -n 1"
                % (builddir, extension, extension),
            ]
        )
    output = output.decode().rstrip("\r\n")
    print("Found latest image of type '%s' to be: %s" % (extension, output))
    return output


def get_bitbake_variables(target, env_setup="true", export_only=False):
    global configuration
    lines = []

    if configuration.get("conversion"):
        config_file_path = os.path.abspath(configuration["test_variables"])
        with open(config_file_path, "r") as config:
            lines = config.readlines()
    else:
        current_dir = os.open(".", os.O_RDONLY)
        os.chdir(os.environ["BUILDDIR"])
        ps = subprocess.Popen(
            "%s && bitbake -e %s" % (env_setup, target),
            stdout=subprocess.PIPE,
            shell=True,
            executable="/bin/bash",
        )
        os.fchdir(current_dir)

        while True:
            line = ps.stdout.readline()
            if not line:
                break
            lines.append(line.decode())

        ps.wait()

    if export_only:
        export_only_expr = ""
    else:
        export_only_expr = "?"
    matcher = re.compile('^(?:export )%s([A-Za-z][^=]*)="(.*)"$' % export_only_expr)
    ret = {}
    for line in lines:
        line = line.strip()
        match = matcher.match(line)
        if match is not None:
            ret[match.group(1)] = match.group(2)

    # For some unknown reason, 'MACHINE' is not included in the 'bitbake -e' output.
    # We set MENDER_MACHINE in mender-setup.bbclass as a proxy so look for that instead.
    if ret.get("MACHINE") is None:
        if ret.get("MENDER_MACHINE") is not None:
            ret["MACHINE"] = ret.get("MENDER_MACHINE")
        else:
            raise Exception("Could not determine MACHINE or MENDER_MACHINE value.")

    return ret


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


# `capture` can be a bool, meaning the captured output is returned, or a stream,
# in which case the output is redirected there, and the process handle is
# returned instead.
def run_verbose(cmd, capture=False):
    if type(capture) is not bool:
        print('subprocess.Popen("%s")' % cmd)
        return subprocess.Popen(
            cmd,
            shell=True,
            executable="/bin/bash",
            stderr=subprocess.STDOUT,
            stdout=capture,
        )
    elif capture:
        print('subprocess.check_output("%s")' % cmd)
        return subprocess.check_output(
            cmd, shell=True, executable="/bin/bash", stderr=subprocess.STDOUT
        )
    else:
        print(cmd)
        return subprocess.check_call(cmd, shell=True, executable="/bin/bash")


# Capture is true or false and conditonally returns output.
def build_image(
    build_dir,
    bitbake_corebase,
    bitbake_image,
    extra_conf_params=None,
    extra_bblayers=None,
    target=None,
    capture=False,
):
    for param in extra_conf_params or []:
        _add_to_local_conf(build_dir, param)

    for layer in extra_bblayers or []:
        _add_to_bblayers_conf(build_dir, layer)

    init_env_cmd = "cd %s && . oe-init-build-env %s" % (bitbake_corebase, build_dir)

    if target:
        _run_bitbake(target, init_env_cmd, capture)
    else:
        _run_bitbake(bitbake_image, init_env_cmd, capture)


def _run_bitbake(target, env_setup_cmd, capture=False):
    cmd = "%s && bitbake %s" % (env_setup_cmd, target)
    ps = run_verbose(cmd, capture=subprocess.PIPE)
    output = ""
    try:
        # Cannot use for loop here due to buffering and iterators.
        while True:
            line = ps.stdout.readline().decode()
            if not line:
                break

            if line.find("is not a recognized MENDER_ variable") >= 0:
                pytest.fail(
                    "Found variable which is not in mender-vars.json: %s" % line.strip()
                )

            if capture:
                output += line
            else:
                sys.stdout.write(line)
    finally:
        # Empty any remaining lines.
        try:
            if capture:
                output += ps.stdout.readlines().decode()
            else:
                ps.stdout.readlines()
        except:
            pass
        ps.wait()
        if ps.returncode != 0:
            e = subprocess.CalledProcessError(ps.returncode, cmd)
            if capture:
                e.output = output
            raise e

    return output


# Make sure we are constructing the paths the same way always
def get_local_conf_path(build_dir):
    return os.path.join(build_dir, "conf", "local.conf")


def get_local_conf_orig_path(build_dir):
    return os.path.join(build_dir, "conf", "local.conf.orig")


def get_bblayers_conf_path(build_dir):
    return os.path.join(build_dir, "conf", "bblayers.conf")


def get_bblayers_conf_orig_path(build_dir):
    return os.path.join(build_dir, "conf", "bblayers.conf.orig")


def _add_to_local_conf(build_dir, string):
    """Add given string to local.conf before the build. Newline is added
    automatically."""
    with open(os.path.join(build_dir, "conf", "local.conf"), "a") as fd:
        fd.write("\n## ADDED BY TEST\n")
        fd.write("%s\n" % string)


def _add_to_bblayers_conf(build_dir, string):
    """Add given string to bblayers.conf before the build. Newline is added
    automatically."""
    with open(os.path.join(build_dir, "conf", "bblayers.conf"), "a") as fd:
        fd.write("\n## ADDED BY TEST\n")
        fd.write("%s\n" % string)


def reset_build_conf(build_dir, full_cleanup=False):
    # Restore original build configuration
    for conf in ["local", "bblayers"]:
        new_file = os.path.join(build_dir, "conf", conf + ".conf")
        old_file = new_file + ".orig"

        if os.path.exists(old_file):
            run_verbose("cp %s %s" % (old_file, new_file))
            if full_cleanup:
                os.remove(old_file)


class bitbake_env_from:
    old_env = {}
    old_path = None
    recipe = None

    def __init__(self, recipe):
        self.recipe = recipe

    def __enter__(self):
        self.setup()

    def setup(self):
        if isinstance(self.recipe, str):
            vars = get_bitbake_variables(self.recipe, export_only=True)
        else:
            vars = self.recipe

        self.old_env = {}
        # Save all values that have keys in the bitbake_env_dict
        for key in vars:
            if key in os.environ:
                self.old_env[key] = os.environ[key]
            else:
                self.old_env[key] = None

        self.old_path = os.environ["PATH"]

        os.environ.update(vars)
        # Exception for PATH, keep old path at end.
        os.environ["PATH"] += ":" + self.old_path

        return os.environ

    def __exit__(self, type, value, traceback):
        self.teardown()

    def teardown(self):
        # Restore all keys we saved.
        for key in self.old_env:
            if self.old_env[key] is None:
                del os.environ[key]
            else:
                os.environ[key] = self.old_env[key]


def versions_of_recipe(recipe):
    """Returns a list of all the versions we have of the given recipe, excluding
    git recipes."""

    versions = []
    for entry in os.listdir("../../meta-mender-core/recipes-mender/%s/" % recipe):
        match = re.match(r"^%s_([1-9][0-9]*\.[0-9]+\.[0-9]+[^.]*)\.bb" % recipe, entry)
        if match is not None:
            versions.append(match.group(1))
    return versions


def version_is_minimum(bitbake_variables, component, min_version):
    version = bitbake_variables.get("PREFERRED_VERSION_pn-%s" % component)
    if version is None:
        version = bitbake_variables.get("PREFERRED_VERSION_%s" % component)
    if version is None:
        version = "master"

    try:
        if LooseVersion(min_version) > LooseVersion(version):
            return False
        else:
            return True
    except TypeError:
        # Type error indicates that 'version' is likely a string (branch
        # name). For now we just default to always consider them higher than the
        # minimum version.
        return True


@contextmanager
def make_tempdir(delete=True):
    """context manager for temporary directories"""
    tdir = tempfile.mkdtemp(prefix="meta-mender-acceptance.")
    print("created dir", tdir)
    try:
        yield tdir
    finally:
        if delete:
            shutil.rmtree(tdir)
