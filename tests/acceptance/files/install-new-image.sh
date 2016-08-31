#!/bin/bash

# This script will install the sdimg onto the sdcard
# and prepare it for testing (adding keys, rssh servce)

# It should be placed in the home directory of the BBBs internal OS

IMAGE="/opt/core-image-base-beaglebone-modified-testing.sdimg"
SDCARD=""

function modify_sdimg {
  PART_OFFSET=$(fdisk -l $IMAGE | grep core-image-base-beaglebone-modified-testing.sdimg2 | awk '{sum = $2 * 512; print sum}')
  mkdir /mnt/sdimg 2>/dev/null
  mount -t ext4 \
        -o loop,offset="$PART_OFFSET" \
        $IMAGE /mnt/sdimg

  if [ $? -ne 0 ];
    then
      echo "Unable to mount mender sdimg!" 1>&2
      exit 1
    fi

  mkdir -p /mnt/sdimg/home/root/.ssh
  cp  /root/.ssh/* /mnt/sdimg/home/root/.ssh

  cp  /lib/systemd/system/rssh.service \
      /mnt/sdimg/etc/systemd/system/multi-user.target.wants/rssh.service

  (cd /tmp && sync && umount /mnt/sdimg)
}


function unmount_sdcard {
  MOUNTED_SD_PART=( $(mount -l | grep "${SDCARD}" | awk '{ print $1 }') )
  for i in "${MOUNTED_SD_PART[@]}"
    do
      umount -f $i
  done

  if [ "$(mount -l | grep '${SDCARD}' | wc -c)" != 0 ];
    then
      echo "Failed to unmount sd card partitions." 1>&2
      exit 1
  fi
}

function check_device_type () {
  test -b /dev/mmcblk0 && test -b /dev/mmcblk1

  if [ $? -eq 0 ];
    then
      MMCBLK0=$(cat /sys/block/mmcblk0/device/type)
      MMCBLK1=$(cat /sys/block/mmcblk1/device/type)
    else
      echo "No sdcard inserted maybe?" 1>&2
      exit 1
  fi

  if [ $MMCBLK0 = "SD" ]
    then
      echo "mmcblk0 is the sdcard"
      SDCARD="/dev/mmcblk0"
    elif [ $MMCBLK1 = "SD" ]
      then
        echo "mmcblk1 is the sdcard"
        SDCARD="/dev/mmcblk1"
    else
      echo "Both devices aren't sdcard." 1>&2
      exit 1
  fi
}

if [ -f "${IMAGE}" ];
  then
    echo "finding sdcard and unmounting sdcard"
    check_device_type
    unmount_sdcard
    echo "copying ssh keys to sdimg, and adding rssh service"
    modify_sdimg
    echo "dd'ing sdimg over to sdcard"
    dd if=$IMAGE of=${SDCARD} bs=1M 2>&1
  else
    echo "${IMAGE} does not exist."
fi
