# meta-mender

This document outlines the steps needed to build a Yocto image containing a
testable version of `Mender`, including the required partitioning and boot
configuration.  It is possible to build the image for both Qemu and Beaglebone
Black using the the ```vexpress-qemu``` or ```beaglebone``` machine type
respectively.


What is Mender
==============

A detailed description of Mender is provided in the [mender
repository](https://github.com/mendersoftware/mender).


Overview
========

This layer contains all the needed recipes to build the Mender Go binary as a
part of the Yocto image. It currently supports cross-compiling Mender for ARM
devices using Go 1.4 and 1.5.

As Mender is a framework not just a standalone application it requires the
bootloader and partition layout set up in a specific way. That's why it is
recommended to use Yocto for building a complete image containing all the needed
dependencies and configuration.

Detailed instructions and recipes needed for building a self-containing image
can be found later in this document.


Dependencies
============

This layer depends on:

```
  URI: git://git.yoctoproject.org/poky
  branch: master or jethro

  URI: git://github.com/mendersoftware/meta-mender
  branch: master

  URI: git://github.com/mem/oe-meta-go
  branch: master
```

Table of  contents:
=========
1. Pre-configuration
2. Yocto build configuration
3. Image building for Qemu
4. Booting the images with Qemu
5. Image building for Beaglebone Black
6. Booting the images with Beaglebone
7. Testing OTA image update
8. Mender overview
9. Project roadmap


1. Pre-configuration
====================

We first need to clone the latest Yocto sources from:

```
git://git.yoctoproject.org/git/poky
```

Having done that, clone the rest of the needed dependencies into the top level
of the Yocto build tree (usually yocto/poky). All the required dependencies are
provided in the 'Dependencies' section above. At the moment, the needed Yocto
layers for building a complete image are:

```
git://github.com/mendersoftware/meta-mender
git://github.com/mem/oe-meta-go
```

After cloning these dependencies to the top of the build tree, the image can be
built by adding the location of the layers `meta-mender` and `oe-meta-go` to
`bblayers.conf`.

In order to do so, first create the build directory for Yocto and set build
environment:

```
    $ source oe-init-build-env
```

This should create the build environment and build directory, and running the
command should change the current directory to the build directory. In this
document, we assume that the name of the build directory is `build`.


2. Yocto build configuration
============================

In order to support building Mender, the following changes are needed in the
```conf/local.conf``` file:

```
    INHERIT += "mender-install"
    MACHINE ??= "vexpress-qemu"
```

for building the image that will be run on the Qemu machine or

```
    INHERIT += "mender-install"
    MACHINE ??= "beaglebone"
```

for building image supported by Beaglebone Black.

The layers used for building the image need to be included.  In order to do so,
edit `conf/bblayers.conf` and make sure that `BBLAYERS` looks like the
following:

```
    BBLAYERS ?= " \
      <YOCTO-INSTALL-DIR>/yocto/poky/meta \
      <YOCTO-INSTALL-DIR>/yocto/poky/meta-yocto \
      <YOCTO-INSTALL-DIR>/yocto/poky/meta-yocto-bsp \
      <YOCTO-INSTALL-DIR>/yocto/poky/meta-mender \
      <YOCTO-INSTALL-DIR>/yocto/poky/oe-meta-go \
      "
```


3. Building image for Qemu
==========================

Once all the configuration steps are done, the image can be built like this:

```
    $ bitbake core-image-full-cmdline
```

This will build the `core-image-full-cmdline` image type. It is possible to
build other image types, but for the simplicity of this document we will assume
that `core-image-full-cmdline` is the selected type.

At the end of a successful build, the image can be tested in qemu.  The images
and build artifacts are placed in `tmp/deploy/images/vexpress-qemu/`. The
directory should contain a file named
```core-image-full-cmdline-vexpress-qemu.sdimg```, which is an image that
contains a boot partition and two other partitions, each with the kernel and
rootfs.  This image will be used later to test Mender with qemu (more on that in
the section 'Booting the images with Qemu' below).

For more information about getting started with Yocto, it is recommended to read
the [Yocto Project Quick Start
guide](http://www.yoctoproject.org/docs/2.0/yocto-project-qs/yocto-project-qs.html).


4. Booting the images with Qemu
===============================

This layer contains bootable Yocto images, which can be used to boot Mender
directly using qemu. In order to simplify the boot process there are qemu boot
scripts provided in the directory `meta-mender/scripts`. To boot Mender, follow
the instructions below:

```
    $ cd ../meta-mender/scripts
    $ ./mender-qemu
```

The above should start qemu and boot the kernel and rootfs from the active
partition.  There should also be an inactive partition available where the
update will be stored.

If you want to forcibly close the emulator without shutting it down properly,
press "Ctrl-c x". "Ctrl-c" will not work because it is intercepted by the shell
inside the emulator.

5. Image building for Beaglebone Black
======================================

In order to build image that can be run on Beaglebone Black use following
command should be used:

```
    $ bitbake core-image-base
```

The reason why the base image is built is the simplicity of the later booting
and testing process. With the base image all needed boot and configuration files
are created by Yocto and copied to appropriate locations in the boot partition
and the root file system. For more information about differences while using
different image types please see [official Yocto Beaglebone support
page](https://www.yoctoproject.org/downloads/bsps/daisy16/beaglebone).


6. Booting the images with Beaglebone
=====================================

With the Mender layer configuration besides of the standard boot files and the
rootfs additional image type - sdimg - is created. It is availabe in the deploy
directory after build
(```./tmp/deploy/images/beaglebone/core-image-base-beaglebone.sdimg```). This is
a partitioned image that can be stored directly into SD card. For more
information about the exact content of the image and detailed information about
partitions layout please see [sdimg class
documentation](https://github.com/mendersoftware/meta-mender/blob/master/classes/sdimg.bbclass).

To copy the sd image to SD card you can use following command:

```
sudo dd if=./tmp/deploy/images/beaglebone/core-image-base-beaglebone.sdimg of=/dev/mmcblk0 bs=1M
```

To run above command you need to be in the Yocto image build directory and you
need to make sure that you are copying the image to correct of device. After
successful copy you can remove the SD card and insert to the Beaglebone.
IMPORTANT: The standard Beaglebone booting process will cause that the
bootloader from internal flash storage will be used. In order to use the
bootloader from SD card make sure that S2 (boot) button is pressed while
powering on your Beaglebone.

![Booring Beaglebone from SD
 card](https://github.com/mendersoftware/meta-mender/raw/master/beaglebone.black.sdboot.jpg
 "Booring Beaglebone from SD card").


7. Testing OTA image update
===========================

To apply an actual update, store the image on a local web server and use a URL
when calling `mender -rootfs` (see below). Python provides a very simply
out-of-the-box web server suitable for this purpose (the below command assumes
the current directory is poky):

```
    $ cd build/tmp/deploy/images/vexpress-qemu
    $ python -m SimpleHTTPServer 8000
```

On the device, attempt an upgrade using the following command:

```
    $ mender -rootfs http://10.0.2.2:8000/core-image-full-cmdline-vexpress-qemu.ext3
```

Having that done reboot the system:

```
    $ reboot
```

Now the system should boot the kernel and corresponding rootfs from the
previously inactive partition where the update was copied (after first update it
should be `mmcblk0p3`). Please note that the previously active partition was
`mmcblk0p2`.

If the update was successful and (currently manual) verification of the
installation is successful, run:

```
    $ mender -commit
```

This ensures that the current kernel and rootfs pair will become the active. If
the change is not committed after the reboot, the kernel and rootfs will be
booted from the *previously active partition* (`mmcblk0p2`).

This is a mechanism for verifying the update and rolling-back to a previous
working version if the new image is broken.


8. Mender overview
==================

For more information of what Mender is and how it works, please see the
documentation in the [mender Github
repository](https://github.com/mendersoftware/mender) or visit [the official
Mender website](https://mender.io).



9. Project roadmap
==================

The update process currently consists of several manual steps.  There is ongoing
development to make it fully automated so that the image will be delivered to a
device automatically and the whole update and roll-back process will be
automatic.  There is also ongoing work on the server side of Mender, where it
will be possible to schedule image updates and get reports for the update status
for each and every device connected to the server.


