# This is a dummy recipe, only meant to populate a sysroot that the tests can
# use, and not meant for real building.

DEPENDS = "mender-artifact-native e2fsprogs-native util-linux-native mtools-native swig-native"

LICENSE = "Apache-2.0"

do_compile() {
    bbfatal 'This is not meant to be built, should be invoked with "-c prepare_recipe_sysroot" only.'
}
