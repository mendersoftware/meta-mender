# This recipe is not actually used for the Toradex boards. We have a different
# PREFERRED_PROVIDER but the recipe is still parsed and will generate a parse
# error if we don't explicitly disable this.
MENDER_UBOOT_AUTO_CONFIGURE = "0"
