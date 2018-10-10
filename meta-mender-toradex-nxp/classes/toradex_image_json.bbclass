# Deploy image metadata before image-generation
do_image[depends] += "mender-toradex-metadata:do_deploy virtual/bootloader:do_deploy"

def mender_rootfs_get_size(d):
    import subprocess

    # Calculate size of rootfs in kilobytes.
    output = subprocess.check_output(["du", "-ks",
                                      d.getVar("IMAGE_ROOTFS", True)])
    return int(output.split()[0])


def mender_rootfs_rawnand(d):
    from collections import OrderedDict
    imagename = d.getVar("IMAGE_BASENAME", True) + "-" + d.getVar("MACHINE", True)

    # Use device tree mapping to create product id <-> device tree relationship
    dtmapping = d.getVarFlags("TORADEX_PRODUCT_IDS")
    dtfiles = []
    for f, v in dtmapping.items():
        dtfiles.append({ "filename": v, "product_ids": f })

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
              "size": d.getVar("IMAGE_ROOTFS_MAXSIZE", True)[:-3]
            }
          }
        })]

python mender_toradex_json() {
    """
    mender_toradex_json creates a JSON image description file needed by
    Toradex Easy Installer. It also makes a copy of the required files
    (rootfs + metadata) into a sub-directory "toradex-easyinstaller",
    under ${DEPLOY_DIR_IMG} that can simply be moved to a USB stick
    and deployed.
    """
    import json
    import re
    import shutil
    from collections import OrderedDict
    from datetime import datetime

    deploydir = os.path.join(d.getVar("DEPLOY_DIR_IMAGE", True), "toradex-easyinstaller")
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
        bb.fatal("Supported Toradex product ids missing, assign TORADEX_PRODUCT_IDS with a list of product ids.")

    data["supported_product_ids"] = d.getVar("TORADEX_PRODUCT_IDS", True).split()

    if bb.utils.contains("TORADEX_FLASH_TYPE", "emmc", True, False, d):
        bb.note("Not able to generate metadata (image.json) for Toradex easy installer.")
        return
    else:
        data["mtddevs"] = mender_rootfs_rawnand(d)

    deploy_dir = d.getVar("DEPLOY_DIR_IMAGE", True)
    image_name = d.getVar("IMAGE_BASENAME", True) + "-" + d.getVar("MACHINE")

    # Copy image file to "toradex" subdirectory (in image deploy directory)
    dst = os.path.join(deploy_dir, "toradex-easyinstaller")
    if not os.path.exists(dst):
        os.makedirs(dst)
    src_match = re.search("%s-%s-[0-9]{14}\.ubimg" % \
                         (d.getVar("IMAGE_BASENAME", True), \
                          d.getVar("MACHINE", True)), \
                         " ".join(os.listdir(d.getVar('IMGDEPLOYDIR'))))
    if src_match == None:
         bb.warn("Could not copy ubimg to toradex-easyinstaller subdir; file not found.")
    else:
        src = os.path.join(d.getVar('IMGDEPLOYDIR'), src_match.group(0))
        shutil.copy(src, os.path.join(dst, image_name) + ".ubimg")

    # Copy uboot environment files
    _dst_ = os.path.join(dst, "uboot.env")
    src = os.path.join(deploy_dir, "uboot.env")
    shutil.copy(src, _dst_)

    _dst_ = os.path.join(dst, "u-boot-nand.imx")
    src = os.path.join(deploy_dir, "u-boot-nand.imx")
    shutil.copy(src, _dst_)

    _dst_ = os.path.join(dst, "uEnv.txt")
    src = os.path.join(deploy_dir, "uEnv.txt")
    shutil.copy(src, _dst_)
    
    # Write generated image.json file
    with open(os.path.join(dst, "image.json"), "w") as outfile:
        json.dump(data, outfile, indent=4)
    bb.note("Toradex Easy Installer metadata file image.json written.")
    bb.note("Easy installer deployment-ready directory \"%s\" created." % dst)
}

# Add JSON-generating function after image has been created
do_image_complete[postfuncs] += "mender_toradex_json"

