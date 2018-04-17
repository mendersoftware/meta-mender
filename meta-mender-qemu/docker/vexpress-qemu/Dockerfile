# Usage of Docker image.
#
# While building:
# --build-arg DISK_IMAGE=<sdimg>
#       image to add to the Docker image
# --build-arg BOOTLOADER=<u-boot.elf>
#       U-Boot ELF image to add to Docker image.
#
# While launching:
# -v $BUILDDIR:/mnt/build:ro
#       Use BUILDDIR from a poky build as image input.
# -v <config-dir>:/mnt/config:ro
#       Use server.crt and/or artifact-verify-key.pem from config-dir, if it exists.
# -e SERVER_URL=https://whatever.mender.io
#       Use SERVER_URL as server address for client.
# -e TENANT_TOKEN=<token>
#       Use token as tenant token for client.

FROM alpine:3.6

# Install packages
RUN apk update && apk upgrade && \
    apk add util-linux \
            bash e2fsprogs-extra python3 && \
    rm -rf /var/cache/apk/*

# Install qemu from source
RUN apk update && apk add --virtual build-dependencies \
    alsa-lib-dev \
    bison \
    curl-dev \
    flex \
	  glib-dev \
	  glib-static \
	  gnutls-dev \
	  gtk+3.0-dev \
	  libaio-dev \
	  libcap-dev \
	  libcap-ng-dev \
	  libjpeg-turbo-dev \
	  libnfs-dev \
	  libpng-dev \
	  libssh2-dev \
	  libusb-dev \
	  linux-headers \
	  lzo-dev \
	  ncurses-dev \
	  paxmark \
	  snappy-dev \
	  spice-dev \
	  texinfo \
	  usbredir-dev \
	  util-linux-dev \
	  vde2-dev \
	  xfsprogs-dev \
	  zlib-dev \
    git \
    alpine-sdk \
    && \
    git clone --progress -b qemu-system-reset-race-fix git://github.com/mendersoftware/qemu.git && \
    cd qemu && \
    git submodule update --init dtc && \
    ./configure --target-list=arm-softmmu \
                --disable-werror \
                --prefix=/usr \
                --localstatedir=/var \
		            --sysconfdir=/etc \
		            --libexecdir=/usr/lib/qemu \
		            --disable-glusterfs \
		            --disable-debug-info \
		            --disable-bsd-user \
		            --disable-werror \
		            --disable-sdl \
		            --disable-xen \
                --disable-attr \
                --disable-gtk \
                && \
    make install -j4 V=1 && \
    cd .. && \
    rm -rf qemu && \
    apk del build-dependencies && \
    apk add so:libaio.so.1 \
            so:libasound.so.2 \
            so:libbz2.so.1 \
            so:libc.musl-x86_64.so.1 \
            so:libcurl.so.4 \
            so:libepoxy.so.0 \
            so:libgbm.so.1 \
            so:libgcc_s.so.1 \
            so:libglib-2.0.so.0 \
            so:libgnutls.so.30 \
            so:libjpeg.so.8 \
            so:liblzo2.so.2 \
            so:libncursesw.so.6 \
            so:libnettle.so.6 \
            so:libnfs.so.8 \
            so:libpixman-1.so.0 \
            so:libpng16.so.16 \
            so:libsnappy.so.1 \
            so:libspice-server.so.1 \
            so:libssh2.so.1 \
            so:libstdc++.so.6 \
            so:libusb-1.0.so.0 \
            so:libusbredirparser.so.1 \
            so:libvdeplug.so.3 \
            so:libz.so.1 \
    rm -rf /var/cache/apk/*

RUN echo vexpress-qemu > /machine.txt

ARG DISK_IMAGE=scripts/docker/empty-file
ARG BOOTLOADER=scripts/docker/empty-file

COPY $BOOTLOADER ./u-boot.elf
COPY $DISK_IMAGE .

ADD scripts/mender-qemu ./
ADD scripts/docker/entrypoint.sh ./
ADD scripts/docker/setup-mender-configuration.py ./
ADD env.txt ./

# Delete images if they are empty. This is to save space if the artifacts are
# mounted on /mnt/build instead.
RUN if [ `stat -c %s core-image-full-cmdline-vexpress-qemu.sdimg` -eq 0 ]; then rm -f core-image-full-cmdline-vexpress-qemu.sdimg; fi
RUN if [ `stat -c %s u-boot.elf` -eq 0 ]; then rm -f u-boot.elf; fi

RUN chmod +x entrypoint.sh mender-qemu
EXPOSE 8822
ENTRYPOINT ["./entrypoint.sh"]
