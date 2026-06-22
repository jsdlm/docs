# Setup Docker CyberLab

# Création d'une partition sur le disque /dev/xvdb

```bash
fdisk /dev/xvdb <<EOF
n
p
1
w
EOF
```

# Création du système de fichiers ext4

```bash
mkfs.ext4 /dev/xvdb1
```

# Création du point de montage

```bash
mkdir -p /opt/docker
```

# Montage de la partition

```bash
mount /dev/xvdb1 /opt/docker
```

# Ajout à /etc/fstab pour montage automatique

```bash
echo '/dev/xvdb1 /opt/docker ext4 defaults 0 2' >> /etc/fstab
```

# Vérification

```bash
df -h | grep /opt/docker
```

# Arrêter Docker

```bash
systemctl stop docker
```

# Monter le disque si ce n’est pas déjà fait

```bash
mount /dev/xvdb1 /opt/docker
```

# Créer la hiérarchie cible

```bash
mkdir -p /opt/docker/var/lib/docker
```

# Copier les anciennes données Docker dans le nouvel emplacement

```bash
rsync -aP /var/lib/docker/ /opt/docker/var/lib/docker/
```

# Sauvegarder l'ancien dossier

```bash
mv /var/lib/docker /var/lib/docker.bak
```

# Créer ou modifier /etc/docker/daemon.json

```bash
mkdir -p /etc/docker
echo '{ "data-root": "/opt/docker/var/lib/docker" }' > /etc/docker/daemon.json
```

# Redémarrer Docker

```bash
systemctl start docker
```

# Vérifier que Docker utilise bien le nouveau chemin

```bash
docker info | grep "Docker Root Dir"
# Doit afficher : /opt/docker/var/lib/docker
```

# (optionnel) Supprimer l'ancienne sauvegarde

```bash
rm -rf /var/lib/docker.bak
```
