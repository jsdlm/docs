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

