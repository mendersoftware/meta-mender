# meta-mender-raspberrypi-demo
This README file contains information on the contents of the /meta-mender/meta-raspberrypi-demo layer.

Please see the corresponding sections below for details.

## Dependencies
============

  URI: git://git.yoctoproject.org/meta-raspberrypi
  branch: rocko
  revision: HEAD:20358ec57a8744b0a02da77b283620fb718b0ee0

  URI: git://git.yoctoproject.org/poky
  branch: rocko
  revision: HEAD:fdeecc901196bbccd7c5b1ea4268a2cf56764a62

  URI: git@github.com:mendersoftware/meta-mender.git
  branch: rocko

  URI: git://git.openembedded.org/meta-openembedded
  branch: rocko

## Build Instructions
Add the meta-raspberrypi-demo layer to your bblayer.conf, along with all it's dependencies and build an image which inherits from the base image in the meta-layer. Also remember to read the instructions in all the dependent layers. Also in order to connect to a wireless network, remember to set
```
MENDER_DEMO_WIFI_SSID ?= "ssid"
MENDER_DEMO_WIFI_PASSKEY ?= "password"
```
where 'ssid' and 'password' is replaced with your wifi's ssid and password accordingly.

