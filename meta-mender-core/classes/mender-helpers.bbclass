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
        /dev/[sh]d[a-z][1-9])
            dev_base=${1##*d[a-z]}
            ;;
        /dev/nvme[0-9]n[0-9]p[0-9])
            dev_base=$(echo $1 | cut -dp -f2)
            ;;
        ubi*_* )
            dev_base=$(echo $1 | cut -d_ -f2)
            ;;
        /dev/disk/by-partuuid/* )
            bberror "Please enable mender-partuuid Distro feature to use PARTUUID"
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

mender_number_to_hex() {
    part_hex=$(printf "%X" $1 2>/dev/null)
}

def mender_get_partuuid_from_device(d, deviceName):
    import re
    if bb.utils.contains('DISTRO_FEATURES', 'mender-partuuid', True, False, d) and deviceName:
        uuid=deviceName.replace('/dev/disk/by-partuuid/', '')
        gptMatch = re.search('^[0-9a-f]{8}\-[0-9a-f]{4}\-[0-9a-f]{4}\-[0-9a-f]{4}\-[0-9a-f]{12}$', uuid)
        if gptMatch:
            return gptMatch.group(0)

        msdosMatch = re.search("^[0-9a-f]{8}\-[0-9]{2}$", uuid)
        if msdosMatch:
            return msdosMatch.group(0)
        bb.fatal("%s Does not contain a valid PARTUUID path" % deviceName )
    return

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
            offset = mender_mtdparts_convert_units_to_bytes(match.group(3), match.group(4))

        if match.group(1) == '-':
            size = '-'
            kbsize = '-'
            remaining_encountered = True
        else:
            size = mender_mtdparts_convert_units_to_bytes(match.group(1), match.group(2))
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

def mender_mtdparts_convert_units_to_bytes(number, unit):
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

mender_get_clean_kernel_devicetree() {
    if [ -n "${MENDER_DTB_NAME_FORCE}" ]; then
        MENDER_DTB_NAME="${MENDER_DTB_NAME_FORCE}"
    else
        # Strip leading and trailing whitespace, then newline divide, and remove dtbo's.
        MENDER_DTB_NAME="$(echo "${KERNEL_DEVICETREE}" | sed -r 's/(^\s*)|(\s*$)//g; s/\s+/\n/g' | sed -ne '/\.dtbo$/b; p')"

        if [ -z "$MENDER_DTB_NAME" ]; then
            bbfatal "Did not find a dtb specified in KERNEL_DEVICETREE"
            exit 1
        fi
    fi

    DTB_COUNT=$(echo "$MENDER_DTB_NAME" | wc -l)

    if [ "$DTB_COUNT" -ne 1 ]; then
        MENDER_DTB_NAME="$(echo "$MENDER_DTB_NAME" | tail -1)"
        bbwarn "Found more than one dtb specified in KERNEL_DEVICETREE (${KERNEL_DEVICETREE}). Only one should be specified. Choosing the last one: ${MENDER_DTB_NAME}. Set KERNEL_DEVICETREE to the desired dtb file to silence this warning."
    fi

    # Now strip any subdirectories off.  Some kernel builds require KERNEL_DEVICETREE to be defined, for example,
    # as qcom/apq8016-sbc.dtb yet when installed, they go directly in /boot
    MENDER_DTB_NAME="$(basename "$MENDER_DTB_NAME")"

    # Return.
    echo "$MENDER_DTB_NAME"
}


def mender_is_msdos_ptable_image(d):
    mptimgs = 'mender-image-sd mender-image-bios'
    return bb.utils.contains_any('DISTRO_FEATURES', mptimgs , True, False, d)


def mender_get_data_and_total_parts_num(d):
    data_pos = 3
    parts_num = 3

    boot_part_size = d.getVar('MENDER_BOOT_PART_SIZE_MB')
    if (boot_part_size and boot_part_size != '0'):
        data_pos += 1
        parts_num += 1

    swap_part_size = d.getVar('MENDER_SWAP_PART_SIZE_MB')
    if (swap_part_size and swap_part_size != '0'):
        data_pos += 1
        parts_num += 1

    extra_parts = d.getVar('MENDER_EXTRA_PARTS')
    if extra_parts is None or len(extra_parts) == 0:
        extra_parts = []
    else:
        extra_parts = extra_parts.split()
    parts_num += len(extra_parts)

    #is an msdos extended partion going to be required
    if parts_num > 4 and mender_is_msdos_ptable_image(d):
        parts_num += 1
        if data_pos >= 4:
            data_pos += 1
    return data_pos, parts_num

def mender_get_data_part_num(d):
    data_num, _ = mender_get_data_and_total_parts_num(d)
    return data_num

def mender_get_total_parts_num(d):
    _, total_part_num = mender_get_data_and_total_parts_num(d)
    return total_part_num

def mender_get_extra_parts_offset(d):
    data_num = mender_get_data_part_num(d)
    total_part_num = mender_get_total_parts_num(d)
    # extra parts start after data part
    extra_part_num = data_num + 1

    # we have no boot part and add two or more extra partitions then move index as extended partition is created
    if data_num < 4 and total_part_num >= 5: extra_part_num += 1

    return extra_part_num 

# Take the content from the rootfs that is going into the boot partition, coming
# from MENDER_BOOT_PART_MOUNT_LOCATION, and merge with the files from
# IMAGE_BOOT_FILES, following the format from the official Yocto documentation.
mender_merge_bootfs_and_image_boot_files() {
    W="${WORKDIR}/bootfs.${BB_CURRENTTASK}"
    rm -rf "$W"

    cp -al "${IMAGE_ROOTFS}/${MENDER_BOOT_PART_MOUNT_LOCATION}" "$W"

    # Put in variable to avoid expansion and ';' being parsed by shell.
    image_boot_files="${IMAGE_BOOT_FILES}"
    for entry in $image_boot_files; do
        if echo "$entry" | grep -q ";"; then
            dest="$(echo "$entry" | sed -e 's/[^;]*;//')"
            entry="$(echo "$entry" | sed -e 's/;.*//')"
        else
            dest="./"
        fi
        if echo "$dest" | grep -q '/$'; then
            dest_is_dir=1
            mkdir -p "$W/$dest"
        else
            dest_is_dir=0
            mkdir -p "$(dirname "$W/$dest")"
        fi

        # Use extra for loop so we can check conflict for each file.
        for file in ${DEPLOY_DIR_IMAGE}/$entry; do
            if [ $dest_is_dir -eq 1 ]; then
                destfile="$W/$dest$(basename $file)"
            else
                destfile="$W/$dest"
            fi
            if [ -e "$destfile" ]; then
                if ! cmp --quiet "$file" "$destfile"; then
                    bbfatal "$destfile already exists in boot partition. Please verify that packages do not put files in the boot partition that conflict with IMAGE_BOOT_FILES."
                fi
            else
                # create a hardlink if possible (prerequisite: the paths are below the same mount point), do a normal copy otherwise
                cp -l "$file" "$destfile" || cp "$file" "$destfile"
            fi
        done
    done
}

