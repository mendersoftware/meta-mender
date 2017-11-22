#!/bin/bash

# This script is just used to establish the ssh connection and run the tests.
set -e

function run_tests() {
  cp $BBB_IMAGE_DIR/core-image-base-beaglebone-yocto.sdimg \
     ./core-image-base-beaglebone-yocto-modified-testing.sdimg
  bash prepare_ext4_testing.sh
  py.test --bbb --host=127.0.0.1:12345 --sdimg-location=`pwd` --junit-xml=results.xml
}

function finish {
  kill -9 $PID
}

trap finish EXIT
for i in {1...5};
  do ssh -Cfo ExitOnForwardFailure=yes -o StrictHostKeyChecking=no bbb@wmd.no -L 12345:localhost:12345 -N
  PID=$(pgrep -f '12345:localhost:12345')
  if [ "$PID" -gt 0 ];
    then
      run_tests
      exit 0
  fi
done

echo "Failed to establish ssh tunnel." 1>&2
