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

get_grub_device_from_device_base() {
    case "$1" in
        /dev/[sh]d[a-z])
            dev_number=${1#/dev/[sh]d}
            dev_number=$(expr $(printf "%d" "'$dev_number") - $(printf "%d" "'a") || true)
            echo "hd$dev_number"
            ;;
        /dev/mmcblk[0-9]p)
            dev_number=${1#/dev/mmcblk}
            dev_number=${dev_number%p}
            echo "hd$dev_number"
            ;;
        /dev/nvme[0-9]n[0-9]p)
            dev_number=${1#/dev/nvme?n}
            dev_number=$(expr $(printf "%d" "'$dev_number") - $(printf "%d" "'1") || true)
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
        /dev/nvme[0-9]n[0-9]p[0-9])
            dev_base=$(echo $1 | cut -dp -f2)
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

def mender_version_is_minimum(d, component, min_version, if_true, if_false):
    from distutils.version import LooseVersion

    version = d.getVar('PREFERRED_VERSION_pn-%s' % component)
    if not version:
        version = d.getVar('PREFERRED_VERSION_%s' % component)
    if not version:
        version = "master"
    try:
        if LooseVersion(min_version) > LooseVersion(version):
            return if_false
        else:
            return if_true
    except TypeError:
        # Type error indicates that 'version' is likely a string (branch
        # name). For now we just default to always consider them higher than the
        # minimum version.
        return if_true
