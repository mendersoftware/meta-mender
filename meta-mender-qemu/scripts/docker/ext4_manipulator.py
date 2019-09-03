import os
import subprocess
from pathlib import PurePath

def get(remote_path, local_path, rootfs):
    subprocess.check_call(["debugfs", "-R", "dump -p %s %s" % (remote_path, local_path), rootfs],
                          stderr=subprocess.STDOUT)

def put(local_path, remote_path, rootfs, remote_path_mkdir_p=False):
    proc = subprocess.Popen(["debugfs", "-w", rootfs], stdin=subprocess.PIPE,
                            stderr=subprocess.STDOUT)
    if remote_path_mkdir_p:
        # Create parent directories sequencially, to simulate a "mkdir -p" on the final dir
        parent_dirs = list(PurePath(remote_path).parents)[::-1][1:]
        for parent in parent_dirs:
            proc.stdin.write(("mkdir %s\n" % parent).encode())
    proc.stdin.write(("cd %s\n" % os.path.dirname(remote_path)).encode())
    proc.stdin.write(("rm %s\n" % os.path.basename(remote_path)).encode())
    proc.stdin.write(("write %s %s\n" % (local_path, os.path.basename(remote_path))).encode())
    proc.stdin.close()
    ret = proc.wait()
    assert ret == 0

def extract_ext4(img, rootfs):
    return _manipulate_ext4(img=img, rootfs=rootfs, write=False)

def insert_ext4(img, rootfs):
    return _manipulate_ext4(img=img, rootfs=rootfs, write=True)

def _manipulate_ext4(img, rootfs, write):
    # calls partx with --show --bytes --noheadings, sample output:
    #
    # $ partx -sbg core-image-full-cmdline-vexpress-qemu.sdimg
    # NR  START    END SECTORS      SIZE NAME UUID  <-- NOTE: this is not shown
    # 1  49152  81919   32768  16777216      a38e337d-01
    # 2  81920 294911  212992 109051904      a38e337d-02
    # 3 294912 507903  212992 109051904      a38e337d-03
    # 4 507904 770047  262144 134217728      a38e337d-04
    output = subprocess.check_output(["partx", "-sbg", img])
    for line in output.decode().split('\n'):
        columns = line.split()
        # This blindly assumes that rootfs is on partition 2.
        if columns[0] == "2":
            if write:
                subprocess.check_call(["dd", "if=%s" % rootfs, "of=%s" % img,
                                       "seek=%s" % columns[1],
                                       "count=%d" % (int(columns[3])),
                                       "conv=notrunc"],
                                      stderr=subprocess.STDOUT)
            else:
                subprocess.check_call(["dd", "if=%s" % img, "of=%s" % rootfs,
                                       "skip=%s" % columns[1],
                                       "count=%d" % (int(columns[3]))],
                                      stderr=subprocess.STDOUT)
            break
    else:
        raise Exception("%s not found in fdisk output: %s" % (img, output))
