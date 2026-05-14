# Enumeration

## Workflow Général

```text
┌──────────────────────────────────────────┐
│        1. INFORMATION GATHERING          │
│------------------------------------------│
│ - Identifier le scope                    │
│ - Découvrir les hôtes actifs             │
│ - Énumérer les ports et services ouverts │
└──────────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                         2. ENUMERATION                                  │
│-------------------------------------------------------------------------│
│ - Récupérer les détails de services (versions, banners)                 │
│ - Inspecter les web apps, shares, endpoints                             │
│ - Identifier les misconfigurations et fonctionnalités exposées          │
└─────────────────────────────────────────────────────────────────────────┘
                    │
                    ▼
      ┌────────────────────────────────────────────────┐
      │             3. VULNERABILITY ANALYSIS          │
      │------------------------------------------------│
      │ - Mapper les services aux faiblesses connues   │
      │ - Analyser configs, permissions, frameworks    │
      │ - Identifier les chemins d'attaque réalistes   │
      └────────────────────────────────────────────────┘
```

---

## Les Règles Perso

**Règle 1** — Peu importe l'outil, vérifie ce qui est ouvert :
```shell
nmap -sC -sV -p- --open $target -v
# Tu peux utiliser rustscan ou autoscan après, mais commence par savoir ce qui est ouvert
# Lance avec -v pour voir les résultats en live, pas besoin d'attendre la fin
```

**Règle 2** — Pour la web enum, pas besoin d'aller sur le site, lance `whatweb` d'abord :
```shell
whatweb $target
whatweb $target:port
# Banner grab depuis le terminal, sauve du temps
```

**Règle 3** — Après whatweb, lance `dirsearch` directement :
```shell
dirsearch -u http://$target
# Vient avec une wordlist intégrée, fonctionne comme gobuster
# Tu peux faire ça pendant que nmap tourne encore
```

**Règle 4** — Banner grab les ports réseau avec netcat :
```shell
nc -nv $target <port>
nc -nnv $target <port>
nmap -sV -A -p <port> $target --script=banner
telnet $target <port>   # Utile pour SMTP (port 25)
```

