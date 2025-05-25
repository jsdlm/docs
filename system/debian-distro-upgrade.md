# Update Debian

## 1. Mettre à jour Debian 11 (bullseye)

```bash
sudo apt update
sudo apt upgrade
sudo apt full-upgrade
sudo apt autoremove
```

## 2. Sauvegarder les sources APT existantes

```bash
cp /etc/apt/sources.list /root/sources.list.bullseye.backup
```

## 3. Basculer vers Debian 12 (bookworm)

```bash
sudo sed -i 's/bullseye/bookworm/g' /etc/apt/sources.list
```

## 4. Mettre à jour l’index et effectuer la migration

```bash
sudo apt update
sudo apt upgrade
sudo apt full-upgrade
sudo apt autoremove
```

## 5. Redémarrer

```bash
sudo reboot
```

## 6. Vérifier la version installée

```bash
cat /etc/os-release
```
