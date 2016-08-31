Acceptance tests for Mender
===========================


Prerequisites
-------------

* PyTest
* [Fabric](http://www.fabfile.org)


Running
-------

To run these tests you need to be in the tests/acceptance directory, and the
meta-mender-qemu layer must be next to the meta-mender layer (this layer). In
addition you must provide a symlink, "image.dat", pointing to image you want to
test. Normally this is the "*.ext4" image inside of your build directory, in
"tmp/deploy/images/vexpress-qemu". Then run the tests with:

```
$ py.test
```


Known issues
------------

The tests currently leave behind a modified image. They won't currently pass if
you run them again a second time without rebuilding the image first.


Troubleshooting
---------------

A common problem is that the SSH server inside the image stops working. This
often happens if you run the tests several times after one another. It is
unknown why, but rebuilding the Yocto image seems to make the problem go away.
