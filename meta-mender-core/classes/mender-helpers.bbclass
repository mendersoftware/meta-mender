DEPENDS += "coreutils-native"

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

    device=$(printf "%d" $dev_base 2>/dev/null)
    if [ $? = 1 ]; then
        bberror "Could not determine U-Boot device from $1"
        exit 1
    else
        echo $device
    fi
}

get_part_number_from_device() {
    dev_base="unknown"
    case "$1" in
        /dev/mmcblk*p* )
            dev_base=$(echo $1 | cut -dk -f2 | cut -dp -f2)
            ;;
        ubi*_* )
            dev_base=$(echo $1 | cut -d_ -f2)
            ;;
    esac
    part=$(printf "%d" $dev_base 2>/dev/null)
    if [ $? = 1 ]; then
        bberror "Could not determine partition number from $1"
        exit 1
    else
        echo $part
    fi
}

get_part_number_hex_from_device() {
    part_dec=$(get_part_number_from_device $1)
    part_hex=$(printf "%X" $part_dec 2>/dev/null)
    if [ $? = 1 ]; then
        bberror "Could not determine partition number from $1"
        exit 1
    else
        echo $part_hex
    fi
}
