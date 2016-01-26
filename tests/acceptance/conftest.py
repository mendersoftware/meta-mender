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

import unittest

import common

def pytest_addoption(parser):
    parser.addoption("--host", action = "store",
                     help = ("IP to connect to, with optional port. Defaults " +
                             "to localhost:8822, which is what the QEMU " +
                             "script sets up."))
    parser.addoption("--user", action = "store",
                     help = "user to log into remote hosts with (default is root)")


def pytest_configure(config):
    host = "localhost:8822"
    if config.getoption("host"):
        host = config.getoption("host")
    env.hosts = [host]

    env.user = "root"
    if config.getoption("user"):
        env.user = config.getoption("user")

    env.password = ""

    # Disable known_hosts file, to avoid "host identification changed" errors.
    env.disable_known_hosts = True

    env.abort_on_prompts = True


def pytest_unconfigure(config):
    common.kill_qemu()


def current_hosts():
    # Workaround for being inside/outside execute().
    if env.host_string:
        # Inside execute(), return current host.
        return [env.host_string]
    else:
        # Outside execute(), return the host(s) we want to run.
        return env.hosts
