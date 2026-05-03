# Revue de code source

## Procédure
1. Télécharger [PMD](https://pmd.github.io/) - Néccéssite Java (Oracle.JDK.21 OK)
2. Télécharger le [ruleset Apex](https://github.com/pmd/pmd/tree/main/pmd-apex/src/main/resources/rulesets/apex).
3. Récupérer le code source

Le code source est exporté via la [Salesforce CLI](06_extractions.md).
Utiliser `package-CodeReview.xml`.

4. Lancer PMD avec le ruleset `apex` sur les sources exportées

`.\bin\pmd.bat check C:\Users\jlobel\Downloads\code_source\unpackaged\ -R .\quickstart.xml -f csv -r output.csv`
`/home/pentester/pmd-bin-7.23.0/bin/pmd check ./force-app/main/default/ -R ../../Documentation/quickstart.xml -f csv -r output.csv`

5. Importer le csv dans Excel puis filtrer sur la **catégorie `Security`**
6. Examiner manuellement chaque finding pour confirmer l'exploitabilité réelle et éliminer les faux positifs


## Points à check
| Thème | point à check |
|-------|-----------|
| **XSS** | escape="false" |
| **XSS et/ou CSRF** | ApexPages.currentPage().getParameters().get( |
| **SOQL injection** | String query = 'SELECT Id, Name FROM Account WHERE Name LIKE \'%' + userInput + '%\''; |
| **Informations disclosure** | System.debug( |
| **CRUD violation** | Absence de WITH USER_MODE ou de check de droits lors des opérations SOQL/DML  |
| **Sharing rules violation** | Absence de with sharing lors de la déclaration de la classe |

## Pages Visualforce - mots-clés à rechercher

Recherche globale dans VS Code sur les fichiers `.page` pour identifier les contrôleurs utilisés et les points d'entrée d'actions.

| Mot-clé | Rôle |
|---------|------|
| `controller=` | Déclare le contrôleur standard ou custom de la page |
| `extensions=` | Déclare les extensions du contrôleur |
| `<apex:commandButton` | Bouton qui appelle une action du contrôleur |
| `<apex:commandLink` | Lien qui appelle une action du contrôleur |
| `<apex:actionPoller` | Appel périodique d'une action (timer côté client) |
| `<apex:actionSupport` | Déclenche une action sur un événement DOM (onclick, onchange…) |
| `<apex:actionFunction` | Définit une fonction JavaScript qui appelle une action |
| `<apex:page action=` | Action appelée au chargement de la page |
| `<apex:inputField` | Champ lié au modèle — vérifier les droits FLS |
| `{!` | Expression Visualforce — identifier les propriétés et méthodes exposées |

Pour chaque contrôleur identifié, ouvrir la classe Apex correspondante et appliquer les contrôles de la section **Points à check** ci-dessus.

## Liens utiles
- [Secure Apex Classes](https://developer.salesforce.com/docs/platform/lwc/guide/apex-security.html)
- [Apex Security and Sharing](https://developer.salesforce.com/docs/atlas.en-us.apexcode.meta/apexcode/apex_security_sharing_chapter.htm)
- [Security Tips for Apex and Visualforce Development](https://developer.salesforce.com/docs/atlas.en-us.apexcode.meta/apexcode/pages_security_tips_intro.htm)
- [Annotations](https://developer.salesforce.com/docs/atlas.en-us.apexcode.meta/apexcode/apex_classes_annotation.htm)
- [Use the with sharing, without sharing, and inherited sharing Keywords](https://developer.salesforce.com/docs/atlas.en-us.apexcode.meta/apexcode/apex_classes_keywords_sharing.htm)
- [Controller Methods](https://developer.salesforce.com/docs/atlas.en-us.pages.meta/pages/pages_controller_methods.htm)

## Questions aux audités

| Thème | Questions |
|-------|-----------|
| **Processus de développement** | Quel est le processus de développement E2E ? Existe-t-il une revue de code ? |
| **Développement sécurisé** | Utilisent-ils des référentiels de sécurité (OWASP, guides Salesforce) ? Des formations sont-elles dispensées aux développeurs ? |
| **Qualité du code** | Un scan de code statique est-il en place ? Des tests unitaires sont-ils écrits et exécutés ? |
| **Versioning** | Quel système de versioning est utilisé (Git, SFDX…) ? |
| **Environnements** | Les environnements de développement, sandbox et production sont-ils séparés ? |
