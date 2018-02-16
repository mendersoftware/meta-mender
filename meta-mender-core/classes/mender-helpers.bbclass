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

def mender_make_mtdparts_shell_array(d):
    """Makes a string that can be shell-eval'ed to get the components of the
    mtdparts string. See the "local mtd_..." definitions below."""

    mtdparts = d.getVar('MENDER_MTDPARTS')
    if len(mtdparts) == 0:
        return "bbfatal 'MENDER_MTDPARTS is empty.'"

    active_mtdid = d.getVar('MENDER_IS_ON_MTDID')
    if len(active_mtdid) == 0:
        return "bbfatal 'MENDER_IS_ON_MTDID is empty. Please set it to the mtdid inside MENDER_MTDPARTS that you want Mender to use.'"

    import re

    def convert_units_to_bytes(number, unit):
        if unit is None or unit.lower() == '':
            to_return = int(number)
        elif unit.lower() == 'k':
            to_return = int(number) * 1024
        elif unit.lower() == 'm':
            to_return = int(number) * 1048576
        elif unit.lower() == 'g':
            to_return = int(number) * 1073741824
        else:
            bb.fatal("Cannot parse number '%s' and unit '%s'" % (number, unit))

        if to_return % 1024 != 0:
            bb.fatal("Numbers in mtdparts must be aligned to a KiB boundary")

        return to_return

    # Breaking up the mtdparts string in shell is tricky, so do it here, and
    # just return a string that can be eval'ed in the shell. Can't use real bash
    # arrays though... sigh.
    count = 0
    total_offset = 0
    shell_cmd = ""
    remaining_encountered = False

    # Pick the mtdid that matches MENDER_IS_ON_MTDID.
    current_mtdparts = None
    for part in mtdparts.split(";"):
        if part.split(":")[0] == active_mtdid:
            current_mtdparts = part

    if current_mtdparts is None:
        return ("bbfatal 'Cannot find a valid mtdparts string inside MENDER_MTDPARTS (\"%s\"), "
                + "corresponding to MENDER_IS_ON_MTDID (\"%s\").'"
                % (mtdparts, active_mtdid))

    mtdparts = current_mtdparts

    # Skip first component (the ID).
    for component in mtdparts.split(":")[1].split(","):
        if len(component) == 0:
            continue

        if remaining_encountered:
            return "bbfatal \"'-' entry was not last entry in mtdparts: '%s'\"" % mtdparts

        match = re.match("^([0-9]+|-)([kmg]?)(?:@([0-9]+)([kmg]?))?\(([^)]+)\)(?:ro)?$", component)
        if match is None:
            return "bbfatal \"'%s' is not a valid mtdparts string. Please set MENDER_MTDPARTS to a valid value\"" % mtdparts

        # Make a shell array out of the mtdparts.
        if match.group(3) is None:
            offset = total_offset
        else:
            offset = convert_units_to_bytes(match.group(3), match.group(4))

        if match.group(1) == '-':
            size = '-'
            kbsize = '-'
            remaining_encountered = True
        else:
            size = convert_units_to_bytes(match.group(1), match.group(2))
            kbsize = int(size / 1024)
            total_offset = offset + size

        name = match.group(5)

        shell_cmd += "local mtd_sizes_%d='%s'\n" % (count, size)
        shell_cmd += "local mtd_kbsizes_%d='%s'\n" % (count, kbsize)
        shell_cmd += "local mtd_offsets_%d='%d'\n" % (count, offset)
        shell_cmd += "local mtd_kboffsets_%d='%d'\n" % (count, offset / 1024)
        shell_cmd += "local mtd_names_%d='%s'\n" % (count, name)

        count += 1

    shell_cmd += "local mtd_count=%d\n" % count

    return shell_cmd
