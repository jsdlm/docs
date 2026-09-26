## 1. Spécifications de la VM

| Composant | Valeur |
|-----------|--------|
| **OS** | Ubuntu Server 24.04 LTS |
| **Disque OS** | 60 GB (ext4 / LVM) - thin provisioned |
| **Disque DATA** | 100 GB / 500 GB / 1 TB / 2 TB (ZFS) - thin provisioned |
| **RAM** | 4 GB (min. 2 GB) |
| **CPU** | 2 cores, 1 socket |
| **BIOS** | UEFI (OVMF) avec Secure Boot |
| **Réseau** | Mode bridgé (IP séparée de l'hôte) |
| **IP** | `192.168.42.50` |
| **DNS** | `drive.delobel.net` |

**Dépendances incluses :**
- Apache 2.4
- PostgreSQL 18
- PHP-FPM 8.5
- Redis (memcache)
- Nextcloud Server (dernière version)

**Version VMware minimale :** ESXi 6.7+

***

## 2. Installation

1. Importer le fichier `.ova` dans VMware ESXi.
2. Démarrer la VM et se connecter avec les identifiants par défaut (`ncadmin` / `nextcloud`).
3. Devenir root pour lancer le script d'initialisation :

```bash
sudo -i
```

> Le script de setup se lance automatiquement à la première connexion root. **Ne pas l'interrompre.**

4. Suivre les étapes du script (clavier, ports, fonctionnalités). La VM redémarre automatiquement à la fin.

Si le script ne se lance pas automatiquement, l'exécuter manuellement :
```bash
sudo bash /var/scripts/nextcloud-startup-script.sh
```

***

## 3. Accès

### SSH

```bash
ssh ncadmin@192.168.42.50
```

> Identifiants dans Bitwarden - entrée : **Nextcloud SSH**
> Le mot de passe par défaut est modifié lors du premier setup.

Pour devenir root :
```bash
sudo -i
```

### Interface web

```
https://drive.delobel.net
```

> Identifiants dans Bitwarden - entrée : **Nextcloud Web Admin**

---
## 4. Mise à jour

### Mise à jour manuelle (recommandée)

Via le menu interactif :
```bash
sudo bash /var/scripts/menu.sh
```

Naviguer vers **Update Nextcloud**.

Ou directement via le script :
```bash
sudo bash /var/scripts/update.sh
```

> L'updater intégré à l'interface Nextcloud est désactivé (permissions restreintes). Pour le réactiver ponctuellement :
> ```bash
> sudo chown www-data:www-data -R /var/www/nextcloud
> ```

### Mises à jour automatiques

Les mises à jour automatiques se configurent via cron. Chaque exécution est journalisée dans `/var/log/nextcloud/update.log`.

Pour désactiver, supprimer la ligne suivante du crontab (`crontab -e -u root`) :

```
0 18 * * 6 /var/scripts/update.sh minor >> /var/log/nextcloud/update.log
```

Pour modifier l'heure d'exécution, utiliser [crontab.guru](https://crontab.guru/).

***

## 5. Logs

Tous les logs de la VM sont centralisés dans :

```
/var/log/nextcloud/
```

| Fichier | Contenu |
|---------|---------|
| `update.log` | Historique des mises à jour automatiques |

***

## 6. Vérification de sécurité

### Scan Nextcloud

Renseigner `https://drive.delobel.net` sur [scan.nextcloud.com](https://scan.nextcloud.com/). Le site affiche par défaut le dernier score en cache - cliquer sur **Trigger re-scan** pour obtenir un résultat frais. Vérifier que le score est **A+**.

![](img/Pasted%20image%2020260926141826.png)
### Security Headers

Renseigner `https://drive.delobel.net` sur [securityheaders.com](https://securityheaders.com/) en cochant **Hide results** avant de lancer le scan. Vérifier que le score est **A+**.
![](img/Pasted%20image%2020260926141524.png)
![](img/Pasted%20image%2020260926141551.png)