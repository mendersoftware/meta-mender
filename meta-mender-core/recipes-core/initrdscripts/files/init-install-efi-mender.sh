#!/bin/sh

set -ue
PATH=/sbin:/bin:/usr/sbin:/usr/bin

devnode="@MENDER_STORAGE_DEVICE@"
bootdev="$(echo /dev/$1 | sed 's@/$@@')"

if [ -z ${devnode} ] || [ ! -b ${devnode} ]; then
    echo "Searching for hard drives ..."
    devlist=$(fdisk -l 2>&1 | \
                  grep ^Disk\ /dev.\*: | \
                  grep -v loop | \
                  grep -v sr0 | \
                  grep -v mapper | \
                  grep -v ram | \
                  grep -v 'mmcblk.*boot' | \
                  grep -v ${bootdev} | \
                  cut -d: -f 1 | cut -d\  -f 2 | sort | uniq)
    for dev in ${devlist}; do
        devbase=$(echo $dev | sed 's@/dev/@@')
        echo "Detected block device " ${dev}
        [ -r /sys/block/$devbase/device/vendor ] && echo "VENDOR=$(cat /sys/block/$devbase/device/vendor)"
        [ -r /sys/block/$devbase/device/model  ] && echo "MODEL=$(cat /sys/block/$devbase/device/model)"
        [ -r /sys/block/$devbase/device/uevent ] && echo "UEVENT=$(cat /sys/block/$devbase/device/uevent)"
        echo -n "Install to this device? <y/n> "
        read yn
        if [ "$yn" = "y" ] || [ "$yn" = "Y" ]; then
            devnode=$dev
            break
        fi
    done
fi

if [ -n "${devnode}" -a -b ${devnode} ]; then
    echo "Installing image on ${devnode} ..."
else
    echo "No device available matching ${devnode}. Installation aborted."
    /bin/sh
    exit 1
fi

if [ -e /run/media/$1$2 ]; then
    echo "Writing Mender-enabled Yocto image /run/media/$1$2 to ${devnode}"
    echo "bzcat /run/media/$1$2 | /bin/dd of=$devnode bs=8M"
    echo -n "OK to proceed? <y/n> "
    read yn
    if [ "$yn" = "y" ] || [ "$yn" = "Y" ]; then
        rc=0
        bzcat /run/media/$1$2 | /bin/dd of=$devnode bs=8M || rc=$?
        sync
        if [ $rc = 0 ]; then
            echo "Installation successful."
        else
            echo "/bin/dd returned error $rc. Review above log. Installation aborted"
            /bin/sh
            exit 1
        fi
    else
        echo "Installation aborted"
        /bin/sh
        exit 1
    fi
else
    echo "Unable to locate image $2, on bootdev ${bootdev}. Installation aborted"
    /bin/sh
    exit 1
fi

echo "Remove your installation media and press ENTER to reboot."
read enter

echo "Rebooting..."
reboot -f
