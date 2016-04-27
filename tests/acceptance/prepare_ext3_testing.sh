#!/bin/bash

SRC_PATH=${1:-"/home/jenkins/workspace/yoctobuild/build/tmp/deploy/images/beaglebone/core-image-base-beaglebone.ext3"}
DST_PATH=${2:-`pwd`"/core-image-base-beaglebone-modified-testing.ext3"}

cp ${SRC_PATH} ${DST_PATH}


if [ ! `ls files/keys/id_rsa* | wc -l` -eq 2 ];
  then
    echo "ssh keys not found" 1>&2
    exit 1
fi

e2cp -P 400 files/keys/{id_rsa,id_rsa.pub} ${DST_PATH}:/home/root/.ssh/
e2cp files/rssh.service ${DST_PATH}:/etc/systemd/system/multi-user.target.wants/
echo "linking image.dat to ${DST_PATH}"
ln -s -f ${DST_PATH} `dirname ${DST_PATH}`/image.dat
