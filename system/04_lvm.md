# LVM

## Partitionner le disque

```bash
fdisk /dev/sda
```

## Créer un système de fichiers sur la partition

```bash
mkfs.ext4 /dev/sda1
```

## Créer un volume physique

```bash
pvcreate /dev/sda1
```

## Créer un groupe de volumes nommé dockervg

```bash
vgcreate dockervg /dev/sda1
```

## Afficher les informations du groupe de volumes

```bash
vgdisplay dockervg
```

## Créer des volumes logiques pour Docker

```bash
lvcreate -L 24G -n data dockervg
lvcreate -l 100%FREE -n lib dockervg
```

## Créer des systèmes de fichiers sur les volumes logiques

```bash
mkfs.ext4 /dev/mapper/dockervg-data
mkfs.ext4 /dev/mapper/dockervg-lib
```

## Créer des répertoires pour les points de montage

```bash
sudo mkdir -p /opt/docker
sudo mkdir -p /var/lib/docker
```

## Monter les volumes logiques

```bash
sudo mount /dev/mapper/dockervg-data /opt/docker
sudo mount /dev/mapper/dockervg-lib /var/lib/docker
```

## Ajouter les points de montage au fichier /etc/fstab pour les rendre persistants

```bash
echo "/dev/mapper/dockervg-lib /var/lib/docker ext4 defaults 0 0" | sudo tee -a /etc/fstab
echo "/dev/mapper/dockervg-data /opt/docker ext4 defaults 0 0" | sudo tee -a /etc/fstab
```
