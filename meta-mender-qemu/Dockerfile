# Usage of Docker image.
#
# While building:
# --build-arg VEXPRESS_IMAGE=<sdimg|vexpress-nor>
#       image to add to the Docker image
# --build-arg UBOOT_ELF=<u-boot.elf>
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

FROM opensuse:tumbleweed

# Install packages
RUN zypper up -y && \
    zypper install -y e2fsprogs qemu-arm python3 && \
    zypper clean -a

ARG VEXPRESS_IMAGE=scripts/docker/empty-file
ARG UBOOT_ELF=scripts/docker/empty-file

COPY $UBOOT_ELF ./u-boot.elf
COPY $VEXPRESS_IMAGE .

ADD scripts/mender-qemu ./
ADD scripts/docker/entrypoint.sh ./
ADD scripts/docker/setup-mender-configuration.py ./

# Delete images if they are empty. This is to save space if the artifacts are
# mounted on /mnt/build instead.
RUN if [ `stat -c %s core-image-full-cmdline-vexpress-qemu.sdimg` -eq 0 ]; then rm -f core-image-full-cmdline-vexpress-qemu.sdimg; fi
RUN if [ `stat -c %s core-image-full-cmdline-vexpress-qemu.vexpress-nor` -eq 0 ]; then rm -f core-image-full-cmdline-vexpress-qemu.vexpress-nor; fi
RUN if [ `stat -c %s u-boot.elf` -eq 0 ]; then rm -f u-boot.elf; fi

RUN chmod +x entrypoint.sh mender-qemu
EXPOSE 8822
ENTRYPOINT ["./entrypoint.sh"]
