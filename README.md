# meta-mender

This README file contains information about the Yocto layer designed for building the Mender client application as a part of the Yocto image.
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
1. What is Mender
2. Overview
3. Using Mender


What is Mender
==============

A detailed description of Mender is provided in the [mender repository](https://github.com/mendersoftware/mender).


Overview
========

This layer contains all the needed recipes to build the Mender Go binary as a part of the Yocto image. It currently supports cross-compiling Mender for ARM devices using Go 1.4 and 1.5.

As Mender is a framework not just a standalone application it requires the bootloader and partition layout set up in a specific way. That's why it is recommended to
use Yocto for building a complete image containing all the needed dependencies and configuration.

Detailed instructions and recipes needed for building a self-containing image can be found in [meta-mender-qemu repository](https://github.com/mendersoftware/meta-mender-qemu).


Using Mender
============

To quickly get started, Mender can be tested using the qemu emulator. Detailed instructions for how to build a Yocto image that can be run and tested in qemu are provided in the [meta-mender-qemu repository](https://github.com/mendersoftware/meta-mender-qemu).

