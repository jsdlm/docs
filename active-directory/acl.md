# ACL

## Exploitation des droits/ACLs

* **ForceChangePassword** : Réinitialiser le mot de passe d’un utilisateur sans connaître l'ancien → prise de contrôle immédiate du compte.
* **GenericWrite** : Écriture sur plusieurs attributs de l’objet (user ou computer) → permet :
  * Ajout de clé publique (Shadow Credentials)
  * Ajout d’un SPN (Targeted Kerberoasting)
  * Manipulation de chemins LDAP (`profilePath`, `scriptPath`) pour capture de hash ou exécution.
* **WriteDACL** : Modifier les permissions (ACL) de l’objet → permet de t’accorder `GenericAll`, puis effectuer toutes les actions possibles sur la cible.
* **AddMember** : Ajouter un utilisateur à un groupe → si groupe à privilèges, escalade immédiate.
* **WriteOwner** : Changer le propriétaire d’un objet → une fois propriétaire, tu peux modifier les ACL et donc t’octroyer `GenericAll`.
* **GenericAll** : Contrôle total sur l’objet (user, group, computer) → changer mot de passe, injecter clé, manipuler les SPN, tout.
* **GPO abuse** : Modifier une stratégie de groupe pour exécuter un payload sur une machine ou sur tous les utilisateurs visés.
* **Read LAPS password** : Lire les mots de passe locaux administrateur gérés par LAPS → accès local admin sur les machines cibles.
* SeEnableDelegationPrivilege : délégation de contrainte.

## Exploitation de droits spécifiques

* **Shadow Credentials** : si `GenericWrite` sur un compte → injection de clé PKINIT (via `Whisker`, `ForgeCert`, etc.).
  * [https://jsdlm.gitbook.io/docs/active-directory/adcs#shadow-credentials](https://jsdlm.gitbook.io/docs/active-directory/adcs#shadow-credentials)
* **sAMAccountName Spoofing** : si droit de **joindre une machine** (10 par défaut), et DC vulnérable.
  * [https://jsdlm.gitbook.io/docs/active-directory/acces-authentifie#samaccountname](https://jsdlm.gitbook.io/docs/active-directory/acces-authentifie#samaccountname)
* **Resource-Based Constrained Delegation (RBCD)** : si contrôle sur un objet machine.
* **DCSync** : si accès à `Replicating Directory Changes (All)` sur le domaine.
