
# softhsm opensc gnutls p11-kit libp11 are needed for MEN-3905
# to access the private key from HSM (emulated via SoftHSM2)
# * softhsm: SoftHSM2, a software emulation of a hardware security module
# * gnutls: required for p11tool for accessing the key for testing, depends on p11-kit
# * libp11: OpenSSL ENGINE plugin PKCS#11 implementation, depends on p11-kit
#           for the OpenSSL to load the lib and access the key from the HSM
# * opensc: pkcs11-tool for initialization of token
# * gnutls-bin: provides p11tool for getting the contents of the token
# * pkcs11-provider is a third-party implementation of a PKCS#11 provider for OpenSSLv3
DEPENDS:append:mender-image:qemuall = " softhsm opensc gnutls p11-kit libp11"
RDEPENDS:${PN}:append:mender-image:qemuall = " softhsm opensc gnutls p11-kit libp11 gnutls-bin pkcs11-provider"

# Needed for the TestFaultTolerance tests in the integration repository.
RDEPENDS:${PN}:append:mender-image:qemuall = " \
    kernel-module-ipt-reject \
    kernel-module-ts-bm \
    kernel-module-xt-string \
"
