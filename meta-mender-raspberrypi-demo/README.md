# meta-mender-raspberrypi-demo
This README file contains information on the contents of the /meta-mender/meta-raspberrypi-demo layer.

Please see the corresponding sections below for details.

## Dependencies

```
  URI: git://git.yoctoproject.org/meta-raspberrypi
  branch: master

  URI: git://git.yoctoproject.org/poky
  branch: master

  URI: git@github.com:mendersoftware/meta-mender.git
  branch: master

  URI: git://git.openembedded.org/meta-openembedded
  branch: master
```

## Build Instructions
Add the meta-raspberrypi-demo layer to your bblayer.conf, along with all it's dependencies and build an image which inherits from the base image in the meta-layer. Also remember to read the instructions in all the dependent layers. Also in order to connect to a wireless network, remember to set
```
MENDER_DEMO_WIFI_SSID ?= "ssid"
MENDER_DEMO_WIFI_PASSKEY ?= "password"
```
where 'ssid' and 'password' is replaced with your wifi's ssid and password accordingly.

