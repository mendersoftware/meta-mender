# Whitespace separated list of files declared by 'deploy_var' variable
# from 'source_dir' (DEPLOY_DIR_IMAGE by default) to place in 'deploy_dir'.
# Entries will be installed under a same name as the source file. To change
# the destination file name, pass a desired name after a semicolon
# (eg. u-boot.img;uboot). Exactly same rules with how IMAGE_BOOT_FILES being
# handled by wic.
def mender_install_deployed_files(d, deploy_var, deploy_dir, source_dir=None):
    import os, re, glob, subprocess

    src_files = d.getVar(deploy_var) or ""
    src_dir = source_dir or d.getVar('DEPLOY_DIR_IMAGE')
    dst_dir = deploy_dir

    # list of tuples (src_name, dst_name)
    deploy_files = []
    for src_entry in re.findall(r'[\w;\-\./\*]+', src_files):
        if ';' in src_entry:
            dst_entry = tuple(src_entry.split(';'))
            if not dst_entry[0] or not dst_entry[1]:
                bb.fatal('Malformed file entry: %s' % src_entry)
        else:
            dst_entry = (src_entry, src_entry)
        deploy_files.append(dst_entry)

    # list of tuples (src_path, dst_path)
    install_task = []
    for deploy_entry in deploy_files:
        src, dst = deploy_entry
        if '*' in src:
            # by default install files under their basename
            entry_name_fn = os.path.basename
            if dst != src:
                # unless a target name was given, then treat name
                # as a directory and append a basename
                entry_name_fn = lambda name: \
                                os.path.join(dst,
                                             os.path.basename(name))

            srcs = glob.glob(os.path.join(src_dir, src))
            for entry in srcs:
                src = os.path.relpath(entry, src_dir)
                entry_dst_name = entry_name_fn(entry)
                install_task.append((src, entry_dst_name))
        else:
            install_task.append((src, dst))

    # install src_path to dst_path
    for task in install_task:
        src_path, dst_path = task
        install_cmd = "install -m 0644 -D %s %s" \
                      % (os.path.join(src_dir, src_path),
                         os.path.join(dst_dir, dst_path))
        try:
            subprocess.check_output(install_cmd, stderr=subprocess.STDOUT, shell=True)
        except subprocess.CalledProcessError as e:
            bb.fatal("Command '%s' returned %d:\n%s" % (e.cmd, e.returncode, e.output))


python rpi_install_firmware_to_rootfs() {
    mender_install_deployed_files(d, 'IMAGE_BOOT_FILES', os.path.join(d.getVar('IMAGE_ROOTFS'), 'boot', 'firmware'))
}
ROOTFS_POSTPROCESS_COMMAND += "rpi_install_firmware_to_rootfs; "

IMAGE_INSTALL:append = " update-firmware-state-script"
