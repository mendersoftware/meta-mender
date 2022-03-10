# meta-mender

This Yocto meta layer contains all the recipes needed to build the Mender client into a Yocto image.

For instructions on using this meta layer as part of a Yocto build environment, please see [the Mender documentation](https://docs.mender.io/system-updates-yocto-project).

## Maintenance strategy

The repository follows the release-named branch strategy.

### Current branch state

Branch `krogoth` is in **end of life** maintenance.

### Maintenance states

A branch can be in one of the following maintenance states:

| State | Maintenance level |
| :---- | :---------------- |
| bleeding edge | Expect breakage as we're working on things. No guarantees for functionality at any given point in time. |
| development | Development once it has stabilized is applied here. Not recommended for production, breakage is considered a bug and will be fixed. Feature submissions should always be applied here first. |
| stable | Ready for production. Stability takes precedence over features. |
| end of life | No maintenance. Expect increasing security problems and breakage. Updating to a stable branch is highly recommended. |

## Contributing

We welcome and ask for your contribution. If you would like to contribute to Mender, please read our guide on how to best get started [contributing code or documentation](https://github.com/mendersoftware/mender/blob/master/CONTRIBUTING.md).
