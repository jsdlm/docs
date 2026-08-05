# Revue documentaire

Prévoir un entretien avec les responsables de l'applicatif afin de demander une démonstration de l'utilisation de l'application, l'accès au code source, et l'accès à la documentation présente dans le tableau ci-dessous :

| Catégorie          | Exemples de documentation                                                                                                         | Éléments à examiner                                                                                                                                                                   |
| ------------------ | --------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Spécifications** | Cahier des charges, SFG (Spécifications Fonctionnelles Générales) et SFD (Spécifications Fonctionnelles Détaillées), user stories | Fonctionnalités de l'application, besoins métier auquel répond l'application ;<br><br>Fonctionnalités de sécurité (authentification, chiffrement, contrôle d'accès, etc..)            |
| **Architecture**   | Dossier d'Architecture Technique (DAT), schémas/diagrammes de flux                                                                | Technologies utilisées et dépendances tierces (bibliothèques, API externes) ;<br><br>Intégrations et flux de données ;<br><br>Composants exposés publiquement vs. composants internes |
| **Implémentation** | Normes de développement sécurisé                                                                                                  | Règles de développement sécurisées ;<br><br>Prise en compte des risques propres au langage/framework utilisé                                                                          |
| **Administration** | Guide d'exploitation, procédures de déploiement                                                                                   | Procédures de déploiement, gestion des secrets, comptes de service ;<br><br>Guides de configurations/durcissement                                                                     |
| **Utilisation**    | Manuel utilisateur, documentation d'API (eg. Swagger)                                                                             | Fonctionnalités et actions accessibles par profil utilisateur documenté ;<br><br>Endpoints/actions exposés par l'API et méthode d'authentification attendue                           |
| **Tests**          | Plan de tests, cahier de recette, rapports de tests (unitaires, intégration, SAST, DAST, UAT)                                     | Méthodologie et périmètre des tests réalisés (unitaires, intégration, automatisés via CI/CD, manuels) ;<br><br>Existence de tests de sécurité dédiés (SAST, DAST) et leur fréquence   |

---
# Revue technique

Une fois l'accès au code source obtenu, suivre la procédure ci-dessous pour effectuer la revue technique.

## Récupération des règles - Semgrep Rules Manager
https://github.com/iosifache/semgrep-rules-manager

Télécharge et agrège différents jeux de règles Semgrep (registre officiel, dépôts communautaires) dans un dossier local. Ces règles servent ensuite de base au scan SAST.

```bash
pipx install semgrep-rules-manager
mkdir ./rules
semgrep-rules-manager --dir ./rules download
```

## Exemples de règles par thème

| Thème                                       | Exemples de règles Semgrep (CWE)                                                                                                                                                                                                                                                                                                                                               |
| ------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| **Mécanismes d'authentification**           | `hardcoded-password-default-argument` (CWE-798: Use of Hard-coded Credentials)<br><br>`jwt-tokenvalidationparameters-no-expiry-validation` (CWE-613: Insufficient Session Expiration)<br><br>`PasswordComplexity` (CWE-521: Weak Password Requirements)                                                                                                                        |
| **Mécanismes cryptographiques**             | `use-of-md5` (CWE-328: Use of Weak Hash)<br><br>`weak-random` (CWE-330: Use of Insufficiently Random Values)<br><br>`insecure-hostname-verifier` (CWE-295: Improper Certificate Validation)                                                                                                                                                                                    |
| **Gestion des utilisateurs**                | `mass-assignment` (CWE-915: Improperly Controlled Modification of Dynamically-Determined Object Attributes)<br><br>`unprotected-mass-assign` (CWE-915)<br><br>`RpcImpersonateClient-ImpersonateLoggedOnUser` (CWE-250: Execution with Unnecessary Privileges)                                                                                                                  |
| **Contrôles d'accès aux ressources**        | `missing-or-broken-authorization` (CWE-862: Missing Authorization)<br><br>`httpservlet-path-traversal` (CWE-22: Improper Limitation of a Pathname to a Restricted Directory ('Path Traversal'))<br><br>`check-unscoped-find` (CWE-639: Authorization Bypass Through User-Controlled Key)                                                                                       |
| **Interactions avec d'autres applications** | `express-ssrf` (CWE-918: Server-Side Request Forgery (SSRF))<br><br>`documentbuilderfactory-external-general-entities-true` (CWE-611: Improper Restriction of XML External Entity Reference)<br><br>`mvc-missing-antiforgery` (CWE-352: Cross-Site Request Forgery (CSRF))                                                                                                     |
| **Validation des données**                  | `csharp-sqli` (CWE-89: Improper Neutralization of Special Elements used in an SQL Command ('SQL Injection'))<br><br>`unquoted-attribute-var` (CWE-79: Improper Neutralization of Input During Web Page Generation ('Cross-site Scripting'))<br><br>`os-command-injection` (CWE-78: Improper Neutralization of Special Elements used in an OS Command ('OS Command Injection')) |

## Scan SAST - OpenGrep
https://github.com/opengrep/opengrep

OpenGrep est un outil d'analyse statique permettant de rechercher des patterns de code, supportant plus de 30 langages, dont :

Apex · Bash · C · C++ · C# · Clojure · Crystal · Dart · Dockerfile · Elixir · Go · HTML · Java · JavaScript · JSON · Jsonnet · JSX · Julia · Kotlin · Lisp · Lua · OCaml · PHP · Python · R · Ruby · Rust · Scala · Scheme · Solidity · Swift · Terraform · TSX · TypeScript · Visual Basic · XML · YAML · Generic (ERB, Jinja, etc.)

Télécharger le binaire correspondant à l'OS depuis la [dernière release](https://github.com/opengrep/opengrep/releases/latest) du repo GitHub (ex. `opengrep_windows_x86.exe` pour Windows).

```powershell
$env:PYTHONUTF8=1
.\opengrep_windows_x86.exe scan --sarif-output=opengrep.sarif -f .\rules\ .\source_code\
```

Le résultat est exporté au format **SARIF** (Static Analysis Results Interchange Format), un format standard permettant d'interfacer les résultats avec d'autres outils (IDE, plateformes de gestion de vulnérabilités).

## Conversion SARIF vers CSV - sarif-tools
https://pypi.org/project/sarif-tools/

Convertit les résultats SARIF en CSV afin de faciliter l'analyse manuelle des findings dans Excel.

```bash
pipx install sarif-tools
sarif csv opengrep.sarif --output opengrep.csv
```

## Recherche de secrets
https://github.com/betterleaks/betterleaks

Recherche des secrets codés en dur dans le code source (clés API, identifiants, tokens, clés privées, etc...).

```bash
go install github.com/betterleaks/betterleaks@latest
betterleaks.exe dir .\source_code\ -v -f csv -r ./betterleaks.csv
```

## Analyse des résultats

1. Ouvrir le code source dans un IDE.
2. Importer les deux CSV générés (`opengrep.csv` et `betterleaks.csv`) dans un classeur Excel, un onglet par outil : **Données > À partir d'un fichier texte/CSV** > sélectionner le fichier > **Charger**.

Ajouter 3 colonnes à la suite de celles générées par l'outil :

| Colonne          | Valeurs                              | Usage                                                              |
| ---------------- | ------------------------------------ | ------------------------------------------------------------------ |
| **Faux positif** | VRAI / FAUX                          | Résultat de la vérification manuelle du finding                    |
| **Criticité**    | Critique / Élevée / Modérée / Faible | Renseignée uniquement si Faux positif = FAUX                       |
| **Commentaire**  | Texte libre                          | Justification, preuve (extrait de code), conditions d'exploitation |

3. Pour chaque ligne du fichier Excel, ouvrir le fichier source à la ligne indiquée par le finding (colonnes `Location`/`Line` pour le l'onglet OpenGrep, `File`/`StartLine` pour l'onglet betterleaks), et analyser le contexte selon les éléments suivants :

| Élément à vérifier                        | Question à se poser                                                                                                                                                                                                                                                                                                                                               |
| ----------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Appelants de la fonction / Exposition** | Remonter la pile d'appels, quelles fonctions/composants appellent la fonction vulnérable ?<br><br>S'agit-il d'une fonction atteignable (code mort, feature flag désactivé, code de test) ?<br><br>La fonction est-elle exposée publiquement, ou protégée par une authentification/autorisation/contrôle de rôle avant d'y accéder (interne, authentifié, admin) ? |
| **Nature de l'input**                     | La donnée manipulée est-elle un véritable *user input* (paramètre de requête, formulaire, upload, header...) ou une donnée interne/de confiance (constante, config, valeur générée côté serveur) ?                                                                                                                                                                |
| **Sanitization/validation existante**     | Y a-t-il un échappement, un encodage, une whitelist, une regex de validation, une requête paramétrée/ORM, etc. en amont ou en aval qui mitige le risque ?<br><br>Le framework/langage utilisé applique-t-il des contrôles par défaut qui mitigent le risque ?                                                                                                     |

En fonction des résultats des éléments analysés, renseigner Faux positif, puis si applicable Criticité et Commentaire