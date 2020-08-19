# meta-mender

This Yocto meta layer contains all the recipes needed to build the Mender client into a Yocto image.

For instructions on using this meta layer as part of a Yocto build environment, please see [the Mender documentation](https://docs.mender.io/system-updates-yocto-project).

## Supported layers

The following layers in this repository are officially supported by Mender:

* `meta-mender-core` (Core components of Mender)
* `meta-mender-demo` (Demo layer. Not intended for production)
* `meta-mender-raspberrypi` (Raspberry Pi 3 board support)
* `meta-mender-raspberrypi-demo` (Raspberry Pi 3 demo-board modifications)
* `meta-mender-qemu` (QEMU emulator board support)

The rest of the layers are community supported, and the response to issues may vary.

## Contributing

We welcome and ask for your contribution. If you would like to contribute to Mender, please read our guide on how to best get started [contributing code or documentation](https://github.com/mendersoftware/mender/blob/master/CONTRIBUTING.md).
