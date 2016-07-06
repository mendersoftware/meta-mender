FROM ubuntu:trusty

# Install QEMU/KVM
RUN apt-get -y update && \
    apt-get -y upgrade && \
    apt-get -y install qemu-kvm qemu-system-arm && \
    rm -rf /var/lib/apt/lists/*

#Use: --build-arg VEXPRESS_IMAGE=core-image-full-cmdline-vexpress-qemu.sdimg --build-arg UBOOT_ELF=u-boot.elf when building
ARG VEXPRESS_IMAGE
ARG UBOOT_ELF

ADD $UBOOT_ELF ./
ADD $VEXPRESS_IMAGE ./

ADD scripts/mender-qemu ./
ADD scripts/docker/entrypoint.sh ./

RUN chmod +x entrypoint.sh mender-qemu
EXPOSE 8822
ENTRYPOINT ["./entrypoint.sh"]
