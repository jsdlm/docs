# Enumération
## Enumération manuelle

### Outils legacy Windows (net.exe)

```cmd
:: Connexion RDP initiale (assumed breach)
xfreerdp /u:stephanie /d:corp.com /v:<IP>
```

> Préférer RDP à WinRM/PSRemoting pour l'énumération AD — PSRemoting entraîne le **Kerberos Double Hop** qui bloque les outils de domaine.

**Utilisateurs**

```cmd
net user /domain                     :: lister tous les utilisateurs du domaine
net user <username> /domain          :: détails d'un utilisateur (groupes, dernière connexion…)
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

# Script complet — génère le chemin LDAP
$PDC = [System.DirectoryServices.ActiveDirectory.Domain]::GetCurrentDomain().PdcRoleOwner.Name
$DN  = ([adsi]'').distinguishedName
$LDAP = "LDAP://$PDC/$DN"
$LDAP
# → LDAP://DC1.corp.com/DC=corp,DC=com
```

> `([adsi]'').distinguishedName` retourne le DN au bon format LDAP directement (`DC=corp,DC=com`), sans manipulation manuelle de la chaîne.

### Recherche LDAP avec DirectorySearcher

**Script de base — lister tous les objets**

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
$user = LDAPSearch -LDAPQuery "(&(objectCategory=user)(cn=<username>))"
$user.properties
```

> **Groupes imbriqués (nested groups)** : `net.exe` n'affiche que les utilisateurs directs. LDAP/DirectorySearcher retourne aussi les groupes membres — ce qui peut révéler des héritages de privilèges non intentionnels.

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
# Get-NetGroupMember ne retourne pas les attributs user — passer par Get-NetUser :
Get-NetGroupMember "Domain Admins" | ForEach-Object {
    Get-NetUser $_.MemberName | select cn, whencreated
}
```

> Chercher des comptes avec `pwdlastset` ancien ou `lastlogon` jamais utilisé → cibles idéales pour password attacks (politique plus laxiste, moins de surveillance).

