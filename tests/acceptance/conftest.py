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
    parser.addoption("--keep-build-dir", action="store_true", default=False,
                     help="do not remove Yocto build directory after each test")
    parser.addoption("--board-type", action="store", default='qemu',
                     help="type of board to use in testing, supported types: qemu, bbb, colibri-imx7")
    parser.addoption("--use-s3", action="store_true", default=False,
                     help="use S3 for transferring images under test to target boards")
    parser.addoption("--s3-address", action="store", default="s3.amazonaws.com",
                     help="address of S3 server, defaults to AWS, override when using minio")


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


def current_hosts():
    # Workaround for being inside/outside execute().
    if env.host_string:
        # Inside execute(), return current host.
        return [env.host_string]
    else:
        # Outside execute(), return the host(s) we want to run.
        return env.hosts
