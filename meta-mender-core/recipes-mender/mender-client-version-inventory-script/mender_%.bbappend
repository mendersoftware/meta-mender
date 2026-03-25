# This provides a way to configure Mender Client's dependency
# on mender-client-version-inventory-script
#
# By default, strict conflicts are enabled with RDEPENDS, meaning the build will fail
# if there are package conflicts.
#
# To enable non-strict conflicts with RRECOMMENDS uncomment the line below:
#
# PACKAGECONFIG:remove:pn-mender = "version-inventory-script-strict"