def get_extra_parts(d):
    final_parts = []
    partsflags = d.getVarFlags("MENDER_EXTRA_PARTS") or {}
    if partsflags:
        parts = (d.getVar('MENDER_EXTRA_PARTS') or "").split()

        for flag, flagval in partsflags.items():
            if flag in parts:
                final_parts.append(flagval)

    return final_parts

def get_extra_parts_flags(d):
    partsflags = d.getVarFlags("MENDER_EXTRA_PARTS") or {}
    if partsflags:
        return partsflags.keys()

    return []

def get_extra_parts_by_id(d, id = None):
    partsflags = d.getVarFlags("MENDER_EXTRA_PARTS") or {}
    if partsflags:
        if id in partsflags.keys():
            return partsflags[id]
    return ""

def get_extra_parts_labels(d):
    labels = []
    ids = get_extra_parts_flags(d)
    if ids:
        for id in ids:
            labels.append(get_extra_parts_label(d, id))
    return ' '.join(labels)

def get_extra_parts_label(d, id = None):
    part = get_extra_parts_by_id(d, id)
    if part:
        import re
        match = re.search(r'--label=(\S+)', part)
        return match.group(1) if match else ""

    return ""

def get_extra_parts_wks(d):
    final_parts = []
    parts = get_extra_parts(d) or {}
    if parts:
        for part in parts:
            final_parts.append("part --ondisk \"$ondisk_dev\" --align \"$alignment_kb\" {}".format(part))
    return '\n'.join(final_parts)

def get_extra_parts_fstab_opts(d, id = None):
    parts_fstab_flags = d.getVarFlags("MENDER_EXTRA_PARTS_FSTAB") or {}
    extra_parts_flags = (d.getVar('MENDER_EXTRA_PARTS') or "").split()
    if parts_fstab_flags:
        if id in parts_fstab_flags:
            split = parts_fstab_flags[id].split()
            elems = len(split)
            if elems < 2:
                bb.fatal("MENDER_EXTRA_PARTS_FSTAB[%s] is invalid. You need to provide parameters for fs_vfstype and fs_mntops (see 'man fstab')" % id)
            elif elems < 3:
                # Need to return pass number and fsck number
                return parts_fstab_flags[id] + " 0 2"
            elif elems < 4:
                # Need to return fsck number
                return parts_fstab_flags[id] + " 2"
            else:
                return parts_fstab_flags[id]

    return "auto default 0 2"

def get_extra_parts_fstab(d):
    out = []
    extra_parts_offset = mender_get_extra_parts_offset(d)
    device = d.getVar('MENDER_STORAGE_DEVICE_BASE')
    for part in get_extra_parts_flags(d):
       label = get_extra_parts_label(d, part)
       fstype_opts = get_extra_parts_fstab_opts(d, part)
       out.append("{} {} {}".format(device + str(extra_parts_offset), "/mnt/{}".format(label), fstype_opts))
       extra_parts_offset += 1

    return '\n'.join(out)
