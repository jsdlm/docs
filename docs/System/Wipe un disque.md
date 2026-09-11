# 1. Préparer la clé bootable

Télécharger l'ISO sur [system-rescue.org](https://www.system-rescue.org/), puis flasher la clé :
```bash
dd if=systemrescue-*.iso of=/dev/sdX bs=4M status=progress oflag=sync
```

Remplacer `/dev/sdX` par ta clé USB (vérifier avec `lsblk`).

# 2. Booter et identifier le disque

Repérer le disque cible par sa taille et son numéro de série.
```bash
loadkeys fr
lsblk -o NAME,SIZE,MODEL,SERIAL
```

# 3. Wipe

### HDD
```bash
dd if=/dev/zero of=/dev/sdX bs=4M status=progress
```

```bash
shred -v -n 0 -z /dev/sdX
```

### SSD SATA
```bash
hdparm --user-master u --security-set-pass p /dev/sdX
hdparm --user-master u --security-erase p /dev/sdX
```

### SSD NVMe
```bash
nvme format /dev/nvmeXn1 --ses=1
# --ses=2 pour un Cryptographic Erase si supporté.
```

# 4. Vérifier

```bash
hexdump -C /dev/sdX | head
```

Le disque doit renvoyer des zéros (ou données aléatoires si Secure Erase crypto).