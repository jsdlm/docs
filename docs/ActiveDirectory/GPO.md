# Structure d'un GPT dans SYSVOL

Format : `\\domaine.com\SYSVOL\domaine.com\Policies\{GUID}`

```
{GUID}\
├── GPT.INI                    # version de la GPO
├── Machine\
│   ├── Registry.pol           # paramètres registre (Computer Config)
│   ├── Microsoft\Windows NT\SecEdit\
│   │   └── GptTmpl.inf        # security settings, restricted groups, password policy
│   ├── Scripts\
│   │   └── Startup\Shutdown
│   └── Preferences\
│       └── *.xml              # Group Policy Preferences (drives, tasks planifiées, etc.)
└── User\
    ├── Registry.pol
    ├── Scripts\
    │   └── Logon\Logoff
    └── Preferences\
        └── *.xml
```

# Énumération via LDAP

```
beacon> ldapsearch (objectClass=groupPolicyContainer) --attributes displayName,gPCFileSysPath

--------------------
displayName: AppLocker
gPCFileSysPath: \\contoso.com\SysVol\contoso.com\Policies\{GUID}
--------------------
```
# Fichiers clés pour l'énumération

## GptTmpl.inf (SecEdit)
PATH : `\\domaine.com\SYSVOL\domaine.com\Policies\{GUID}\Machine\Microsoft\Windows NT\SecEdit\GptTmpl.inf`

Contient Restricted Groups, Password Policy, Audit Policy, User Rights Assignment. Format INI texte, facile à parser. Identifie les groupes ayant des droits d'administration locale sur des postes/OU spécifiques.
```ini
[Unicode]
Unicode=yes
[Version]
signature="$CHICAGO$"
Revision=1
[Group Membership]
*S-1-5-21-3926355307-1661546229-813047887-1107__Memberof = *S-1-5-32-544
*S-1-5-21-3926355307-1661546229-813047887-1107__Members =
```

Ceci nous indique qu'un groupe de domaine avec le SID `S-1-5-21-3926355307-1661546229-813047887-1107` est membre d'un groupe local avec le SID `S-1-5-32-544`. On peut rechercher le SID du groupe de domaine dans BloodHound pour découvrir qu'il s'agit du groupe Server Admins.

![](img/Pasted%20image%2020260729221809.png)

Et on peut simplement rechercher le SID local dans la documentation de Microsoft, où S-1-5-32-544 correspond au groupe intégré Administrators. Cela signifie que tout membre du groupe Server Admins sera administrateur local sur les ordinateurs de l'OU Member Servers.

Ces chemins peuvent être ajoutés manuellement à BloodHound via une requête Cypher.

```
MATCH (x:Computer{objectid:'S-1-5-21-3926355307-1661546229-813047887-1110'})
MATCH (y:Group{objectid:'S-1-5-21-3926355307-1661546229-813047887-1107'})
MERGE (y)-[:AdminTo]->(x)
```

Où :

- S-1-5-21-3926355307-1661546229-813047887-1110 est le SID de lon-ws-1.
- S-1-5-21-3926355307-1661546229-813047887-1107 est le SID du groupe Server Admins.

## Registry.pol
PATH : `\\domaine.com\SYSVOL\domaine.com\Policies\{GUID}Machine\Registry.pol`

Format binaire propriétaire contenant les clés/valeurs de registre poussées. Nécessite un parser dédié (ex: `python-lgpo`).
Détecte des configurations de sécurité (ex: App Locker, LSA protection, UAC, etc.)

```
ls \\contoso.com\SysVol\contoso.com\Policies\{GUID}\Machine
download \\contoso.com\SysVol\contoso.com\Policies\{GUID}\Machine\Registry.pol
```

Once sync'd to your desktop, the file can be read using the `Parse-PolFile` cmdlet from the [GpRegistryPolicy](https://www.powershellgallery.com/packages/GPRegistryPolicy/0.3) module.

```powershell
Parse-PolFile -Path .\Desktop\Registry.pol
```
## Preferences (\*.xml)
Dans `Machine\Preferences\` ou `User\Preferences\` : format XML lisible directement. Sous-dossiers notables :

- `Groups\Groups.xml` : gestion de comptes/mots de passe locaux (historiquement vulnérable, cf. CVE-2014-1812 / MS14-025, mots de passe chiffrés avec une clé AES statique publiée par Microsoft).
- `Drives\Drives.xml` : mappages réseau.
- `ScheduledTasks\ScheduledTasks.xml` : tâches planifiées, peut contenir des credentials.
- `Services\Services.xml`, `Printers\Printers.xml`, etc.

Recherche de `cpassword` (mot de passe chiffré déchiffrable).

## Scripts : 
Dans `Machine\Scripts\` et `User\Scripts\`, souvent des `.bat`, `.vbs`, `.ps1`, intéressant car peuvent contenir des credentials en clair ou des chemins vers des ressources sensibles.

## GPT.INI
Simple fichier texte avec le numéro de version de la GPO (`Version=`), utile pour détecter les modifications récentes.
