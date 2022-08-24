python do_check_for_missing_licenses() {
    import re

    if d.getVar('LIC_FILES_CHKSUM') is None:
        bb.fatal("LIC_FILES_CHKSUM cannot be empty!")
    licenses = [entry.split(";")[0] for entry in d.getVar('LIC_FILES_CHKSUM').split()]

    # Assume that the first license in LIC_FILES_CHKSUM is also the folder where
    # LIC_FILES_CHKSUM.sha256 resides.
    first_license = re.sub('^file://', '', licenses[0])

    var_dir = os.path.dirname(first_license)
    if var_dir == ".":
        var_dir = ""
    elif var_dir != "":
        var_dir += "/"
    real_dir = os.path.dirname(os.path.join(d.getVar('S'), first_license))

    with open(os.path.join(real_dir, "LIC_FILES_CHKSUM.sha256")) as fd:
        for line in fd.readlines():
            line = line.strip()
            if len(line) == 0 or line.startswith("#"):
                continue

            license_file = "file://%s%s" % (var_dir, line.split()[1])
            if license_file not in licenses:
                bb.fatal(f"{license_file} not found in LIC_FILES_CHKSUM (the latter contains {licenses}). Use mendertesting/utils/make_bitbake_license_list.sh to automatically generate the required entries.")
}
python() {
    if d.getVar('_MENDER_DISABLE_STRICT_LICENSE_CHECKING', '0') != '1':
        bb.build.addtask('do_check_for_missing_licenses', 'do_configure', 'do_patch', d)
}
