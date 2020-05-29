################################################################################
#
# Utility library for functions used by mender classes
#
################################################################################

# Get the full path of a script in a meta-layer scripts/ directory
def get_script_path(d, script_name):
    script_path = ""

    # Search BBPATH, which includes all meta layers
    for path in d.getVar("BBPATH").split(":"):
        bitbake_path = os.path.join(path, "scripts", script_name)
        if os.path.exists(bitbake_path):
            script_path = bitbake_path
            break

    return script_path
