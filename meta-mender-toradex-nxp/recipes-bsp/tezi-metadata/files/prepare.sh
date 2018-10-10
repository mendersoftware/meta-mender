#!/bin/sh
#
# (c) Toradex AG 2016
#
# Empty in-field hardware update script
#

PRODUCT_ID=$1
BOARD_REV=$2
SERIAL=$3
IMAGE_FOLDER=$4

error_exit () {
	echo "$1" 1>&2
	exit 1
}

exit 0
