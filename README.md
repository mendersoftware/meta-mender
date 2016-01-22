# meta-mender

This README file contains information about the Yocto layer designed for building Mender client application as a part of the Yocto image.
Please see the corresponding sections below for more details.

Dependencies
============

This layer depends on:

  URI: git://git.yoctoproject.org/xxxx
  branch: master

  URI: git://github.com/mem/oe-meta-go
  branch: master



Table of  contents:
===================
1. Overview
2. What is Mender
3. Using Mender



Overview
========

This layer contains all the needed recipes to build Mender Go binary as a part of the Yocto image. Currently we are supporting
cross-compiling Mender for ARM devices using Go 1.4 and 1.5.

As Mender is a framework not just a standalone application it requires the bootloader and partition layout set up in a specific way. That's why it is recommended to
use Yocto for building a complete image containing all the needed dependencies and configuration.

Detailed instructions and recipes needed for building a self-containing image can be found in [meta-mender-qemu repository](https://github.com/mendersoftware/meta-mender-qemu).


What is Mender
==============

Detailed Mender description is provided in [mender repository](https://github.com/mendersoftware/mender).


Using Mender
============

To quickly get started, Mender can be tested using the qemu emulator. Detailed instructions how to build a Yocto image that can be run and tested in qemu are provided in the [meta-mender-qemu repository](https://github.com/mendersoftware/meta-mender-qemu).

