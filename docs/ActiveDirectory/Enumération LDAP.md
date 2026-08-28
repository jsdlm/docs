# Enumération manuelle

## Built-in

**Utilisateurs**

```cmd
net user /domain                     :: lister tous les utilisateurs du domaine
net user <USERNAME> /domain          :: détails d'un utilisateur (groupes, dernière connexion…)
```

**Groupes**

```cmd
net group /domain                    :: lister tous les groupes du domaine
net group "Sales Department" /domain :: membres d'un groupe spécifique
```

## PowerView

```bash
sudo apt install powersploit
powersploit -h
/usr/share/windows-resources/powersploit/Recon/PowerView.ps1
```

```powershell
Import-Module .\PowerView.ps1
```

**Domaine et utilisateurs**

```powershell
Get-NetDomain                                        # infos domaine (PDC, DC…)
Get-NetUser                                          # tous les attributs de tous les utilisateurs
Get-NetUser | select cn                              # liste des usernames
Get-NetUser | select cn,pwdlastset,lastlogon         # dernière MAJ mdp + dernière connexion
```

**Groupes**

```powershell
Get-NetGroup | select cn                             # liste de tous les groupes
Get-NetGroup "Sales Department" | select member      # membres d'un groupe (inclut les groupes imbriqués)
Get-NetGroupMember "Domain Admins" | select MemberName  # membres directs d'un groupe

# Attributs utilisateur (ex: whencreated) pour les membres d'un groupe
# Get-NetGroupMember ne retourne pas les attributs user -  passer par Get-NetUser :
Get-NetGroupMember "Domain Admins" | ForEach-Object {
    Get-NetUser $_.MemberName | select cn, whencreated
}
```

> Chercher des comptes avec `pwdlastset` ancien ou `lastlogon` jamais utilisé → cibles idéales pour password attacks (politique plus laxiste, moins de surveillance).

**Machines**

```powershell
Get-NetComputer | select operatingsystem,dnshostname   # OS + hostname de toutes les machines
Get-NetComputer | select dnshostname,operatingsystem,operatingsystemversion
```

> Repérer les OS anciens (Windows 10, Server 2016…) -  plus susceptibles d'avoir des vulnérabilités non patchées. Noter également les serveurs web/fichiers comme cibles prioritaires.

**Droits admin locaux sur les machines du domaine**

```powershell
Find-LocalAdminAccess    # machines où l'utilisateur courant est admin local
```

**Sessions actives / utilisateurs connectés**

```powershell
# Fonctionne seulement si le user courant a des droits admin sur la machine cible
# (accès refusé sur Windows 11 / Server 2019+ pour les non-admins)
Get-NetSession -ComputerName <HOSTNAME> -Verbose
```

> `Get-NetSession` utilise `NetSessionEnum` -  bloqué par défaut depuis Windows 11 build 1709 et Server 2019 build 1809 (changement des permissions sur la clé `SrvsvcSessionInfo` dans `HKLM\SYSTEM\CurrentControlSet\Services\LanmanServer\DefaultSecurity`).

**PsLoggedOn (SysInternals) -  alternative fiable**

Se connecte à distance via **SMB (port 445)** avec deux mécanismes :
- **Remote Registry** → lit `HKEY_USERS` → users connectés localement
- **NetSessionEnum** → users connectés via partages réseau

Nécessite que le service **Remote Registry** soit actif sur la cible :
- Activé par défaut sur Windows Server
- Désactivé par défaut sur les workstations depuis Windows 8 (mais peut être activé par un admin)

Pas besoin d'être admin local sur la cible -  juste que Remote Registry soit accessible.

```cmd
.\PsLoggedon.exe \\<HOSTNAME>
```

```
Users logged on locally:
    CORP\jeff
Users logged on via resource shares:
    CORP\stephanie
```

> Si un utilisateur à hauts privilèges (ex: `jeffadmin`) est connecté sur une machine où on a des droits admin locaux → vecteur d'attaque pour vol de credentials.

**Service Principal Names (SPN)**

Un SPN associe un service (IIS, MSSQL, Exchange…) à un compte de service AD. Énumérer les SPNs permet de découvrir les services et leurs IP/ports sans port scan.

```powershell
# Lister les SPNs d'un compte spécifique
setspn -L <USERNAME>
```

