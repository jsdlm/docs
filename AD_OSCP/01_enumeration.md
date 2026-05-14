# Enumération
## Enumération manuelle

### Outils legacy Windows (net.exe)

```cmd
:: Connexion RDP initiale (assumed breach)
xfreerdp /u:stephanie /d:corp.com /v:<IP>
```

> Préférer RDP à WinRM/PSRemoting pour l'énumération AD -  PSRemoting entraîne le **Kerberos Double Hop** qui bloque les outils de domaine.

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

Points à noter lors de l'énumération :
- Noms d'utilisateurs avec suffixes admin (ex: `jeffadmin`) → vérifier l'appartenance à `Domain Admins`
- Groupes personnalisés (Development Department, Management Department…) → souvent plus intéressants que les groupes par défaut

### PowerShell + .NET / LDAP

AD s'énumère via LDAP. Le chemin LDAP requis a la forme :

```
LDAP://HostName/DistinguishedName
```

- **HostName** : le PDC (Primary Domain Controller, seul DC avec `PdcRoleOwner`)
- **DistinguishedName** : ex. `DC=corp,DC=com`

**Construire le chemin LDAP dynamiquement**

```powershell
# Bypasser l'execution policy
powershell -ep bypass

# Script complet -  génère le chemin LDAP
$PDC = [System.DirectoryServices.ActiveDirectory.Domain]::GetCurrentDomain().PdcRoleOwner.Name
$DN  = ([adsi]'').distinguishedName
$LDAP = "LDAP://$PDC/$DN"
$LDAP
# → LDAP://DC1.corp.com/DC=corp,DC=com
```

> `([adsi]'').distinguishedName` retourne le DN au bon format LDAP directement (`DC=corp,DC=com`), sans manipulation manuelle de la chaîne.

### Recherche LDAP avec DirectorySearcher

**Script de base -  lister tous les objets**

```powershell
$PDC  = [System.DirectoryServices.ActiveDirectory.Domain]::GetCurrentDomain().PdcRoleOwner.Name
$DN   = ([adsi]'').distinguishedName
$LDAP = "LDAP://$PDC/$DN"

$direntry    = New-Object System.DirectoryServices.DirectoryEntry($LDAP)
$dirsearcher = New-Object System.DirectoryServices.DirectorySearcher($direntry)
$dirsearcher.FindAll()
```

**Filtrer par type d'objet (`samAccountType`)**

```powershell
$dirsearcher.filter = "samAccountType=805306368"   # utilisateurs du domaine
$result = $dirsearcher.FindAll()

Foreach($obj in $result) {
    Foreach($prop in $obj.Properties) { $prop }
    Write-Host "-------------------------------"
}
```

| Valeur `samAccountType` | Objets retournés |
|---|---|
| `805306368` (`0x30000000`) | Utilisateurs |
| `805306369` | Machines |
| `268435456` | Groupes |

**Fonction réutilisable (`function.ps1`)**

```powershell
function LDAPSearch {
    param ([string]$LDAPQuery)
    $PDC = [System.DirectoryServices.ActiveDirectory.Domain]::GetCurrentDomain().PdcRoleOwner.Name
    $DN  = ([adsi]'').distinguishedName
    $DirectoryEntry    = New-Object System.DirectoryServices.DirectoryEntry("LDAP://$PDC/$DN")
    $DirectorySearcher = New-Object System.DirectoryServices.DirectorySearcher($DirectoryEntry, $LDAPQuery)
    return $DirectorySearcher.FindAll()
}
```

```powershell
Import-Module .\function.ps1

# Tous les utilisateurs
LDAPSearch -LDAPQuery "(samAccountType=805306368)"

# Tous les groupes
LDAPSearch -LDAPQuery "(objectclass=group)"

# Membres de tous les groupes (CN + member)
foreach ($group in $(LDAPSearch -LDAPQuery "(objectCategory=group)")) {
    $group.properties | select {$_.cn}, {$_.member}
}

# Membres d'un groupe spécifique
$sales = LDAPSearch -LDAPQuery "(&(objectCategory=group)(cn=Sales Department))"
$sales.properties.member

# Tous les attributs d'un utilisateur spécifique
$user = LDAPSearch -LDAPQuery "(&(objectCategory=user)(cn=<USERNAME>))"
$user.properties
```

