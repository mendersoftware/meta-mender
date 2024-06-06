inherit mender-licensing

SUB_FOLDER:arm = "arm"
SUB_FOLDER:aarch64 = "aarch64"
SUB_FOLDER:x86-64 = "x86_64"

def mender_flash_tool_dependency(d):
    flash_tool = d.getVar("MENDER_FLASH_TOOL")
    if flash_tool == "mender-flash":
        return " mender-flash"
    elif flash_tool == "ubiupdatevol":
        return " mtd-utils-ubifs"
    else:
        return ""

MENDER_FLASH_TOOL ??= "${_MENDER_FLASH_TOOL_DEFAULT}"
_MENDER_FLASH_TOOL_DEFAULT ??= "mender-flash"
RDEPENDS:${PN}:append = "${@mender_flash_tool_dependency(d)}"

COMPATIBLE_HOSTS = "arm|aarch64|x86_64"

# "lsb-ld" is needed because Yocto by default does not provide a cross platform
# dynamic linker. On x86_64 this manifests as a missing
# `/lib64/ld-linux-x86-64.so.2`
RDEPENDS:${PN} = "lsb-ld xz liblzma"

FILES:${PN} = " \
    ${sysconfdir}/mender/mender-binary-delta.conf \
    ${datadir}/mender/modules/v3/mender-binary-delta \
"

INSANE_SKIP:${PN} = "already-stripped"

do_version_check() {
    if [ ! -e ${S}/${SUB_FOLDER}/mender-binary-delta ]; then
        bbfatal "No mender-binary-delta binary found. Have you added the package to SRC_URI?"
    fi

    if ! ${@'true' if d.getVar('MENDER_DEVMODE') else 'false'}; then
        if ! strings ${S}/${SUB_FOLDER}/mender-binary-delta | fgrep -q "${PN} ${PV}"; then
            bbfatal "String '${PN} ${PV}' not found in binary. Is it the correct version? Check with --version. Possible candidates: $(strings ${S}/${SUB_FOLDER}/mender-binary-delta | grep '${PN} [a-f0-9]')"
        fi
    fi
}
addtask do_version_check after do_patch before do_install

do_configure() {
    echo "{" > ${WORKDIR}/mender-binary-delta.conf

    if [ -n "${MENDER_FLASH_TOOL}" ]; then
        cat >>${WORKDIR}/mender-binary-delta.conf <<EOF
   "FlashTool": "${MENDER_FLASH_TOOL}",
EOF
    fi

    cat >> ${WORKDIR}/mender-binary-delta.conf <<EOF
   "RootfsPartA": "${MENDER_ROOTFS_PART_A}",
   "RootfsPartB": "${MENDER_ROOTFS_PART_B}"
EOF

    # We need to us echo instead of Here Document because bitbake misinterprets the JSON closing
    # brace as end of function, if it is at the beginning of the line.
    echo '}' >> ${WORKDIR}/mender-binary-delta.conf
}

do_install() {
    install -d -m 755 ${D}${datadir}/mender/modules/v3
    install -m 755 ${S}/${SUB_FOLDER}/mender-binary-delta ${D}${datadir}/mender/modules/v3/mender-binary-delta

    install -d -m 755 ${D}${sysconfdir}/mender
    install -m 644 ${WORKDIR}/mender-binary-delta.conf ${D}${sysconfdir}/mender/mender-binary-delta.conf
}
