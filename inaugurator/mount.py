from inaugurator import sh
from inaugurator import partitiontable
import contextlib


class Mount:
    _ROOT_MOUNT_POINT = "/destRoot"
    _BOOT_MOUNT_POINT = "/destBoot"

    def __init__(self, targetDevice):
        self._bootPartition = "%s1" % targetDevice
        self._swapPartition = "/dev/%s/swap" % partitiontable.PartitionTable.VOLUME_GROUP
        self._rootPartition = "/dev/%s/root" % partitiontable.PartitionTable.VOLUME_GROUP

    def rootPartition(self):
        return self._rootPartition

    def bootPartition(self):
        return self._bootPartition

    def swapPartition(self):
        return self._swapPartition

    @contextlib.contextmanager
    def mountRoot(self):
        sh.run("/usr/sbin/busybox mkdir -p %s" % self._ROOT_MOUNT_POINT)
        sh.run("/usr/sbin/busybox mount -t ext4 -o noatime,data=writeback %s %s" % (
            self._rootPartition, self._ROOT_MOUNT_POINT))
        yield self._ROOT_MOUNT_POINT
        sh.run("/usr/sbin/busybox umount %s" % self._ROOT_MOUNT_POINT)

    @contextlib.contextmanager
    def mountBoot(self):
        sh.run("/usr/sbin/busybox mkdir -p %s" % self._BOOT_MOUNT_POINT)
        sh.run("/usr/sbin/busybox mount -t ext4 %s %s" % (self._bootPartition, self._BOOT_MOUNT_POINT))
        yield self._BOOT_MOUNT_POINT
        sh.run("/usr/sbin/busybox umount %s" % self._BOOT_MOUNT_POINT)

    @contextlib.contextmanager
    def mountBootInsideRoot(self):
        sh.run("/usr/sbin/busybox mount -t ext4 %s %s/boot" % (
            self._bootPartition, self._ROOT_MOUNT_POINT))
        sh.run("/usr/sbin/busybox cp -a /dev/* %s/dev/" % self._ROOT_MOUNT_POINT)
        sh.run("/usr/sbin/busybox mount -t proc none %s/proc" % self._ROOT_MOUNT_POINT)
        yield self._ROOT_MOUNT_POINT
        sh.run("/usr/sbin/busybox umount %s/proc" % self._ROOT_MOUNT_POINT)
        sh.run("/usr/sbin/busybox umount %s/boot" % self._ROOT_MOUNT_POINT)
