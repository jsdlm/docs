# Workflow Général

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
# Vecteurs par Fréquence

|Vecteur|Fréquence|Temps|Outils|
|:--|:-:|:-:|:--|
|Anonymous SMB/Web Share|60%|5–10 min|smbclient, curl|
|WordPress/CMS Vulnerability|40%|10–20 min|WPScan, Burp, manual|
|Weak Credentials (Default/Brute-force)|35%|5–15 min|Hydra, Medusa|
|Credential in File/Share|30%|10–20 min|grep, manual search|
|Unpatched Service (CVE)|25%|10–30 min|Exploit-DB, Metasploit|
|LDAP Null Bind|20%|5–10 min|ldapsearch, Python|
|SQL Injection|15%|15–30 min|SQLMap, manual|

---
# Checklist Initial Access

- Web app (WordPress, Joomla, custom app)
    
    - [ ] WPScan pour WordPress
    - [ ] Vérifier /admin, /login, /config
    - [ ] Chercher upload de fichiers
    - [ ] SQL injection, LFI
- SMB shares
    
    - [ ] Accès anonyme ?
    - [ ] Default credentials ?
    - [ ] Fichiers backup avec mots de passe ?
- LDAP
    
    - [ ] Null bind possible ?
    - [ ] Récupérer la liste d'utilisateurs
    - [ ] Comptes sans pre-auth ?
- Default credentials
    
    - [ ] Creds par défaut des applications
    - [ ] Mots de passe de service accounts dans les configs
- Code/fichiers manuels
    
    - [ ] Source code dans un dossier .git ?
    - [ ] Credentials hardcodés dans des fichiers
    - [ ] Commentaires dans HTML/PHP

---
# Checklist Web

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

# Low Hanging Fruit

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
# Rescanning

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

# Mental Rules OSCP

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

---
# Service par Service

## FTP (21)

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


ftp $target                    # anonymous:anonymous
get id_rsa                     # Clé SSH
get backup.zip                 # Cracker avec zip2john
get .keychain                  # Cracker avec keychain2john
wget -m ftp://anonymous:anonymous@$target  # Download tout le répertoire
```

Chercher :
- Fichiers avec indices (ex: `minniemouse.exe`)
- Uploads qui vont vers un répertoire web ?

## SSH (22)

```shell
nmap -p 22 -sV --script=ssh2-enum-algos,ssh-hostkey $target
# Bannière, version OS, indices de réutilisation de clé faible
# Ignorer jusqu'à avoir des credentials
```

## Telnet (23)

```shell
nmap -p 23 --script=telnet-brute,telnet-ntlm-info $target
telnet $target 23
```

## SMTP (25)

```shell
nc -nv $target 25
telnet $target 25

# VRFY pour vérifier si un user existe
VRFY root
VRFY admin

# Nmap enum users
nmap -p 25 --script smtp-enum-users --script-args smtp-enum-users.methods={VRFY,EXPN} $target
```

## SMB (139/445)

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

smbclient -L //$target -N               # Lister les shares
smbclient //$target/share -N -c 'mget *' # Download tout
nxc smb $target -u '' -p '' --shares    # Null session
```

## SNMP (161)

```shell
# Brute-force community strings
sudo nmap -sU -p 161 --script snmp-brute $target

# Enumération avec community string public
snmpwalk -v 1 -c public $target NET-SNMP-EXTEND-MIB::nsExtendObjects
snmpwalk -v2c -c public $target | grep <string>

# Nmap complet
nmap -sU -p 161 --script=snmp-info,snmp-interfaces,snmp-processes $target
```

## MSSQL (1433)

```shell
# Connexion
impacket-mssqlclient user:pass@$target -windows-auth

# Enum des bases de données
SQL> SELECT name FROM sys.databases;

impacket-mssqlclient user:pass@$target -windows-auth
SQL> enable_xp_cmdshell
SQL> xp_cmdshell "powershell -e <BASE64>"
```

## RDP (3389)

```shell
nmap -p 3389 --script=rdp-enum-encryption $target
# Check encryption → indice sur la version Windows

xfreerdp3 /u:user /p:password /v:$target /cert-ignore
xfreerdp3 /cert-ignore /u:user /p:password /v:$target /drive:/var/www/html
nxc rdp $target -u users.txt -p 'Password123'  # Spray
```
