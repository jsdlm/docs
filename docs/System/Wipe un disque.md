# 1. Préparer la clé bootable

Télécharger l'ISO sur systemrescue.org, puis flasher la clé :
```bash
dd if=systemrescue-*.iso of=/dev/sdX bs=4M status=progress oflag=sync
```

Remplacer `/dev/sdX` par ta clé USB (vérifier avec `lsblk`).

# 2. Booter et identifier le disque

Booter sur la clé, puis :
```bash
lsblk -o NAME,SIZE,MODEL,SERIAL
```

Repérer le disque cible par sa taille et son numéro de série. Ne pas se tromper de device.

# 3. Wipe

Choisir selon le type de disque.

**HDD (magnétique) — passe unique de zéros :**

```bash
shred -v -n 0 -z /dev/sdX
```

Ou avec dd :

```bash
dd if=/dev/zero of=/dev/sdX bs=4M status=progress
```

**SSD / NVMe — Secure Erase natif (recommandé, plus fiable que shred sur SSD) :**

SATA :
```bash
hdparm --user-master u --security-set-pass p /dev/sdX
hdparm --user-master u --security-erase p /dev/sdX
```

NVMe :
```bash
nvme format /dev/nvmeXn1 --ses=1
```

`--ses=2` pour un Cryptographic Erase si supporté.

# 4. Vérifier

```bash
hexdump -C /dev/sdX | head
```

Le disque doit renvoyer des zéros (ou données aléatoires si Secure Erase crypto).