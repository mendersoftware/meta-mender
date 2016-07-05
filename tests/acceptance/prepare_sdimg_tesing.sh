#!/bin/bash
SRC_PATH=${1:-`pwd`"/core-image-base-beaglebone.sdimg"}
DST_PATH=${2:-`pwd`"/core-image-base-beaglebone-modified-testing.sdimg"}

# If the Beaglebone is stuck in U-boot, you want to flash to the sdcard with
# the image produced by this script and reboot.

function finish {
  umount -f /mnt/loopdev
}

cp ${SRC_PATH} ${DST_PATH}
PART_OFFSET=$(fdisk -l ${SRC_PATH} | grep core-image-base-beaglebone.sdimg2 | awk '{sum = $2 * 512; print sum}')
mkdir -p /mnt/loopdev >/dev/null
sudo mount -t ext3 -o loop,offset=${PART_OFFSET} ${DST_PATH} /mnt/loopdev
mkdir -p /mnt/loopdev/home/root/.ssh >/dev/null
cp  files/keys/* /mnt/loopdev/home/root/.ssh
chmod 400 /mnt/loopdev/home/root/.ssh/id_rsa*
cp  files/rssh.service /mnt/loopdev/etc/systemd/system/multi-user.target.wants/
trap finish EXIT
