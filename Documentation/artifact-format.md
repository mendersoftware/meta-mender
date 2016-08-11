Mender artifact file format
===========================

File extension: `.mender`

The format of the tar file is listed as a tree below. Note that there are some
restrictions on ordering of the files, described in the "Ordering" section.

```
-artifact.mender (tar format)
  |
  +---info
  |
  +---header.tar (or tar.gz, tar format)
  |    |
  |    +---header-info
  |    |
  |    +---type-info
  |    |
  |    +---meta-data
  |    |
  |    +---checksums
  |    |    +--<image file.sha25sum>
  |    |    +--<binary delta.sha256sum>
  |    |    `--...
  |    |
  |    +---signatures
  |    |    +--<image file.sig>
  |    |    +--<binary delta.sig>
  |    |    `--...
  |    |
  |    `---scripts
  |         |
  |         +---pre
  |         |    +--01_do_this
  |         |    +--02_do_that
  |         |    `--xx_ ...
  |         |
  |         +---post
  |         |    +--01_do_this
  |         |    +--02_do_that
  |         |    `--xx_ ...
  |         |
  |         `---check
  |              +--01_check_this
  |              +--02_check_that
  |              `--xx_ ...
  |
  `---data
       +--<image-file (ext4 or ext4.gz)>
       +--<binary delta, etc>
       `--...
```


info
----

Format: JSON

Contains the below content exactly:

```
{
  "format": "mender",
  "version": "1"
}
```

The `format` value is to confirm that this is indeed a Mender update file, and
the `version` value is a way to extend/change the format later if
needed. Currently there is only version 1, but this document may describe later
versions if they are created.


header.tar
----------

Format: tar

A tar file that contains various header files.

The reason the `info` file above is not part of this tar file is in case it is
decided to move away from `header.tar`, then it is important that the format
version is specified outside of `header.tar`.

Why is there a tar file inside a tar file? See the "Ordering" section.


### header-info

Format: JSON

`header-info` must be the first file within `header.tar`. Its content is:

```
{
  "type": "rootfs-image"
}
```

`type` is the type of update contained within the image. At the moment there is
only `rootfs-image`, but there may be others in the future, like `docker-image`
or something package based.


### type-info

Format: JSON

A file that provides information about the type of package contained within the
tar file. The contents of this file depends on the `type` specified in
`header-info`. For `rootfs-image` there is only one entry in this file, which is
the name of the image file inside `data` (without the `data` path). For
instance:

```
{
  "rootfs": "core-image-minimal-201608110900.ext4"
}
```

For other package types this file can contain for example number of files in the
`data` directory, if the update contains more than one. Or it can contain
network address(es) and credentials if Mender is to do a proxy update.


### meta-data

Format: JSON

Meta data about the image. This depends on the `type` in `header-info`. For
`rootfs-image` this is at minimum `ImageID` and `DeviceType`. For example:

```
{
  "DeviceType": "vexpress-qemu",
  "ImageID": "core-image-minimal-201608110900"
}
```

There may also be other meta data attributes specified.


### checksums

Format: Directory containing one checksum file for each file in `data`.

#### Checksum file

Format: Checksum

Each file must match the name of a file in `data` exactly, plus an appended
suffix which determines the type of checksum. For maximum compatibility, there
is only one checksum in each file. Currently, there is only one type of
checksum, `sha256`, which follows the format of the `sha256sum` tool. For
example:

```
b6207e04cbdd57b12f22591cca02c774463fe1fac2cb593f99b38a9e07cf050f  core-image-minimal-201608110900.ext4
```


### signatures

Format: Directory containing one signature file for each file in `data`.

#### Signature file

Format: TBD

Each file must match the name of a file in `data` exactly, plus an appended
suffix which determines the type of signature. For maximum compatibility, there
is only one signature in each file. Currently there are no signature types, this
still needs to be decided.


### scripts

Format: Directory containing two subdirectories, `pre` and `post`.

Either or both of the subdirectories can be missing, if there is no script of
that type.

#### scripts/pre

Format: Directory containing script files.

The script files must start with two digits following by an underscore, for
example `10_`, and are executed in numerically ascending order. Scripts that do
not follow this naming convention will cause the update to be interrupted with a
failure result.

##### scripts/pre files

Format: Any executable

Is run by Mender before the update begins. The script should not reboot nor
disrupt network connectivity, since at this point Mender will still be connected
to the server, expecting to receive the rest of the update contents,
particularly the `data` files.

The executable will run with `/` as the current directory, and if any script
returns a non-zero return code the update will stop and be marked as failed.

#### scripts/post

Format: Directory containing script files.

The script files must start with two digits following by an underscore, for
example `10_`, and are executed in numerically ascending order. Scripts that do
not follow this naming convention will cause the update to be interrupted with a
failure result.

##### scripts/post files

Format: Any executable

Is run by Mender after the update has been applied, but before it has been
marked as a success. This implies that the script will run using the updated
system.

The executable will run with `/` as the current directory, and if any script
returns a non-zero return code the update will be marked as a failure and Mender
will roll back to the previous image.


data
----

Format: Directory containing image files.

All files listed in the tar archive under the `data` directory must be after all
other files. If any non-`data` file is found after a `data` file, this will
cause the update to immediately fail.

The rationale behind failing if `data` files are not last is that the client
should know everything that is possible about the update *before* the payload
arrives. Receiving this knowledge later might be at a point where it's too late
to apply it, hence this precaution.

It is legal for an update file to not contain any `data` files at all. In such
cases it is expected that the update type in question will receive the update
payload by using alternative means, such as providing a download link in
`type-info`.


Ordering
========

Some ordering rules are enforced on the artifact tar file. For the outer tar
file:

| File/Directory | Ordering rule                  |
|----------------|--------------------------------|
| `info`         | First in `.mender` tar archive |
| `header.tar`   | After `info`                   |
| `data`         | After `header.tar`             |

For the embedded `header.tar` file:

| File/Directory | Ordering rule              |
|----------------|----------------------------|
| `header-info`  | First in `header.tar` file |
| `type-info`    | After `header-info`        |
| `meta-data`    | After `type-info`          |
| `checksums`    | After `type-info`          |
| `signatures`   | After `type-info`          |
| `scripts`      | After `type-info`          |
| `scripts/pre`  | No rules                   |
| `scripts/post` | No rules                   |

The fact that many files/directories inside `header.tar` have ambiguous rules
(`checksums` can be before or after `signatures`) implies that the order is not
strictly enforced for these entries. The client is expected to cache what it
needs during reading of `header.tar` even if reading out-of-order, and then
assembling the pieces when `header.tar` has been completely read.

So why do we have the `header.tar` tar file inside another tar file? The reason
is that order is important, and the files in the `data` directory need to come
last in order for the download to be efficient (by the time the main image
arrives, the client must already know everything in the header). Since the
number of files in the header can vary depending on what scripts are used and
whether signatures are enabled for example, it is better to group these together
in one indivisible unit which is the `header.tar` file, rather than being
"surprised" by a signature file that arrives after the data file. All this is
not a problem as long as the mender tool is used to manipulate the
`artifact.mender` file, but if anyone does a custom modification using regular
tar, this is important.


Compression
===========

`header.tar` as well as every file inside `data` can be compressed, and will
receive a suffix corresponding to the compression, such as `.gz`. Exact
compression method to be decided.
