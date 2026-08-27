# Enumération manuelle

## Users et Groupes

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

## Service Principal Names (SPN)

Un SPN associe un service (IIS, MSSQL, Exchange…) à un compte de service AD. Énumérer les SPNs permet de découvrir les services et leurs IP/ports sans port scan.

```cmd
:: Lister les SPNs d'un compte spécifique
setspn -L <USERNAME>
```

```powershell
:: Lister tous les comptes avec SPN dans le domaine
Get-NetUser -SPN | select samaccountname,serviceprincipalname
```

```powershell
:: Résoudre le hostname associé
nslookup.exe web04.corp.com
```

> Les comptes de service ont généralement plus de privilèges qu'un user standard. Un SPN de type `HTTP/web04.corp.com` indique un serveur web -  vecteur pour Kerberoasting (voir modules suivants).

## Shares

```powershell
Find-DomainShare                    # tous les partages du domaine
Find-DomainShare -CheckShareAccess  # uniquement ceux accessibles par l'utilisateur courant
```

**Cibles prioritaires**

```powershell
# SYSVOL -  accessible par tous les users du domaine, contient scripts et GPO
ls \\dc1.corp.com\sysvol\corp.com\
ls \\dc1.corp.com\sysvol\corp.com\Policies\

# Lire un fichier de politique
cat \\dc1.corp.com\sysvol\corp.com\Policies\oldpolicy\old-policy-backup.xml
```

> Les fichiers XML de Group Policy Preferences (GPP) peuvent contenir des mots de passe chiffrés (`cpassword`). La clé AES-256 est publique -  déchiffrer avec `gpp-decrypt` :

```bash
gpp-decrypt "<CPASSWORD_VALUE>"
```

**Explorer les partages non-standard** (ex: `docshare`, `backup`, `docs`…) -  les admins y laissent souvent des fichiers sensibles (emails, mots de passe en clair, scripts).

## LDAP Enumeration

```shell
# Null bind
ldapsearch -h $rhost -x -b "DC=domain,DC=local"

# Zone transfer DNS
dig @$rhost axfr
dig -x $rhost
```

# Enumération automatique

## BOFHound
https://github.com/coffeegist/bofhound
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

github.com/Tw1sm/pyldapsearch

```bash
git clone https://github.com/Tw1sm/pyldapsearch.git
cd pyldapsearch/
pipx install .

pyldapsearch north.sevenkingdoms.local/'samwell.tarly':'Heartsbane' '(objectClass=*)'

bofhound -i ~/.pyldapsearch/logs/ --properties-level all
```

## SharpHound
https://github.com/SpecterOps/SharpHound

SharpHound collecte les données AD (LDAP, NetSessionEnum, Remote Registry…) et les exporte dans un ZIP analysable par BloodHound.

```bash
sudo apt install sharphound
sharphound -h
/usr/share/sharphound
```

**Collecte depuis la machine compromise**

```
SharpHound.exe --CollectionMethods All
SharpHound.exe --CollectionMethods Session --Loop --Loopduration 03:09:41
```

```powershell
Import-Module .\Sharphound.ps1
Invoke-BloodHound -CollectionMethod All
Invoke-BloodHound -CollectionMethod All -Loop -LoopDuration 02:00:00 -LoopInterval 00:05:00
```

- `All` : collecte tout sauf les GPO locales (groupes, sessions, ACLs, SPNs, trusts…)
- Le résultat est un fichier ZIP à transférer sur Kali pour analyse dans BloodHound
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

## BloodHound-ce python

https://github.com/dirkjanm/BloodHound.py

```bash
# https://github.com/dirkjanm/BloodHound.py
pipx install bloodhound-ce
bloodhound-ce-python --zip -c All -u 'USER' -p 'PASSWORD' -d 'DOMAIN.COM' -dc 'DC_FQDN' -ns 192.168.1.10
```

# Server BloodHound
https://github.com/SpecterOps/BloodHoundQueryLibrary

```bash
cd /opt/tools/bloodhound
docker compose up -d

# Récupérer le mot de passe initial dans les logs
docker logs bloodhound-bloodhound-1 2>&1 | grep "Initial Password"
```

Se connecter sur `http://127.0.0.1:8080` avec `admin` / `<INITIAL_PASSWORD>`.

**Importer le ZIP SharpHound** -  glisser-déposer le fichier dans l'interface ou utiliser le bouton Upload.

**Requêtes utiles (onglet Analysis)**

| Requête | Utilité |
|---|---|
| Find all Domain Admins | Lister les DA et leurs relations |
| Find Shortest Paths to Domain Admins | Chemin d'attaque le plus court vers DA |
| Shortest Paths to Domain Admins from Owned Principals | Chemin depuis les objets qu'on contrôle |

**Marquer des objets comme "owned"** -  clic droit sur un nœud → *Mark as Owned* (icône crâne). À faire pour chaque user/machine compromis afin d'affiner les chemins d'attaque.

> Cliquer sur une arête entre deux nœuds → **? Help** → onglet *Abuse* : explique comment exploiter la relation concrètement.

Chercher :
- **Shortest path to Domain Admins**
- **Users with DCSync rights**
- **Kerberoastable users**
- **ASREPRoastable users**
- **ACL abuse paths** (AllExtendedRights, GenericAll, WriteDacl)
- **GPO abuse paths**

Visualisation des droits dans bloodhound, check "outbound control rights" depuis notre USER et les [ACL](ACL.md).

