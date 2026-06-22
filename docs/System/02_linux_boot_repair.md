# Linux Boot repair

> This guide outlines the steps needed to troubleshoot and repair a Linux system that fails to boot. It includes using a bootable USB, chrooting into the system, repairing GRUB, and regenerating initramfs.

***

# **Boot from a Live USB**

1. Insert the bootable USB and start the machine.
2. Access the BIOS/UEFI settings and set the USB as the primary boot device.
3. Boot into the live environment.

***

# **Accessing the Encrypted Disk**

If the root filesystem is encrypted, you will need to decrypt it before proceeding. Open a terminal in the live environment and list available disks.

```bash
lsblk
```

Unlock the encrypted partition (replace /dev/sda3 with your actual partition).

```bash
cryptsetup luksOpen /dev/sda3 sda3_opened
```

***

# **Mounting Partitions**

Mount the root partition (replace ubuntu--vg-ubuntu--lv if necessary).

```bash
mount /dev/mapper/ubuntu--vg-ubuntu--lv /mnt
```

If /boot is on a separate partition, mount it too.

```bash
mount /dev/sda2 /mnt/boot
```

Bind the necessary system directories.

```bash
mount --bind /dev /mnt/dev
mount --bind /proc /mnt/proc
mount --bind /sys /mnt/sys
```

***

# **Chroot into the System**

Now, change the root directory to your installed system.

```bash
chroot /mnt
```

You are now inside your installed system. You can perform repairs as if you were logged in normally.

***

# **Repair GRUB**

Reinstall GRUB to the disk (usually /dev/sda).

```bash
grub-install /dev/sda
```

Regenerate the GRUB configuration file.

```bash
update-grub
```

***

# **Regenerate initramfs**

If necessary, regenerate the initramfs image to ensure that the kernel and encryption modules are correctly loaded.

```bash
update-initramfs -u
```

***

# **Exit chroot and Unmount Partitions**

Exit the chroot environment:

```bash
exit
```

Unmount the partitions:

```bash
umount /mnt/dev
umount /mnt/proc
umount /mnt/sys
umount /mnt/boot # If boot is mounted separately
umount /mnt
```

***

# **Reboot**

```bash
reboot
```

***

**9. Troubleshooting the Passphrase Issue**

If the system does not ask for the passphrase on boot, check the following files:

1. /etc/crypttab: Ensure the correct UUID and parameters for your encrypted partition are listed.
2. /etc/fstab: Verify that the correct device mapping is used for the root filesystem (e.g., /dev/mapper/sda3\_opened).
3. Regenerate initramfs after any changes: `update-initramfs -u`
4. GRUB configuration: Ensure that /etc/default/grub has the following line for encrypted disks:\
   `GRUB_ENABLE_CRYPTODISK=y`\
   Then update GRUB:\
   `update-grub`

***

### Arriving at (initramfs) Shell

If you're dropped into the (initramfs) shell, follow these steps:

1. Check if LVM volumes are visible:\
   `lvm pvdisplay`
2. Unlock the encrypted partition:\
   `cryptsetup luksOpen /dev/sda3 dm_crypt-0`
3. Activate the LVM volumes:\
   `vgchange -ay`
4. Mount the root partition:\
   `mount /dev/mapper/ubuntu--vg-ubuntu--lv /root`
5. Exit initramfs to continue booting:\
   `exit`