> **Groupes imbriqués (nested groups)** : `net.exe` n'affiche que les utilisateurs directs. LDAP/DirectorySearcher retourne aussi les groupes membres -  ce qui peut révéler des héritages de privilèges non intentionnels.

### PowerView

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

### Service Principal Names (SPN)

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

### Permissions sur les objets AD (ACL/ACE)

Chaque objet AD a une ACL (Access Control List) composée d'ACEs (Access Control Entries). Permissions intéressantes pour un attaquant :

| Permission | Effet |
|---|---|
| `GenericAll` | Contrôle total sur l'objet |
| `GenericWrite` | Modifier certains attributs |
| `WriteOwner` | Changer le propriétaire |
| `WriteDACL` | Modifier les ACEs |
| `AllExtendedRights` | Reset de mot de passe, etc. |
| `ForceChangePassword` | Forcer le changement de mdp |
| `Self` | S'ajouter soi-même (ex: à un groupe) |

**Énumérer les ACEs d'un objet**

```powershell
Get-ObjectAcl -Identity "Management Department" | ? {$_.ActiveDirectoryRights -eq "GenericAll"} | select SecurityIdentifier,ActiveDirectoryRights
```

**Convertir un SID en nom lisible**

```powershell
Convert-SidToName S-1-5-21-1987370270-658905905-1781884369-1104

# Convertir plusieurs SIDs d'un coup
"S-1-5-...-512","S-1-5-...-1104" | Convert-SidToName
```

**Exploiter un GenericAll sur un groupe**

```cmd
:: Ajouter un utilisateur au groupe
net group "Management Department" stephanie /add /domain

:: Retirer l'utilisateur (cleanup)
net group "Management Department" stephanie /del /domain
```

> Un user standard avec `GenericAll` sur un objet est une misconfiguration -  permet d'ajouter des membres à des groupes, de reset des mots de passe, etc. Toujours nettoyer après exploitation.

### Partages du domaine

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

## Enumération automatique

### SharpHound

SharpHound collecte les données AD (LDAP, NetSessionEnum, Remote Registry…) et les exporte dans un ZIP analysable par BloodHound.

```bash
sudo apt install sharphound
sharphound -h
/usr/share/sharphound
```

**Collecte depuis la machine compromise**

```powershell
powershell -ep bypass
Import-Module .\Sharphound.ps1

Invoke-BloodHound -CollectionMethod All -OutputDirectory C:\Users\stephanie\Desktop\ -OutputPrefix "corp audit"
```

- `All` : collecte tout sauf les GPO locales (groupes, sessions, ACLs, SPNs, trusts…)
- Le résultat est un fichier ZIP à transférer sur Kali pour analyse dans BloodHound

> SharpHound crée aussi un fichier `.bin` (cache) -  inutile pour l'analyse, peut être supprimé.

**Option looping** -  relancer la collecte en boucle pour capturer les sessions qui changent :

```powershell
Invoke-BloodHound -CollectionMethod All -Loop -LoopDuration 02:00:00 -LoopInterval 00:05:00
```

### Netexec

```bash
nxc ldap 192.168.1.10 -u 'USER' -p 'PASSWORD' -d 'DOMAIN.COM' --bloodhound -c All --dns-server 192.168.1.10
```

### BloodHound-ce python

```bash
# https://github.com/dirkjanm/BloodHound.py
pipx install bloodhound-ce
bloodhound-ce-python --zip -c All -u 'USER' -p 'PASSWORD' -d 'DOMAIN.COM' -dc 'DC_FQDN' -ns 192.168.1.10
```

### BloodHound (Server)

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

