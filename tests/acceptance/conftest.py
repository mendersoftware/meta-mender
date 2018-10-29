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

import os
import os.path
import subprocess

from fabric.api import *

import unittest

from fixtures import *


def pytest_addoption(parser):
    parser.addoption("--host", action="store", default="localhost:8822",
                     help="""IP to connect to, with optional port. Defaults
                     to localhost:8822, which is what the QEMU script sets up.""")
    parser.addoption("--user", action="store", default="root",
                     help="user to log into remote hosts with (default is root)")
    parser.addoption("--http-server", action="store", default="10.0.2.2:8000",
                     help="Remote HTTP server containing update image")
    parser.addoption("--sdimg-location", action="store",
                     default=os.getcwd(),
                     help="location to the sdimg you want to install on the bbb")
    parser.addoption("--bitbake-image", action="store",
                     default='core-image-full-cmdline',
                     help="image to build during the tests")
    parser.addoption("--no-tmp-build-dir", action="store_true", default=False,
                     help="Do not use a temporary build directory. Faster, but may mess with your build directory.")
    parser.addoption("--no-pull", action="store_true", default=False,
                     help="Do not pull submodules. Handy if debugging something locally.")
    parser.addoption("--board-type", action="store", default='qemu',
                     help="type of board to use in testing, supported types: qemu, bbb, colibri-imx7")
    parser.addoption("--use-s3", action="store_true", default=False,
                     help="use S3 for transferring images under test to target boards")
    parser.addoption("--s3-address", action="store", default="s3.amazonaws.com",
                     help="address of S3 server, defaults to AWS, override when using minio")
    parser.addoption("--test-conversion", action="store_true", default=False,
                     help="""conduct testing of .sdimg image built with mender-convert tool""")
    parser.addoption("--test-variables", action="store", default="default",
                     help="configuration file holding settings for dedicated platform")
    parser.addoption("--mender-image", action="store", default="default",
                     help="Mender compliant raw disk image")


def pytest_configure(config):
    env.hosts = config.getoption("host")
    env.user = config.getoption("user")

    env.password = ""

    # Bash not always available, nor currently required:
    env.shell = "/bin/sh -c"

    # Disable known_hosts file, to avoid "host identification changed" errors.
    env.disable_known_hosts = True

    env.abort_on_prompts = True

    # Don't allocate pseudo-TTY by default, since it is not fully functional.
    # It can still be overriden on a case by case basis by passing
    # "pty = True/False" to the various fabric functions. See
    # http://www.fabfile.org/faq.html about init scripts.
    env.always_use_pty = False

    # Don't combine stderr with stdout. The login profile sometimes prints
    # terminal specific codes there, and we don't want it interfering with our
    # output. It can still be turned on on a case by case basis by passing
    # combine_stderr to each run() or sudo() command.
    env.combine_stderr = False

    env.connection_attempts = 10
    env.timeout = 30

    if not config.getoption("--no-pull"):
        print("Automatically pulling submodules. Use --no-pull to disable")
        subprocess.check_call("git submodule update --init --remote", shell=True)


def current_hosts():
    # Workaround for being inside/outside execute().
    if env.host_string:
        # Inside execute(), return current host.
        return [env.host_string]
    else:
        # Outside execute(), return the host(s) we want to run.
        return env.hosts
