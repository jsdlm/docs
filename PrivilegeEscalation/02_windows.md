# Windows

## Outils

* Mimikatz
* [winPEAS](https://github.com/peass-ng/PEASS-ng/tree/master/winPEAS)
* [LOLBAS](https://lolbas-project.github.io)

## Enumerating Windows

**Username et hostname**
```cmd
whoami
```

**Groupes de l'utilisateur courant**
```cmd
whoami /groups
```

**Utilisateurs locaux**
```powershell
Get-LocalUser
```
```cmd
net user
```

**Groupes locaux**
```powershell
Get-LocalGroup
```
```cmd
net localgroup
```

**Membres d'un groupe**
```powershell
Get-LocalGroupMember <groupname>
```

**OS, version et architecture**
```cmd
systeminfo
```

**Interfaces réseau**
```cmd
ipconfig /all
```

**Table de routage**
```cmd
route print
```

**Connexions réseau actives**
```cmd
netstat -ano
```

**Applications installées (32-bit et 64-bit)**
```powershell
Get-ItemProperty "HKLM:\SOFTWARE\Wow6432Node\Microsoft\Windows\CurrentVersion\Uninstall\*" | select displayname
Get-ItemProperty "HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\*" | select displayname
```

**Processus en cours d'exécution**
```powershell
Get-Process
```
