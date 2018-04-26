get_uboot_interface_from_device() {
    case "$1" in
        /dev/mmcblk[0-9]p[1-9]|/dev/mmcblk[0-9])
            echo mmc
            ;;
        *)
            bberror "Could not determine U-Boot interface from $1"
            exit 1
            ;;
    esac
}

get_uboot_device_from_device() {
    case "$1" in
        /dev/mmcblk[0-9]p[1-9])
            dev_base=${1%p[1-9]}
            echo ${dev_base#/dev/mmcblk}
            ;;
        /dev/mmcblk[0-9])
            echo ${1#/dev/mmcblk}
            ;;
        *)
            bberror "Could not determine U-Boot device from $1"
            exit 1
            ;;
    esac
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
    case "$1" in
        /dev/*[0-9]p[1-9])
            echo ${1##*[0-9]p}
            ;;
        /dev/[sh]d[a-z][1-9])
            echo ${1##*d[a-z]}
            ;;
        ubi[0-9]_[0-9])
            echo ${1##*[0-9]_}
            ;;
        *)
            bberror "Could not determine partition number from $1"
            exit 1
            ;;
    esac
}
