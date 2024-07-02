# ------------------------------ CONFIGURATION ---------------------------------

# Extra arguments that should be passed to mender-artifact.
MENDER_ARTIFACT_CAPSULE_EXTRA_ARGS ?= ""

# The guid used to sign the mender update.
MENDER_ARTIFACT_SIGNING_KEY ?= ""

do_image_mender_capsule[depends] += "mender-artifact-native:do_populate_sysroot"

MENDER_ARTIFACT_CAPSULE_NAME ??= "${MENDER_ARTIFACT_CAPSULE_NAME_DEFAULT}"
MENDER_ARTIFACT_CAPSULE_NAME_DEFAULT = "uefi-capsule-${MACHINE}"

MENDER_ARTIFACT_CAPSULE_NAME_DEPENDS ?= ""

MENDER_ARTIFACT_CAPSULE_PROVIDES ?= ""

MENDER_ARTIFACT_CAPSULE_DEPENDS ?= ""

CAPSULE_GUIDS ?= ""

CAPSULE_TYPE ?= "uefi-firmware"


def get_mender_capsule_artifact_provides(d):
    # This function creates the provides format required by mender artifact to
    # generate the capsule artifact.
    # MENDER_ARTIFACT_CAPSULE_PROVIDES needs to be used in the following way.
    # MENDER_ARTIFACT_CAPSULE_PROVIDES[e2bb9c06-70e9-4b14-97a3-5a7913176111] = "tfa:3"
    # MENDER_ARTIFACT_CAPSULE_PROVIDES[e2bb9c06-70e9-4b14-97a3-5a7913176222] = "edk2:3"
    # This gets converted to the following provides format:
    # "uefi-firmware.e2bb9c06-70e9-4b14-97a3-5a7913176111.name":"tfa",
    # "uefi-firmware.e2bb9c06-70e9-4b14-97a3-5a7913176111.version":"3",
    # "uefi-firmware.e2bb9c06-70e9-4b14-97a3-5a7913176222.name":"edk2",
    # "uefi-firmware.e2bb9c06-70e9-4b14-97a3-5a7913176222.version":"3",
    guids = d.getVarFlags("MENDER_ARTIFACT_CAPSULE_PROVIDES")
    capsule_type = d.getVar("CAPSULE_TYPE", expand=True)
    if guids is None:
        return
    provides = ""
    for guid in guids:
        splt = guids[guid].split(":")
        provides += " --provides " + capsule_type + "." + guid + ".version:" + splt[1]
        provides += " --provides " + capsule_type + "." + guid + ".name:" + splt[0]
    return provides

def get_mender_capsule_artifact_depends(d):
    # This function creates the depends format required by mender artifact to
    # generate the capsule artifact.
    # MENDER_ARTIFACT_CAPSULE_DEPENDS needs to be used in the following way.
    #MENDER_ARTIFACT_CAPSULE_DEPENDS[e2bb9c06-70e9-4b14-97a3-5a7913176111] = "2"
    #MENDER_ARTIFACT_CAPSULE_DEPENDS[e2bb9c06-70e9-4b14-97a3-5a7913176222] = "2"
    # This gets converted to the following depends format:
    # "uefi-firmware.e2bb9c06-70e9-4b14-97a3-5a7913176111.version":"2"
    # "uefi-firmware.e2bb9c06-70e9-4b14-97a3-5a7913176222.version":"2"
    guids = d.getVarFlags("MENDER_ARTIFACT_CAPSULE_DEPENDS")
    capsule_type = d.getVar("CAPSULE_TYPE", expand=True)
    if guids is None:
        return
    depends = ""
    for guid in guids:
        depends += " --depends " + capsule_type + "." + guid + ".version:" + guids[guid]
    return depends

def get_mender_capsule_artifact_clears_provides(d):
    # This function creates the clears provides format required by mender artifact
    # to generate the capsule artifact.
    guids = d.getVarFlags("MENDER_ARTIFACT_CAPSULE_PROVIDES")
    capsule_type = d.getVar("CAPSULE_TYPE", expand=True)
    if guids is None:
        return
    clears_provides = ""
    for guid in guids:
        clears_provides += " --clears-provides " + capsule_type + "." + guid + ".version"
    return clears_provides

_MENDER_CAPSULE_PROVIDES = "${@get_mender_capsule_artifact_provides(d)}"
_MENDER_CAPSULE_CLEARS_PROVIDES = "${@get_mender_capsule_artifact_clears_provides(d)}"
_MENDER_CAPSULE_DEPENDS = "${@get_mender_capsule_artifact_depends(d)}"

# --------------------------- END OF CONFIGURATION -----------------------------
do_image_mender_capsule[depends] += "mender-artifact-native:do_populate_sysroot"

IMAGE_CMD:mender-capsule () {
    set -x

    if [ -z "${MENDER_ARTIFACT_CAPSULE_NAME}" ]; then
        bbfatal "Need to define MENDER_ARTIFACT_CAPSULE_NAME variable."
    fi

    if [ -z "${UEFI_CAPSULE}" ]; then
        bbfatal "Need to define UEFI_CAPSULE variable."
    fi

    if [ -z "${MENDER_DEVICE_TYPES_COMPATIBLE}" ]; then
        bbfatal "MENDER_DEVICE_TYPES_COMPATIBLE variable cannot be empty."
    fi

    if [ "${_MENDER_CAPSULE_PROVIDES}" = "None" ]; then
        bbfatal "MENDER_ARTIFACT_CAPSULE_PROVIDES variable cannot be empty."
    fi

    extra_args=""

    for dev in ${MENDER_DEVICE_TYPES_COMPATIBLE}; do
        extra_args="$extra_args -t $dev"
    done

    if [ -n "${MENDER_ARTIFACT_SIGNING_KEY}" ]; then
        extra_args="$extra_args -k ${MENDER_ARTIFACT_SIGNING_KEY}"
    fi

    if [ -n "${MENDER_ARTIFACT_CAPSULE_NAME_DEPENDS}" ]; then
        cmd=""
        apply_arguments "--artifact-name-depends" "${MENDER_ARTIFACT_CAPSULE_NAME_DEPENDS}"
        extra_args="$extra_args  $cmd"
    fi

    provides="${_MENDER_CAPSULE_PROVIDES}"
    extra_args="$extra_args  $provides"

    clears_provides="${_MENDER_CAPSULE_CLEARS_PROVIDES}"
    extra_args="$extra_args  $clears_provides"

    if [ "${_MENDER_CAPSULE_DEPENDS}" != "None" ]; then
        depends="${_MENDER_CAPSULE_DEPENDS}"
        extra_args="$extra_args  $depends"
    fi

    mender-artifact write module-image \
        -n ${MENDER_ARTIFACT_CAPSULE_NAME} \
        $extra_args \
        -T uefi-capsule \
        -f ${IMGDEPLOYDIR}/${UEFI_CAPSULE} \
        -o ${IMGDEPLOYDIR}/${IMAGE_NAME}${IMAGE_NAME_SUFFIX}-uefi-capsule.mender \
        --software-filesystem uefi \
        --no-default-clears-provides \
        --no-default-software-version
}

# The UEFI capsule generation class should be executed before this class
# can generate a mender artifact for it.
IMAGE_TYPEDEP:mender-capsule:append = " uefi_capsule"
