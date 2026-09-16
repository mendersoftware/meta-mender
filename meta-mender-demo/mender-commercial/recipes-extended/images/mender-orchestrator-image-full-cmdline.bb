require recipes-extended/images/core-image-full-cmdline.bb

# Orchestrator deployments need more space, doubled as per MEN-7405 recommendation
MENDER_STORAGE_TOTAL_SIZE_MB ?= "2048"
MENDER_DATA_PART_SIZE_MB ?= "512"

MENDER_FEATURES_ENABLE:append = " mender-orchestrator-install"

# Enabling the feature here covers IMAGE_INSTALL, but not the MENDER_DEVICE_TIER it also
# sets: that one is read by the mender-client recipe when it generates mender.conf, and an
# override set in an image recipe never reaches another recipe's datastore. Verified by
# building without this: the device then registers as "standard" and the server has no way
# to tell it is a System Device. Set it on this image's own copy of the configuration
# instead, taking the value from the feature rather than repeating it here.
python set_orchestrator_device_tier() {
    import json

    conf = os.path.join(d.getVar("IMAGE_ROOTFS"), "etc/mender/mender.conf")
    if not os.path.exists(conf):
        bb.fatal("%s is missing, cannot set DeviceTier for the orchestrator" % conf)

    with open(conf) as fd:
        config = json.load(fd)
    config["DeviceTier"] = d.getVar("MENDER_DEVICE_TIER")
    with open(conf, "w") as fd:
        json.dump(config, fd, indent=4, sort_keys=True)
}
set_orchestrator_device_tier[vardeps] += "MENDER_DEVICE_TIER"
ROOTFS_POSTPROCESS_COMMAND += "set_orchestrator_device_tier;"

# Replace the mock-env topology that mender-orchestrator-support installs with a limited
# set of components to allow a deployment. The default one expects a "gateway" device_type
# that clashes with the image device_type (IOW the machine name) in QEMU.
install_orchestrator_topology() {
    cat > ${IMAGE_ROOTFS}/data/mender-orchestrator/topology.yaml <<'TOPOLOGY'
api_version: mender/v1
kind: topology
system_type: "system-core"

components:
  - component_type: rtos
    interface: rtos-interface
    interface_args: ["1"]

  - component_type: rtos
    interface: rtos-interface
    interface_args: ["2"]
TOPOLOGY
}
ROOTFS_POSTPROCESS_COMMAND += "install_orchestrator_topology;"