```powershell
# Lister tous les comptes avec SPN dans le domaine
Get-NetUser -SPN | select samaccountname,serviceprincipalname
```

```powershell
# Résoudre le hostname associé
nslookup.exe web04.corp.com
```

> Les comptes de service ont généralement plus de privilèges qu'un user standard. Un SPN de type `HTTP/web04.corp.com` indique un serveur web -  vecteur pour Kerberoasting (voir modules suivants).

**Shares**

```powershell
Find-DomainShare                    # tous les partages du domaine
Find-DomainShare -CheckShareAccess  # uniquement ceux accessibles par l'utilisateur courant
```

**Cibles prioritaires**

```powershell
# SYSVOL -  accessible par tous les users du domaine, contient scripts et GPO
ls \\dc1.corp.com\sysvol\corp.com\
ls \\dc1.corp.com\sysvol\corp.com\Policies\
```

**Explorer les partages non-standard** (ex: `docshare`, `backup`, `docs`…) -  les admins y laissent souvent des fichiers sensibles (emails, mots de passe en clair, scripts).
# Enumération automatique

## SharpHound
https://github.com/SpecterOps/SharpHound

SharpHound collecte les données AD (LDAP, NetSessionEnum, Remote Registry…) et les exporte dans un ZIP analysable par BloodHound.

```powershell
SharpHound.exe -d target.local --domaincontroller dc01.target.local --ldapusername user --ldappassword 'Password' -c All

#Ou lancer une session avec les creds cibles puis exécuter SharpHound normalement
runas /netonly /user:target.local\user cmd
SharpHound.exe -d target.local -c All

# Loop sur les sessions
SharpHound.exe -c Session --Loop --Loopduration 03:09:41

# Detected by MDI
SharpHound.exe -c All

# More OPSEC-friendly, but still detected by MDI
SharpHound.exe -c Group,GPOLocalGroup,Session,Trusts,ACL,Container,ObjectProps,SPNTargets,CertServices --excludedcs
```

```powershell
Import-Module .\Sharphound.ps1
Invoke-BloodHound -CollectionMethod All
Invoke-BloodHound -CollectionMethod All -Loop -LoopDuration 02:00:00 -LoopInterval 00:05:00
```

- `All` : collecte tout sauf les GPO locales (groupes, sessions, ACLs, SPNs, trusts…)
- Le résultat est un fichier ZIP à transférer sur Kali pour analyse dans BloodHound

## RustHound-CE
https://github.com/g0h4n/RustHound-CE

Télécharger la dernière release https://github.com/g0h4n/RustHound-CE/releases
```
./rusthound-ce -d north.sevenkingdoms.local -u 'samwell.tarly' -p 'Heartsbane' -c All -z
```
## BOFHound
https://github.com/coffeegist/bofhound

```
pipx install bofhound
```
### ldapsearch

