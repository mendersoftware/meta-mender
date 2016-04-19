#!/bin/bash

# This script is just used to establish the ssh connection and run the tests.

function run_tests() {
  cp /home/jenkins/workspace/yoctobuild/build/tmp/deploy/images/beaglebone/core-image-base-beaglebone.sdimg \
     ./core-image-base-beaglebone-modified-testing.sdimg
  bash prepare_ext3_testing.sh
  py.test --bbb --host=127.0.0.1:12345 --sdimg-location=`pwd`
}

function finish {
  kill -9 $PID
}

trap finish EXIT
for i in {1...5};
  do ssh -Cfo ExitOnForwardFailure=yes bbb@wmd.no -L 12345:localhost:12345 -N
  PID=$(pgrep -f '12345:localhost:12345')
  if [ "$PID" -gt 0 ];
    then
      run_tests
      exit 0
  fi
done

echo "Failed to establish ssh tunnel." 1>&2
