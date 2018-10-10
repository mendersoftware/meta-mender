do_image_mender_teziimg[depends] += "tezi-metadata:do_deploy virtual/bootloader:do_deploy"

def mender_rootfs_rawnand(d):
    from collections import OrderedDict
    import subprocess

    ubimg_name = d.getVar("IMAGE_NAME")
    if ubimg_name == None:
        bb.warn("[Tezi json]: Unable to locate ubimg file. Aborting.")
        return None
    ubimg_sz_mb = subprocess.check_output(["du", "-ms", \
                                os.path.join(d.getVar("IMGDEPLOYDIR", True), \
                                ubimg_match.group(0))]).split()[0]

    return [
        OrderedDict({
          "name": "u-boot1",
          "content": {
            "rawfile": {
              "filename": d.getVar("UBOOT_BINARY", True),
              "size": 1
            }
          },
        }),
        OrderedDict({
          "name": "u-boot2",
          "content": {
            "rawfile": {
              "filename": d.getVar("UBOOT_BINARY", True),
              "size": 1
            }
          }
        }),
        OrderedDict({
          "name": "u-boot-env",
          "content": {
            "rawfile": {
              "filename": "uboot.env",
              "size": 1
            }
          }
        }),
        OrderedDict({
          "name": "ubi",
          "content": {
            "rawfile": {
              "filename": imagename + ".ubimg",
              "size": int(ubimg_sz_mb)
            }
          }
        })]

python mender_teziimg() {
    """
    mender_toradex_json creates a JSON image description file needed by
    Toradex Easy Installer. It also makes a copy of the required files
    (rootfs + metadata) into a sub-directory "toradex-easyinstaller",
    under ${DEPLOY_DIR_IMG} that can simply be moved to a USB stick
    and deployed.
    """
    import json
    from collections import OrderedDict
    from datetime import datetime

    deploydir = os.path.join(d.getVar("DEPLOY_DIR_IMAGE", True))
    release_date = datetime.strptime(d.getVar("DATE", True), "%Y%m%d").date().isoformat()

    data = OrderedDict({ "config_format": 2, "autoinstall": False })

    # Use image recipes SUMMARY/DESCRIPTION/PV...
    data["name"] = "Toradex/Mender Embedded Linux Demo"
    data["description"] = d.getVar("DESCRIPTION", True)
    data["version"] = "Yocto Rocko, Mender v1.5.0"
    data["release_date"] = release_date
    data["u_boot_env"] = "uEnv.txt"
    if os.path.exists(os.path.join(deploydir, "prepare.sh")):
        data["prepare_script"] = "prepare.sh"
    if os.path.exists(os.path.join(deploydir, "wrapup.sh")):
        data["wrapup_script"] = "wrapup.sh"
    if os.path.exists(os.path.join(deploydir, "marketing_mender_toradex.tar")):
        data["marketing"] = "marketing_mender_toradex.tar"
    if os.path.exists(os.path.join(deploydir, "mender_toradex_linux.png")):
        data["icon"] = "mender_toradex_linux.png"

    product_ids = d.getVar("TORADEX_PRODUCT_IDS", True)
    if product_ids is None:
        bb.fatal("Supported Toradex product ids missing, assign " + \ 
            "TORADEX_PRODUCT_IDS with a space separated list of product ids.")

    data["supported_product_ids"] = d.getVar("TORADEX_PRODUCT_IDS", True).split()

    if bb.utils.contains("TORADEX_FLASH_TYPE", "emmc", True, False, d):
        bb.note("Not able to generate metadata (image.json) for Toradex easy installer.")
        return
    else:
        mtddevs = mender_rootfs_rawnand(d)
        if mtddevs == None:
            return # warning message already generated
        data["mtddevs"] = mtddevs

    deploy_dir = d.getVar("DEPLOY_DIR_IMAGE", True)
    image_name = d.getVar("IMAGE_BASENAME", True) + "-" + d.getVar("MACHINE")

    # Write generated image.json file
    with open(os.path.join(deploy_dir, "image.json"), "w") as outfile:
        json.dump(data, outfile, indent=4)
    bb.note("Toradex Easy Installer metadata file image.json written.")
}

IMAGE_CMD_mender_teziimg() {
    case "${IMAGE_FSTYPES}" in
    *"ubimg"*)
        tar --transform="s,.*/,${IMAGE_BASENAME}-${MACHINE}-Teziimg/," \
            -chf ${IMGDEPLOYDIR}/${MACHINE}-${IMAGE_BASENAME}-Tezi-${DATETIME}.tar \
                    ${DEPLOY_DIR_IMAGE}/image.json \
                    ${DEPLOY_DIR_IMAGE}/mender_toradex_linux.png \
                    ${DEPLOY_DIR_IMAGE}/marketing_mender_toradex.tar \
                    ${DEPLOY_DIR_IMAGE}/prepare.sh \
                    ${DEPLOY_DIR_IMAGE}/wrapup.sh \
                    ${DEPLOY_DIR_IMAGE}/${UBOOT_BINARY} \
                    ${DEPLOY_DIR_IMAGE}/uboot.env \
                    ${DEPLOY_DIR_IMAGE}/uEnv.txt \
                    ${IMGDEPLOYDIR}/${IMAGE_BASENAME}-${MACHINE}.ubimg
        bbnote "Mender Tezi metadata successfully written and packed."
        ;;
    *)
        bbwarn "\"ubifs\" not in IMAGE_FSTYPES. Skipping teziimg."
    esac
}

IMAGE_FSTYPES += "mender_teziimg"
IMAGE_TYPEDEP_mender_teziimg_append = " ubimg"

