FROM ubuntu:trusty

RUN apt-get -y update
RUN apt-get -y upgrade

#Use: --build-arg VEXPRESS_IMAGE=core-image-full-cmdline-vexpress-qemu.sdimg --build-arg UBOOT_ELF=u-boot.elf when building
ARG VEXPRESS_IMAGE
ARG UBOOT_ELF

# Install QEMU/KVM
RUN apt-get -y install qemu-kvm qemu-system-arm

ADD $UBOOT_ELF ./
ADD $VEXPRESS_IMAGE ./

ADD scripts/mender-qemu ./
ADD scripts/docker/entrypoint.sh ./

RUN chmod +x entrypoint.sh mender-qemu
EXPOSE 8822
ENTRYPOINT ["./entrypoint.sh"]
