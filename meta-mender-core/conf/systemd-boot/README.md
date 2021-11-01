# systemd-boot reference configuration

This configuration demonstrates support for systemd-boot on a QEMU system
via the OVMF UEFI firmware.

As tested, this systemd-boot support requires the meta-intel layer
to create suitable UEFI images.

## Setup

In your top-level BSP directory:

```shell
# enter Yocto environment
. poky/oe-init-build-env build

# copy the example configuration files
cp -v meta-mender/meta-mender-core/conf/systemd-boot/*.conf conf/
```

## Build

```shell
bitbake core-image-minimal
```

## Test

## QEMU

By default, the configuration is setup to be verified using QEMU:

```shell
imagedir=tmp/deploy/images/intel-corei7-64
runqemu nographic slirp ovmf \
	$imagedir/core-image-minimal-intel-corei7-64.uefiimg
```

**Note**: The `runqemu` on `zeus` required the following patch to
allow it to detect the `uefiimg` as a virtual machine image and
run the custom `systemd-boot` firmware:

```diff
diff --git a/scripts/runqemu b/scripts/runqemu
index a05facd0db..efd8fce668 100755
--- a/scripts/runqemu
+++ b/scripts/runqemu
@@ -180,7 +180,7 @@ class BaseConfig(object):
         self.wictypes = ('wic', 'wic.vmdk', 'wic.qcow2', 'wic.vdi')
         self.fstypes = ('ext2', 'ext3', 'ext4', 'jffs2', 'nfs', 'btrfs',
                         'cpio.gz', 'cpio', 'ramfs', 'tar.bz2', 'tar.gz')
-        self.vmtypes = ('hddimg', 'iso')
+        self.vmtypes = ('hddimg', 'iso', 'uefiimg')
         self.fsinfo = {}
         self.network_device = "-device e1000,netdev=net0,mac=@MAC@"
         # Use different mac section for tap and slirp to avoid
```

### Hardware

By adjusting the device in local.conf, the functionality can be verified
on real hardware using a bootable USB key:

```shell
bmaptool copy $imagedir/core-image-minimal-intel-corei7-64.uefiimg.bz2 /dev/sdX
```

# `systemd-boot` Modifications

The `systemd-boot` patch in meta-mender adds a check for A/B
configuration that, when found, determines the boot partition and
upgrade status.  The new `slot.h` header file contains the on-disk
configuration files.

Mimicing the `grub-mender-grubenv` package, two copies of the
configuration file are written to disk, providing redundancy against
corruption of the FAT-formatted EFI partition.

When a valid A/B configuration file is found, systemd-boot boots the
appropriate kernel image that has been installed on the EFI partition.

# User Space Support

The `systemd-mender-config` package provides `systemd-boot-printenv`
and `systemd-boot-setenv`.  These symlinks point at the `ab_setup.py`
script, which accesses the EFI partition, reads and writes the
configuration files, and updates the EFI kernel images.

In `dunfell`, additional symlinks are provided to from `fw_printenv` and
`fw_setenv`, supporting their usage as drop-in replacements for the
corresponding utilities provided in Mender-enabled systems using U-Boot
or GRUB.  After `dunfell`, the symlinks have been dropped, as the Mender
tools were modified to call these tools directly.

While suitable for prototyping, the `ab_setup.py` script deserves to be
reimplemented in C to eliminate the dependency on Python, once the
on-disk format is stable.  At that time, the systemd-boot environment
file operations (`slot.c`) could be encapsulated in a library and
re-used by both systemd-boot and the user space tool.
