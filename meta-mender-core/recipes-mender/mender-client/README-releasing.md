# Making a new release recipe

1. Copy the most recent recipe from an earlier release to the new file name, for
   example:

   ```
   cp mender_4.0.0.bb mender_4.0.1.bb
   ```

2. Edit the `branch` setting in the `SRC_URI` variable in the name, setting it
   to correct branch for the release. Yes, *branch*, not tag, that comes later.

3. Change the `Tag` comment to mention the correct tag.

4. Change the `SRCREV` to point to the correct revision of the tag you're
   releasing. `git show 1.2.2` will show you the revision.

5. Update the license checksum in `LIC_FILES_CHKSUM` using
   [`make_bitbake_license_list.sh`](https://github.com/mendersoftware/mendertesting/blob/master/utils/make_bitbake_license_list.sh).
   If it results in a change, *make sure* that the listed licenses indeed match
   the licenses listed in `LICENSE`.

6. Set recipe version preference:

   * For beta releases, add this to the bottom of the file.

     ```
     # Downprioritize this recipe in version selections.
     DEFAULT_PREFERENCE = "-1"
     ```

   * For non-beta releases, make sure to remove the above block.

7. Remember to repeat the same procedure for `mender-artifact`, if applicable.
