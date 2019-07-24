#!/bin/sh

set -ue
PATH=/sbin:/bin:/usr/sbin:/usr/bin

devnode=@MENDER_STORAGE_DEVICE@

if [ -b ${devnode} ]; then
    echo "Installing image on ${devnode} ..."
else
    echo "No device available matching ${devnode}. Installation aborted."
    exit 1
fi

if [ -e /run/media/$1/$2 ]; then
    echo "Writing Mender-enabled Yocto image /run/media/$1/$2 to ${devnode}"
    echo "bzcat /run/media/$1/$2 | /bin/dd of=$devnode bs=8M"
    echo -n "OK to proceed? <y/n> "
    read yn
    if [ "$yn" = "y" ] || [ "$yn" = "Y" ]; then
        rc=0
        bzcat /run/media/$1/$2 | /bin/dd of=$devnode bs=8M || rc=$?
        sync
        if [ $rc = 0 ]; then
            echo "Installation successful."
        else
            echo "/bin/dd returned error $rc. Review above log. Installation aborted"
        fi
    else
        echo "Installation aborted"
    fi
else
    echo "Unable to locate $2. Installation aborted"
fi

echo "Remove your installation media and press ENTER to reboot."
read enter

echo "Rebooting..."
reboot -f
