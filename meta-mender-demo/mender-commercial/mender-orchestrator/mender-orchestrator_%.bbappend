# Override topology file check to allow missing topology.yaml in SRC_URI
do_topology_file_check() {
    # Skip topology file check in demo - mender-orchestrator-support provides a pre-defined topology
    :
}

