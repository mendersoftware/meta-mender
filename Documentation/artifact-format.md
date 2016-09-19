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
  +---header.tar.xz (tar format)
  |    |
  |    +---header-info
  |    |
  |    `---headers
  |         |
  |         +---0000
  |         |    |
  |         |    +---files
  |         |    |
  |         |    +---type-info
  |         |    |
  |         |    +---meta-data
  |         |    |
  |         |    +---checksums
  |         |    |    +--<image file.sha25sum>
  |         |    |    +--<binary delta.sha256sum>
  |         |    |    `--...
  |         |    |
  |         |    +---signatures
  |         |    |    +--<image file.sig>
  |         |    |    +--<binary delta.sig>
  |         |    |    `--...
  |         |    |
  |         |    `---scripts
  |         |         |
  |         |         +---pre
  |         |         |    +--01_do_this
  |         |         |    +--02_do_that
  |         |         |    `--xx_ ...
  |         |         |
  |         |         +---post
  |         |         |    +--01_do_this
  |         |         |    +--02_do_that
  |         |         |    `--xx_ ...
  |         |         |
  |         |         `---check
  |         |              +--01_check_this
  |         |              +--02_check_that
  |         |              `--xx_ ...
  |         |
  |         +---0001
  |         |    |
  |         |    `---<more headers>
  |         |
  |         `---000n ...
  |
  `---data
       |
       +---0000.tar.xz
       |    +--<image-file (ext4)>
       |    +--<binary delta, etc>
       |    `--...
       |
       +---0001.tar.xz
       |    +--<image-file (ext4)>
       |    +--<binary delta, etc>
       |    `--...
       |
       +---000n.tar.xz ...
            `--...
```


info
----

Format: JSON

Contains the below content exactly:

```
{
  "format": "mender",
  "version": 1
}
```

The `format` value is to confirm that this is indeed a Mender update file, and
the `version` value is a way to extend/change the format later if needed.
Currently there is only version 1, but this document may describe later versions
if they are created.


header.tar.xz
-------------

Format: tar

A tar file that contains various header files.

The reason the `info` file above is not part of this tar file is in case it is
decided to move away from `header.tar.xz`, then it is important that the format
version is specified outside of `header.tar.xz`.

Why is there a tar file inside a tar file? See the "Ordering" section.


### header-info

Format: JSON

`header-info` must be the first file within `header.tar.xz`. Its content is:

```
{
  "updates": [
    {
      "type": "rootfs-image"
    },
    {
      "type": "rootfs-image"
    },
    {
      ...
    }
  ]
}
```

The `updates` list is a list of all the updates contained within the
artifact. The intention of having multiple updates is to allow proxy based
updates to deploy to several different hosts at the same time. However, for
updates downloaded to single devices, there will usually be only one.

`type` is the type of update contained within the image. At the moment there is
only `rootfs-image`, but there may be others in the future, like `docker-image`
or something package based.

The remaining entries in `header.tar.xz` are then organized in buckets under
`headers/xxxx` folders, where `xxxx` are four digits, starting from zero, and
corresponding to each element `updates` inside `header-info`, in order. The
following sub sections define each field under each such bucket.


### files

Format: JSON

Contains a JSON list of file names that make up the payload for this update (the
image file / package file / etc.), listed as bare file names. There may be one
or multiple files listed.  For example:

```
{ "files" : ["core-image-minimal-201608110900.ext4", "core-image-base-201608110900.ext4"]}
```


### type-info

Format: JSON

A file that provides information about the type of package contained within the
tar file. The first and the only required entry is the type of the update 
corresponding to the type in `header-info` file. Rest of the content depends on the 
`type` specified in `header-info`. For `rootfs-image` there is no additional fields 
required. For instance:

```
{
  "type": "rootfs-image"
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

Format: Directory containing one checksum file for each file listed in the
`files` header.

It is legal for an update not to have any checksums.

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

Format: Directory containing one signature file for each file listed in the
`files` header.

It is legal for an update not to have any signatures.

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

Is run by Mender after the update has been applied, but before the `check`
scripts. This implies that the script will run using the updated system. The
scripts are allowed to make changes to the system.

The executable will run with `/` as the current directory, and if any script
returns a non-zero return code the update will be marked as a failure and Mender
will roll back to the previous image.

#### scripts/check

Format: Directory containing script files.

The script files must start with two digits following by an underscore, for
example `10_`, and are executed in numerically ascending order. Scripts that do
not follow this naming convention will cause the update to be interrupted with a
failure result.

##### scripts/check files

Format: Any executable

Is run by Mender after the `post` scripts, but before the update has been marked
as a success. This implies that the script will run using the updated
system. Unlike the `post` scripts, `check` scripts should not make any changes
to the system, only verify acceptance conditions for the update.

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

Each file in the `data` folder should be a file of the format `xxxx.tar.xz`,
where `xxxx` are four digits corresponding to each entry in the `updates` list
in `header-info`, in order. Each file inside the `xxxx.tar.xz` archive should be
a file name corresponding exactly to a filename from the `files` header under
the corresponding header bucket. If the list of files found inside `xxxx.tar.xz`
is in any way different from the files listed in `files`, an error should be
produced and the update should fail.


Ordering
========

Some ordering rules are enforced on the artifact tar file. For the outer tar
file:

| File/Directory  | Ordering rule                  |
|-----------------|--------------------------------|
| `info`          | First in `.mender` tar archive |
| `header.tar.xz` | After `info`                   |
| `data`          | After `header.tar.xz`          |

For the embedded `header.tar.xz` file:

| File/Directory | Ordering rule                 |
|----------------|-------------------------------|
| `header-info`  | First in `header.tar.xz` file |
| `headers`      | After `header-info`           |
| `files`        | First in every `xxxx` bucket  |
| `type-info`    | After `files`                 |
| `meta-data`    | After `type-info`             |
| `checksums`    | After `type-info`             |
| `signatures`   | After `type-info`             |
| `scripts`      | After `type-info`             |
| `scripts/pre`  | No rules                      |
| `scripts/post` | No rules                      |

The fact that many files/directories inside `header.tar.xz` have ambiguous rules
(`checksums` can be before or after `signatures`) implies that the order is not
strictly enforced for these entries. The client is expected to cache what it
needs during reading of `header.tar.xz` even if reading out-of-order, and then
assembling the pieces when `header.tar.xz` has been completely read.

So why do we have the `header.tar.xz` tar file inside another tar file? The reason
is that order is important, and the files in the `data` directory need to come
last in order for the download to be efficient (by the time the main image
arrives, the client must already know everything in the header). Since the
number of files in the header can vary depending on what scripts are used and
whether signatures are enabled for example, it is better to group these together
in one indivisible unit which is the `header.tar.xz` file, rather than being
"surprised" by a signature file that arrives after the data file. All this is
not a problem as long as the mender tool is used to manipulate the
`artifact.mender` file, but if anyone does a custom modification using regular
tar, this is important.


Compression
===========

All file tree components ending in `.xz` in the tree displayed above should be
compressed, and the suffix corresponds to the compression method. Exact
compression method to be decided.
