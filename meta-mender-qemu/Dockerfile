FROM alpine:3.4

# Install QEMU
RUN apk update && apk upgrade && \
    apk add qemu-system-arm bash && \
    rm -rf /var/cache/apk/*

# Use: --build-arg VEXPRESS_IMAGE=core-image-full-cmdline-vexpress-qemu.sdimg
# --build-arg UBOOT_ELF=u-boot.elf when building
# Or use "docker run -v $BUILDDIR:/mnt/build" to get build artifacts from local
# hard drive.
ARG VEXPRESS_IMAGE=scripts/docker/empty-file
ARG UBOOT_ELF=scripts/docker/empty-file

ADD $UBOOT_ELF ./u-boot.elf
ADD $VEXPRESS_IMAGE ./core-image-full-cmdline-vexpress-qemu.sdimg

ADD scripts/mender-qemu ./
ADD scripts/docker/entrypoint.sh ./

# Delete images if they are empty. This is to save space if the artifacts are
# mounted on /mnt/build instead.
RUN if [ `stat -c %s core-image-full-cmdline-vexpress-qemu.sdimg` -eq 0 ]; then rm -f core-image-full-cmdline-vexpress-qemu.sdimg; fi
RUN if [ `stat -c %s u-boot.elf` -eq 0 ]; then rm -f u-boot.elf; fi

RUN chmod +x entrypoint.sh mender-qemu
EXPOSE 8822
ENTRYPOINT ["./entrypoint.sh"]