**Règle 5** — SSH passe en dernier (brute-force uniquement si t'as des users) :
```shell
hydra -L users.txt -P /usr/share/wordlists/rockyou.txt ssh://$target -V -e nsr -f -t 50
# Ne t'y attarde pas si t'as rien pour commencer
```

**Règle 6** — Ne pas oublier UDP :
```shell
nmap -sU -p 53,161,137 $target -v
# UDP est sans connexion (pas de handshake), ça prend du temps
# Cible surtout le port 161 (SNMP)
nmap -sU -p 161 --script=snmp-info,snmp-interfaces,snmp-processes $target
```

**Règle 7** — Toujours tester anonymous/guest sur 445, 21, 135 :
```shell
# Si ça ne marche pas → cocher et passer
# Si ça marche → récupérer TOUT depuis FTP et SMB

nmap -v -p 139,445 --script smb-os-discovery $target
rpcclient -U "" -N $target
# Dans rpcclient : enumdomusers / srvinfo / querydispinfo

# Banner grab RPC puis revenir avec un user
```

**Règle 7bis** — Banner grab SMTP et tester VRFY :
```shell
nc -nv $target 25
# VRFY root
telnet $target 25
```

**Règle 8** — Si Metasploit a un module, il y a probablement un exploit GitHub ou ExploitDB :
```shell
# exploit-db.com est ton ami
searchsploit <service name>
```

**Règle 9** — Garder Metasploit pour la dernière machine :
```text
Metasploit est autorisé sur 1 seule machine.
Si t'as 60 pts et qu'il reste une machine → utilise Metasploit pour passer.
```

**Règle 10** — Faire attention au nom du serveur (indice sur son rôle) :
```text
web-serv1 → serveur web
mail-serv1 → serveur mail
```

**Règle 11** — Garder un timer, se lever, faire une pause. Obligatoire.

**Règle 12** — Prendre TOUTES les notes, commandes, screenshots de succès — pas seulement pour le rapport, mais pour revenir en arrière si bloqué.

**Règle 13** — Utiliser Burp pour les attaques web si quelque chose d'intéressant est trouvé.

---

## Port Scanning

```shell
# Scan complet recommandé
nmap -Pn -sC -sV -p- --open -T4 $target -v -oN nmap_TCPscan.txt

# Rustscan (plus rapide)
rustscan -a $target --ulimit 5000 -- -Pn
rustscan -a $target --ulimit 5000 -- -A -sV
rustscan -a 10.0.x.x/24 --ulimit 5000 -- -Pn  # scan réseau

# Unicornscan
unicornscan -v -I -i tun0 -mT $target

# UDP
nmap -sU -p 53,161,137 $target -v
nmap -sV -sU -p- --open $target -v

# SSL/TLS
openssl s_client -connect $target:443
```

---

## Web Enumeration

### Identifier le Stack

```shell
whatweb http://$target
whatweb http://$target:port
curl -I http://$target
curl -kI http://$target    # HTTPS sans vérif cert
curl -i http://$target/    # Avec headers complets
```

### Directory Brute-Force

```shell
dirsearch -u http://$target

gobuster dir -u http://$target \
  -w /usr/share/seclists/Discovery/Web-Content/raft-medium-directories.txt \
  -x php,txt,html,asp,aspx,bak

feroxbuster -u http://$target \
  -w /usr/share/seclists/Discovery/Web-Content/directory-list-2.3-medium.txt
```

### Checklist Web

- [ ] Identifier le stack (framework, serveur, CMS)
- [ ] Vérifier headers HTTP (Server, X-Powered-By, cookies)
- [ ] Vérifier SSL/TLS (cert info, hostnames SAN)
- [ ] robots.txt / sitemap.xml / changelog / readme
- [ ] Chercher des backups exposés (.zip, .tar, .old, .bak)
- [ ] Login pages / Admin panels / Upload functionality
- [ ] Search boxes / Filtering / Hidden form fields
- [ ] JavaScript : chemins cachés, credentials hardcodés, routes dépréciées
- [ ] Stack traces et messages d'erreur verbeux
- [ ] API endpoints, réponses pour champs cachés
- [ ] Version numbers dans les commentaires HTML
- [ ] Screenshot chaque page intéressante

---

## Service par Service

### FTP (21)

```shell
# Version et exploits
searchsploit ftp <version>

# Anonymous login
ftp $target
# user: anonymous  pass: anonymous

# Download tout le répertoire
wget -m ftp://anonymous:anonymous@$target

# Nmap scripts
nmap -p 21 --script ftp-anon,ftp-syst,ftp-bounce $target
```

Chercher :
- Fichiers avec indices (ex: `minniemouse.exe`)
- Uploads qui vont vers un répertoire web ?

### SSH (22)

```shell
nmap -p 22 -sV --script=ssh2-enum-algos,ssh-hostkey $target
# Bannière, version OS, indices de réutilisation de clé faible
# Ignorer jusqu'à avoir des credentials
```

### SMTP (25)

```shell
nc -nv $target 25
telnet $target 25

# VRFY pour vérifier si un user existe
VRFY root
VRFY admin

# Nmap enum users
nmap -p 25 --script smtp-enum-users --script-args smtp-enum-users.methods={VRFY,EXPN} $target
```

### SMB (139/445)

```shell
# Null session et liste des shares
smbclient -L //$target -N
nxc smb $target -u '' -p '' --shares

# Accéder à un share
smbclient //$target/share -N

# Enum complet
enum4linux-ng $target

# OS discovery
nmap -v -p 139,445 --script smb-os-discovery $target

# RPC
rpcclient -U "" -N $target
# Dans rpcclient :
# enumdomusers
# srvinfo
# querydispinfo

# Nmap null session
nxc smb $target -u '' -p '' --shares
```

### SNMP (161)

```shell
# Brute-force community strings
sudo nmap -sU -p 161 --script snmp-brute $target

# Enumération avec community string public
snmpwalk -v 1 -c public $target NET-SNMP-EXTEND-MIB::nsExtendObjects
snmpwalk -v2c -c public $target | grep <string>

# Nmap complet
nmap -sU -p 161 --script=snmp-info,snmp-interfaces,snmp-processes $target
```

### RDP (3389)

```shell
nmap -p 3389 --script=rdp-enum-encryption $target
# Check encryption → indice sur la version Windows
```

### MSSQL (1433)

```shell
# Connexion
impacket-mssqlclient user:pass@$target -windows-auth

# Enum des bases de données
SQL> SELECT name FROM sys.databases;
```

### Telnet (23)

```shell
nmap -p 23 --script=telnet-brute,telnet-ntlm-info $target
telnet $target 23
```

---

## Low Hanging Fruit

- [ ] CMS/framework version obsolète
- [ ] Accès anonymous/guest sur des services
- [ ] Fichiers de config lisibles dans des shares
- [ ] Backups exposés (zip, tar, old)
- [ ] Test d'upload (type + contraintes de taille)
- [ ] Endpoints dépréciés
- [ ] Pages admin par défaut
- [ ] Réutilisation de mot de passe (username = password)
- [ ] Bases de données ouvertes sans credentials
- [ ] Répertoires world-readable ou shares mal configurés

---
## Rescanning

- [ ] Rescanner si bloqué — la précision de l'enum compte
- [ ] Ajuster le timing Nmap (T2/T3 vs T4/T5)
- [ ] Essayer des scanners ou wordlists différents
- [ ] Vérifier :
    - Utilisation de root/admin là où nécessaire
    - Outils non bloqués par firewall ou timeout
    - VPN/connexion stable
- [ ] Re-lancer des scans ciblés sur les ports "bizarres"
- [ ] Vérifier les changements après avoir interagi avec des services

---

## Mental Rules OSCP

- [ ] Ne pas sauter de machines au hasard — finir l'enum complète d'abord
- [ ] Documenter TOUT, surtout les anomalies
- [ ] Si bloqué : refaire la recon, élargir l'enum, rester systématique
- [ ] Mémo : Enumeration → Enumeration → Enumeration
- [ ] Identifier le rôle probable de la machine (dev box, file server, CMS host)
- [ ] Déduire le modèle de privileges (BD backend ? AD ? API interne ?)
- [ ] Construire une liste de :
    - Misconfigurations potentielles
    - Points d'authentification faibles
    - Artefacts de développement
    - Logique interne exposée
- [ ] Prioriser les cibles par simplicité et faisabilité

> Ton plus grand ennemi sur l'exam, c'est le temps.
