## meta-mender-selftest

OE selftest layer for mender Yocto support. Before using it, you need to add it
to `BBLAYERS` like this:

```
BBLAYERS ?= " \
  ...
  <your-path>/meta-mender/meta-mender-selftest \
  ...
```

Tests can be listed with `oe-selftest --list-tests-by module mender`. Individual
tests are run by `oe-selftest -r mender.Mender.test_hello`. See `oe-selftest
--help` for details.
