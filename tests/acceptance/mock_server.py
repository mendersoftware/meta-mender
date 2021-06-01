#!/usr/bin/python
# Copyright 2021 Northern.tech AS
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
import pytest
import tempfile

from utils.common import put_no_sftp

EXPIRATION_TIME = 30
BOOT_EXPIRATION_TIME = 15

MENDER_CONF = """{
    "UpdatePollIntervalSeconds": 1,
    "InventoryPollIntervalSeconds": 5,
    "RetryPollIntervalSeconds": 1,
    "UpdateControlMapExpirationTimeSeconds": %d,
    "UpdateControlMapBootExpirationTimeSeconds": %d,
    "ServerURL": "https://docker.mender.io:8443",
    "DBus": {
        "Enabled": true
    }
}
""" % (
    EXPIRATION_TIME,
    BOOT_EXPIRATION_TIME,
)


@pytest.fixture(scope="function")
def setup_mock_server(request, bitbake_variables, connection):
    conffile = "/data/etc/mender/mender.conf"
    conffile_bkp = f"{conffile}.backup"
    bdir = os.path.dirname(conffile_bkp)
    result = connection.run(
        f"mkdir -p {bdir} && if [ -e {conffile} ]; then cp {conffile} {conffile_bkp}; fi"
    )

    tf = tempfile.NamedTemporaryFile()
    with open(tf.name, "w") as fd:
        fd.write(MENDER_CONF)

    put_no_sftp(tf.name, connection, remote=conffile)

    hostsfile = "/data/etc/hosts"
    hostsfile_bkp = f"{hostsfile}.backup"
    connection.run(
        f"cp {hostsfile} {hostsfile_bkp} && echo 127.0.0.1 docker.mender.io >> {hostsfile}"
    )

    def fin():
        connection.run(
            f"if [ -e {conffile_bkp} ]; then dd if={conffile_bkp} of=$(realpath {conffile}); fi"
        )
        connection.run(
            f"if [ -e {hostsfile_bkp} ]; then dd if={hostsfile_bkp} of=$(realpath {hostsfile}); fi"
        )

    request.addfinalizer(fin)


def prepare_deployment_response(
    connection,
    artifact_file,
    device_type,
    deployment_id="test-deployment",
    artifact_name="test-artifact",
):
    with tempfile.NamedTemporaryFile() as fd:
        fd.write(
            b"""{
  "id": "%s",
  "artifact": {
    "source": {
      "uri": "https://docker.mender.io:8443/data/%s",
      "expire": "2099-01-01T00:00:00.000+0000"
    },
        "device_types_compatible": ["%s"],
    "artifact_name": "%s"
  }
}"""
            % (
                deployment_id.encode(),
                os.path.basename(artifact_file).encode(),
                device_type.encode(),
                artifact_name.encode(),
            )
        )
        fd.flush()

        put_no_sftp(
            artifact_file,
            connection,
            remote=os.path.join("/data", os.path.basename(artifact_file)),
        )
        put_no_sftp(
            fd.name,
            connection,
            remote="/data/mender-mock-server-deployment-header.json",
        )


def cleanup_deployment_response(connection):
    connection.run("rm -f /data/mender-mock-server-deployment-header.json")
