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

get_part_number_from_device() {
    case "$1" in
        /dev/mmcblk[0-9]p[1-9])
            echo ${1##*[0-9]p}
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
