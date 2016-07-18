#!/bin/bash

SRC_PATH=${1:-"$WORKSPACE/build/tmp/deploy/images/beaglebone/core-image-base-beaglebone.ext3"}
DST_PATH=${2:-`pwd`"/core-image-base-beaglebone-modified-testing.ext3"}

cp ${SRC_PATH} ${DST_PATH}


# These files are found inside the tests/acceptance/files/keys/*.gpg archive.
# However, since it is needed for all workspaces, and we don't want to extract
# them for each and every one, they should be extracted in $HOME/files/keys,
# where they will be picked up.
if [ ! `ls $HOME/files/keys/id_rsa* | wc -l` -eq 2 ];
  then
    echo "ssh keys not found" 1>&2
    exit 1
fi

e2cp -P 400 $HOME/files/keys/{id_rsa,id_rsa.pub} ${DST_PATH}:/home/root/.ssh/
e2cp files/rssh.service ${DST_PATH}:/etc/systemd/system/multi-user.target.wants/
echo "linking image.dat to ${DST_PATH}"
ln -s -f ${DST_PATH} `dirname ${DST_PATH}`/image.dat
