# Making a new release recipe

1. Copy the most recent recipe from an earlier release to the new file name, for
   example:

   ```
   cp mender-client_1.2.1.bb mender-client_1.2.2.bb
   ```

2. Edit the `branch` setting in the `SRC_URI` variable in the name, setting it
   to correct branch for the release. Yes, *branch*, not tag, that comes later.

3. Change the `Tag` comment to mention the correct tag.

4. Change the `SRCREV` to point to the correct revision of the tag you're
   releasing. `git show 1.2.2` will show you the revision.

5. Make sure that the md5 checksum of `LIC_FILES_CHKSUM.sha256` matches what is
   listed in the recipe. If you change it, *make sure* that the listed licenses
   indeed match the licenses we use.

6. Set recipe version preference:

   * For beta releases, add this to the bottom of the file.

     ```
     # Downprioritize this recipe in version selections.
     DEFAULT_PREFERENCE = "-1"
     ```

   * For non-beta releases, make sure to remove the above block.

7. Remember to repeat the same procedure for `mender-artifact`, if applicable.
