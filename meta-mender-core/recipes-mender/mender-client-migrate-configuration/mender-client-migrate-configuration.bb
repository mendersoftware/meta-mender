FILESEXTRAPATHS_prepend := "${THISDIR}/files:"

SRC_URI = " \
          file://mender-client-migrate-configuration;subdir=${PN}-${PV} \
          file://LICENSE;subdir=${PN}-${PV} \
          "

LICENSE = "Apache-2.0"
LIC_FILES_CHKSUM = "file://LICENSE;md5=e3fc50a88d0a364313df4b21ef20c29e"

inherit mender-state-scripts

ALLOW_EMPTY_${PN} = "1"

RDEPENDS_${PN} += "jq"

DEPENDS += "mender-client"

do_check_split_conf() {
    if [ -f ${STAGING_DIR_TARGET}/data/mender/mender.conf ]; then
        bbfatal "A persistent Mender configuration file was found on the /data partition. To migrate the configuration, \
disable split-mender-config by adding PACKAGECONFIG_remove = \" split-mender-config\" to your local.conf"
    fi
}
addtask do_check_split_conf before do_compile

do_compile[vardeps] += "MENDER_PERSISTENT_CONFIGURATION_VARS"
do_compile() {

    # Get and filter the variables that the user wants to migrate to the persistent configuration.
    # This also ensures that our fields are split by a single space, which means that translate
    # below always functions properly.
    PERSISTENT_CONFIGS="${@bb.utils.filter("MENDER_PERSISTENT_CONFIGURATION_VARS", d.getVar("MENDER_CONFIGURATION_VARS"), d)}"

    # [a b] -> [{a,b}]
    MENDER_JQ_PROGRAM="{$(echo $PERSISTENT_CONFIGS | tr ' ' ',')}"

    # [a b] -> [.a, .b]
    MENDER_JQ_DELETE=".$(echo $PERSISTENT_CONFIGS | awk -F ' ' -v OFS=', .' '$1=$1')"

    # Replace the program markers in the script with the jq programs generated above.
    sed -i "s/%jq-program-marker%/${MENDER_JQ_PROGRAM}/" mender-client-migrate-configuration
    sed -i "s/%jq-delete-fields-marker%/${MENDER_JQ_DELETE}/" mender-client-migrate-configuration

    # Deploy script as a State Script
    cp mender-client-migrate-configuration ${MENDER_STATE_SCRIPTS_DIR}/ArtifactCommit_Enter_10_migrate-configuration
}
