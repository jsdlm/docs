## 3. Revue de configuration

### Revue via l'interface web

#### Politiques de mot de passe
- Accéder aux paramètres (Setup > Security > Password Policies)
- Vérifier :
  - Longueur minimale ≥ 12 caractères
  - Complexité activée
  - Expiration ≤ 90 jours
  - Verrouillage après ≤ 5 tentatives
  - Historique ≥ 10 mots de passe
- Toute déviation → **FINDING**

#### Authentification multi-facteurs (MFA)
- Accéder à (Setup > Identity > Identity Verification)
- Vérifier que MFA est :
  - Obligatoire pour tous les utilisateurs → sinon **FINDING**
  - Activé au niveau de l’organisation (et non optionnel)
- Vérifier que les administrateurs utilisent des méthodes fortes

#### Single Sign-On (SSO)
- Accéder à (Setup > Identity > Single Sign-On Settings)
- Vérifier :
  - Certificat IdP valide (non expiré)
  - Assertions SAML signées et chiffrées
  - Provisioning JIT avec permissions minimales
- Mauvaise configuration → **FINDING**

#### Organisation-Wide Defaults (OWD)
- Accéder à (Setup > Security > Sharing Settings)
- Vérifier que les objets sensibles sont en **Private**
- Si accès trop ouvert par défaut → **FINDING**

#### Règles de partage
- Accéder à (Setup > Security > Sharing Settings > Sharing Rules)
- Identifier les règles trop larges :
  - Partage global avec tous les utilisateurs → **FINDING**
  
#### API
- Vérifier les profils avec permission **API Enabled**
- Restreindre aux comptes nécessaires uniquement
- Vérifier :
  - Utilisation TLS 1.2+
  - Utilisation de **Named Credentials**
- Non conformité → **FINDING**

#### Paramètres de session
- Accéder à (Setup > Security > Session Settings)
- Vérifier :
  - Timeout ≤ 2h
  - Restriction IP activée
  - HTTPS obligatoire
  - Protection clickjack activée
- Sinon → **FINDING**

#### Certificats
- Accéder à (Setup > Security > Certificate and Key Management)
- Vérifier :
  - Certificats expirés → **FINDING**
  - Certificats auto-signés en production → **FINDING**
  
#### Flows & automatisations
- Accéder à (Setup > Process Automation > Flows)
- Identifier :
  - Flows actifs avec accès système
- Vérifier contrôles d’accès → sinon **FINDING**

#### Packages installés
- Accéder à (Setup > Apps > Installed Packages)
- Vérifier :
  - Utilisation réelle
  - Version à jour
  - Statut sécurité AppExchange
- Package obsolète → **FINDING**

#### Chiffrement (Shield)
- Accéder à (Setup > Security > Platform Encryption)
- Vérifier :
  - Données sensibles chiffrées
  - Gestion des clés (rotation, stockage)
- Sinon → **FINDING**

#### Chiffrement classique
- Vérifier utilisation du type **Encrypted**
- Identifier limites → recommander Shield si nécessaire
```
SELECT QualifiedApiName, DataType 
FROM FieldDefinition 
WHERE DataType = 'EncryptedText'
```
#### Données en transit
- Vérifier TLS 1.2+ sur toutes les intégrations (HTTP/HTTPS)
- openssl s_client -connect yourInstance.salesforce.com:443 -tls1_2
- Non conformité → **FINDING**

#### Health Check
- Accéder au **Health Check** natif Salesforce (Setup > Health Check)
- Prendre des captures d'écran de chaque paramètre non conforme
- Documenter l'écart par rapport au score recommandé par Salesforce

#### Connected Apps
- Recenser les **Connected Apps** managées (Setup > Connected Apps > Manage Connected Apps)
  - Lignes avec `Permitted Users = All users may self-authorize` -> **FINDING**
  - Lignes avec `Permitted Users = 	Admin approved users are pre-authorized` -> Ok whitelist par profil
- Analyser les **tokens OAuth actifs** via la page d'usage (Setup > Connected Apps > Connected Apps OAuth Usage) :
  - Ligne avec bouton `Install` : Connected App utilisée sans être gérée dans l'instance Salesforce - **FINDING**
  - Ligne avec bouton `Uninstall` : Connected App installée et gérée dans l'instance - **OK**
  - Ligne sans bouton `Install`/`Uninstall` : Connected App native, créée directement dans cette instance Salesforce - **OK**
- Extraire les **tokens OAuth actifs** via SOQL :

```sql
SELECT Id, AppName, UserId, CreatedDate, LastUsedDate, UseCount, AppMenuItemId, User.Name FROM OAuthToken
```

- Extraire la **configuration des Connected Apps** (validité des refresh tokens, restrictions d'accès) :

```sql
SELECT Id, Name, OptionsAllowAdminApprovedUsersOnly, RefreshTokenValidityPeriod, OptionsRefreshTokenValidityMetric FROM ConnectedApplication
```

  - `OptionsAllowAdminApprovedUsersOnly = true` → accès restreint aux utilisateurs approuvés par l'admin - **OK**
  - `OptionsAllowAdminApprovedUsersOnly = false` → tout utilisateur peut autoriser l'app - **FINDING potentiel**


### Revue via les métadonnées

Le code source est exporté via la [Salesforce CLI](06_extractions.md).
Utiliser `package-ConfigurationReview.xml`.
À partir des métadonnées exportées, analyser les fichiers de profils dans VS Code via une **recherche globale** dans le workspace.

| Contrôle | Détail |
|----------|--------|
| **Approbation de Connected Apps non autorisées** | Identifier quel profil dispose du droit d'approuver des Connected Apps sans autorisation préalable (`CanApproveUninstalledApps`) |
| **Accès API** | Identifier les profils avec `ApiEnabled` |
| **Filtrage par IP** | Vérifier si des restrictions IP (`loginIpRanges`) sont configurées sur les profils sensibles |
| **Permissions** | Passer en revue les `userPermissions` des profils custom `<custom>true</custom>` pour identifier les profils à hauts privilèges |
| **Option - Field Level Security** | Vérifier `fieldPermissions` sur champs sensibles |

### Liens utiles
- [Salesforce Network Access and Profile-Based IP Restrictions](https://help.salesforce.com/s/articleView?id=000386441&type=1)
