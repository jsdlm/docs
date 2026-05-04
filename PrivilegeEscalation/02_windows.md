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

**Recherche de fichiers sensibles par extension**
```powershell
# Password manager databases
Get-ChildItem -Path C:\ -Include *.kdbx -File -Recurse -ErrorAction SilentlyContinue

# Fichiers de config et texte dans un répertoire applicatif
Get-ChildItem -Path C:\xampp -Include *.txt,*.ini -File -Recurse -ErrorAction SilentlyContinue

# Documents dans le home de l'utilisateur
Get-ChildItem -Path C:\Users\<user>\ -Include *.txt,*.pdf,*.xls,*.xlsx,*.doc,*.docx -File -Recurse -ErrorAction SilentlyContinue

Get-ChildItem -Path C:\Users\ -Include *.ini -File -Recurse -ErrorAction SilentlyContinue

# CMD
dir /s /b /a C:\*.txt
```

**Lire un fichier**
```powershell
# Aliases pour Get-Content
cat C:\path\to\file.txt
type C:\path\to\file.txt
gc C:\path\to\file.txt
Get-Content C:\path\to\file.txt
```

```cmd
type C:\path\to\file.txt
```

**Exécuter une commande en tant qu'un autre utilisateur**

Nécessite un accès GUI (RDP ou session physique) - le prompt de mot de passe n'accepte pas l'input depuis un bind shell ou WinRM.

```cmd
runas /user:<username> cmd
```

**Historique PowerShell (Get-History)**

Ne contient que les commandes de la session courante, effacé par `Clear-History`.

```powershell
Get-History
```

**Historique PSReadline**

Non effacé par `Clear-History` - contient l'historique persistant entre les sessions.

```powershell
(Get-PSReadlineOption).HistorySavePath
type C:\Users\<user>\AppData\Roaming\Microsoft\Windows\PowerShell\PSReadLine\ConsoleHost_history.txt
```

**Transcripts PowerShell**

Enregistrent toutes les commandes et leur output, peuvent contenir des credentials en clair.

```powershell
type C:\Users\Public\Transcripts\transcript01.txt
```

**Se connecter en WinRM avec des credentials**

```powershell
$password = ConvertTo-SecureString "<password>" -AsPlainText -Force
$cred = New-Object System.Management.Automation.PSCredential("<username>", $password)
Enter-PSSession -ComputerName <host> -Credential $cred
```

```bash
evil-winrm -i <ip> -u '<username>' -p '<password>'
```

**Event Viewer**

Logs les scripts PowerShell exécutés. Dans l'Event Viewer : `Applications and Services Logs > Microsoft > Windows > PowerShell > Operational`, filtrer par Event ID 4104. Chercher des mots de passe dans les entrées.

```powershell
Get-WinEvent -LogName "Microsoft-Windows-PowerShell/Operational" | Where-Object {$_.Id -eq 4104} | Select-Object TimeCreated, Message | Format-List
```
