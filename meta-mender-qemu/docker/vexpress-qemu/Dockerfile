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

FROM alpine:3.7

# Install packages
RUN apk update && apk upgrade && \
    apk add util-linux multipath-tools \
            bash e2fsprogs-extra python3

RUN apk add qemu-system-arm

RUN rm -rf /var/cache/apk/*

RUN echo vexpress-qemu > /machine.txt

ARG DISK_IMAGE=scripts/docker/empty-file
ARG BOOTLOADER=scripts/docker/empty-file

COPY $BOOTLOADER ./u-boot.elf
COPY $DISK_IMAGE .

ADD scripts/mender-qemu ./
ADD scripts/docker/entrypoint.sh ./
ADD scripts/docker/ext4_manipulator.py ./
ADD scripts/docker/setup-mender-configuration.py ./
ADD scripts/docker/extract_fs ./
ADD env.txt ./

# Delete images if they are empty. This is to save space if the artifacts are
# mounted on /mnt/build instead.
RUN if [ $(stat -c %s $(basename $DISK_IMAGE)) -eq 0 ]; then rm -f $(basename $DISK_IMAGE); fi
RUN if [ $(stat -c %s u-boot.elf) -eq 0 ]; then rm -f u-boot.elf; fi

RUN chmod +x entrypoint.sh mender-qemu
EXPOSE 8822
ENTRYPOINT ["./entrypoint.sh"]
