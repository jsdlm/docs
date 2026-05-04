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

net user <username>
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
# 32bits
Get-ItemProperty "HKLM:\SOFTWARE\Wow6432Node\Microsoft\Windows\CurrentVersion\Uninstall\*" | select displayname

# 64bits
Get-ItemProperty "HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\*" | select displayname
```
```cmd
dir "C:\Program Files"
dir "C:\Program Files (x86)"
dir C:\Users\<user>\Downloads
```

**Processus en cours d'exécution**
```powershell
Get-Process

# Process non standard Windows
Get-Process | Where-Object {$_.Path -notlike "C:\Windows\*" -and $_.Path -ne $null} | Select-Object Id, Name, Path, CPU, WS

# Path du binaire derrière le process
Get-Process NonStandardProcess | Select-Object Path
```
