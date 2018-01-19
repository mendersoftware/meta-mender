get_uboot_interface_from_device() {
    case "$1" in
        /dev/mmcblk* )
            echo mmc
            ;;
        *)
            bberror "Could not determine U-Boot interface from $1"
            exit 1
            ;;
    esac
}

get_uboot_device_from_device() {
    dev_base="unknown"
    case "$1" in
        /dev/mmcblk*p* )
            dev_base=$(echo $1 | cut -dk -f2 | cut -dp -f1)
            ;;
        /dev/mmcblk* )
            dev_base=$(echo $1 | cut -dk -f2)
            ;;
    esac

    device=$(printf "%X" $dev_base 2>/dev/null)
    if [ $? = 1 ]; then
        bberror "Could not determine U-Boot device from $1"
        exit 1
    else
        echo $device
    fi
}

get_grub_device_from_device_base() {
    case "$1" in
        /dev/[sh]da)
            dev_number=${1#/dev/[sh]d}
            dev_number=$(expr $(printf "%d" "'$dev_number") - $(printf "%d" "'a") || true)
            echo "hd$dev_number"
            ;;
        *)
            bberror "Could not determine Grub device from $1"
            exit 1
            ;;
    esac
}

get_part_number_from_device() {
    dev_base="unknown"
    case "$1" in
        /dev/mmcblk*p* )
            dev_base=$(echo $1 | cut -dk -f2 | cut -dp -f2)
            ;;
        /dev/[sh]d[a-z][1-9])
            dev_base=${1##*d[a-z]}
            ;;
        ubi*_* )
            dev_base=$(echo $1 | cut -d_ -f2)
            ;;
    esac
    part=$(printf "%X" $dev_base 2>/dev/null)
    if [ $? = 1 ]; then
        bberror "Could not determine partition number from $1"
        exit 1
    else
        echo $part
    fi
}