BOFHound est un ingestor BloodHound hors ligne et un parser de résultats LDAP compatible avec le [ldapsearch BOF](https://github.com/trustedsec/CS-Situational-Awareness-BOF) de TrustedSec, son adaptation Python [pyldapsearch](https://github.com/fortalice/pyldapsearch), et le [LDAP Sentinel](https://bruteratel.com/tabs/commander/badgers/#ldapsentinel) de Brute Ratel. La sortie du ldapsearch BOF peut aussi être parsée depuis des logs [Havoc](https://github.com/HavocFramework/Havoc), des logs OutflankC2, et des callbacks [Mythic](https://github.com/its-a-feature/Mythic).

```
ldapsearch (|(objectClass=domain)(objectClass=organizationalUnit)(objectClass=groupPolicyContainer)) --attributes *,ntsecuritydescriptor

ldapsearch (|(samAccountType=805306368)(samAccountType=805306369)(samAccountType=268435456)) --attributes *,ntsecuritydescriptor
```

```
scp -r attacker@10.0.0.5:/opt/cobaltstrike/logs .
bofhound -i logs/
ls -l

-rwxrwxrwx 1 attacker attacker 16072 Mar 12 12:06 computers_20250312_120659.json
-rwxrwxrwx 1 attacker attacker  1803 Mar 12 12:06 domains_20250312_120659.json
-rwxrwxrwx 1 attacker attacker 13792 Mar 12 12:06 gpos_20250312_120659.json
-rwxrwxrwx 1 attacker attacker 34772 Mar 12 12:06 groups_20250312_120659.json
drwxrwxrwx 1 attacker attacker  4096 Mar 12 12:06 logs
-rwxrwxrwx 1 attacker attacker  5690 Mar 12 12:06 ous_20250312_120659.json
-rwxrwxrwx 1 attacker attacker 21889 Mar 12 12:06 users_20250312_120659.json
```

Tout objet représenté uniquement par un SID, ou marqué "no name or id", signifie qu'on n'a pas encore collecté de données à son sujet :
```
ldapsearch (objectsid=[SID]) --attributes *,ntsecuritydescriptor
```

### pyldapseach

https://github.com/Tw1sm/pyldapsearch

```bash
pipx install pyldapsearch

pyldapsearch north.sevenkingdoms.local/'samwell.tarly':'Heartsbane' '(objectClass=*)'

bofhound -i ~/.pyldapsearch/logs/ --properties-level all
```

## ADExplorer

ADExplorer (Microsoft Sysinternals) is a signed tool for AD viewing and editing - a better alternative to LDAP recon.

- Reference: [https://learn.microsoft.com/en-us/sysinternals/downloads/adexplorer](https://learn.microsoft.com/en-us/sysinternals/downloads/adexplorer)
- A user can take a snapshot of AD and process it offline.
- The snapshot can be converted into BloodHound JSON files: [https://github.com/c3c/ADExplorerSnapshot](https://github.com/c3c/ADExplorerSnapshot)
```
pipx install git+https://github.com/c3c/ADExplorerSnapshot
pipx install bofhound

ADExplorerSnapshot.py -m BOFHound snapshot.dat
bofhound -i ./dc.server.com_1234567890_bofhound.log -o output
```
- Reference: [https://trustedsec.com/blog/adexplorer-on-engagements](https://trustedsec.com/blog/adexplorer-on-engagements)

**Drawbacks:**

- May fail in large domains with poor connectivity.
- When ADFS is deployed, ADExplorer triggers an MDI alert by reading the ADFS LDAP container.
![](app://d768204a59517f387194779db93cb30a37b1/C:/Users/jules/_dev/github/docs/docs/RedTeam/img/Pasted%20image%2020260421164605.png?1784982942041)

![](app://d768204a59517f387194779db93cb30a37b1/C:/Users/jules/_dev/github/docs/docs/RedTeam/img/Pasted%20image%2020260421164615.png?1784982942042)

> **Prefer ADWS over LDAP when possible** to avoid MDI detection.

## ADWS

### SOAPHound

[SOAPHound](https://github.com/FalconForceTeam/SOAPHound) talks to Active Directory Web Services (ADWS - Port 9389) instead of sending LDAP queries.

- Almost no network-based detection by MDI.
- Retrieves all objects (`objectGuid=*`) then processes them locally.
- Limited LDAP queries - less chance of endpoint detection.

```bash
# Build a cache with basic info about domain objects
SOAPHound.exe --buildcache -c c:\users\vagrant\desktop\cache.txt

# Collect BloodHound-compatible data
SOAPHound.exe -c c:\users\vagrant\desktop\cache.txt --bhdump -o c:\users\vagrant\desktop\bloodhound-output --nolaps
```

**MDI detection:** MDI detected the original SOAPHound due to the LDAP filter `(!soaphound=*)`.
The filter is hardcoded in the source:

![](app://d768204a59517f387194779db93cb30a37b1/C:/Users/jules/_dev/github/docs/docs/RedTeam/img/Pasted%20image%2020260417145354.png?1784982942018)

After modifying `(!soaphound=*)` in the source and recompiling, SOAPHound bypasses MDI:

![](app://d768204a59517f387194779db93cb30a37b1/C:/Users/jules/_dev/github/docs/docs/RedTeam/img/Pasted%20image%2020260417145713.png?1784982942019)

![](app://d768204a59517f387194779db93cb30a37b1/C:/Users/jules/_dev/github/docs/docs/RedTeam/img/Pasted%20image%2020260421171341.png?1784982942045)

**Drawbacks:**

- Requires introducing a binary to monitored endpoints.
- May fail against very large domains.

### ShadowHound-ADM

[ShadowHound-ADM](https://github.com/Friends-Security/ShadowHound/blob/main/ShadowHound-ADM.ps1) is a PowerShell script leveraging the AD Module over ADWS.

- Uses native PowerShell - no need for known-malicious binaries like SharpHound.
- Talks to ADWS (Port 9389) instead of LDAP.

```bash
# AD Recon
Import-Module .\ShadowHound-ADM.ps1
ShadowHound-ADM -OutputFilePath "C:\users\consultant\documents\mhd\ldap_output.txt" -SplitSearch -LetterSplitSearch -Recurse

# ADCS Recon
ShadowHound-ADM -OutputFilePath "C:\users\consultant\documents\mhd\cert_output.txt" -Certificates
```

**MDI detection:** Detected due to specific LDAP filters in the original code.

For AD Recon:

![](app://d768204a59517f387194779db93cb30a37b1/C:/Users/jules/_dev/github/docs/docs/RedTeam/img/Pasted%20image%2020260420111459.png?1784982942021)

![](app://d768204a59517f387194779db93cb30a37b1/C:/Users/jules/_dev/github/docs/docs/RedTeam/img/Pasted%20image%2020260421180249.png?1784982942047)

For ADCS Recon:

![](app://d768204a59517f387194779db93cb30a37b1/C:/Users/jules/_dev/github/docs/docs/RedTeam/img/Pasted%20image%2020260421180720.png?1784982942047)

![](app://d768204a59517f387194779db93cb30a37b1/C:/Users/jules/_dev/github/docs/docs/RedTeam/img/Pasted%20image%2020260421180754.png?1784982942048)

![](app://d768204a59517f387194779db93cb30a37b1/C:/Users/jules/_dev/github/docs/docs/RedTeam/img/Pasted%20image%2020260421181527.png?1784982942050)

After modifying the filters in the source, ShadowHound-ADM bypasses MDI:

![](app://d768204a59517f387194779db93cb30a37b1/C:/Users/jules/_dev/github/docs/docs/RedTeam/img/Pasted%20image%2020260420111907.png?1784982942021)

![](app://d768204a59517f387194779db93cb30a37b1/C:/Users/jules/_dev/github/docs/docs/RedTeam/img/Pasted%20image%2020260420132551.png?1784982942024)

**Convert outputs to BloodHound JSON:**

```bash
pipx install bofhound

# Convert
bofhound -i ~/workspace/ldap_output.txt -p All --parser ldapsearch
bofhound -i ~/workspace/certs_output.txt -p All --parser ldapsearch
```

## BloodHound-ce python

https://github.com/dirkjanm/BloodHound.py

```bash
# https://github.com/dirkjanm/BloodHound.py
pipx install bloodhound-ce
bloodhound-ce-python --zip -c All -u 'USER' -p 'PASSWORD' -d 'DOMAIN.COM' -dc 'DC_FQDN' -ns 192.168.1.10
```


## Netexec

```bash
# Export bloodhound
nxc ldap 192.168.1.10 -u 'USER' -p 'PASSWORD' -d 'DOMAIN.COM' --bloodhound -c All --dns-server 192.168.1.10

# share enum with user
nxc smb 192.168.56.10-23 -u 'jon.snow' -p 'iknownothing' --shares

# Get DC ip
nxc ldap 192.168.56.11 -u 'brandon.stark' -p 'iseedeadpeople' --dc-list

# Get all users from all DCs
nxc ldap 192.168.56.10-23 -u 'brandon.stark' -p 'iseedeadpeople' -d 'north.sevenkingdoms.local' --users

# Export users to file for each DCs
nxc ldap 192.168.56.10 -u 'brandon.stark' -p 'iseedeadpeople' -d 'north.sevenkingdoms.local' --users-export KINGSLANDING_USERS.txt
nxc ldap 192.168.56.11 -u 'brandon.stark' -p 'iseedeadpeople' -d 'north.sevenkingdoms.local' --users-export WINTERFELL_USERS.txt
nxc ldap 192.168.56.12 -u 'brandon.stark' -p 'iseedeadpeople' -d 'north.sevenkingdoms.local' --users-export MEEREEN_USERS.txt
```

