#!/usr/bin/python

#Fabric file to copy over needed files to the BBB's internal system
from fabric.api import put, sudo, settings, env


def setup_internal_bbb_os():
    env.user = "root"
    env.password = ""

    with settings(warn_only=True):
        sudo("mkdir /root/.ssh &>/dev/null")

    put("install-new-image.sh", remote_path="/root/")
    put(local_path="keys/*", remote_path="/root/.ssh/", mode=0600)
    put("rssh.service", "/lib/systemd/system/")
    sudo("systemctl enable rssh.service")
    sudo("systemctl start rssh.service")
