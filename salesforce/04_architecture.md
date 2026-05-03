# Audit d'architecture

## Entretiens et revue de schéma

La majorité de cet axe repose sur des entretiens avec les équipes techniques et la revue de schémas d'architecture fournis par le client.

## Connected Apps et intégrations

| Point de contrôle | Questions / vérifications |
|-------------------|--------------------------|
| **Ségrégation des Connected Apps** | Une Connected App distincte est-elle utilisée par intégration ? |
| **Restriction des droits OAuth** | Les scopes OAuth sont-ils limités au strict nécessaire ? |
| **Comptes de service** | Quels comptes de service sont utilisés ? Sont-ils dédiés et à privilèges minimaux ? |
| **Contrôle d'accès IP** | Des restrictions IP sont-elles configurées sur les Connected Apps et les profils associés ? |
| **Exposition d'APIs** | Des APIs sont-elles exposées ? Comment l'authentification est-elle gérée (OAuth, certificat mTLS…) ? |

## Questions aux audités

| Thème | Questions |
|-------|-----------|
| **Environnements** | Quels environnements existent (dev, sandbox, pré-prod, prod) ? Sont-ils cloisonnés ? |
| **Intégrations** | Quels types d'intégrations sont en place (middleware, ETL, appels directs…) ? |
| **Identity Providers** | Quels IdP sont configurés ? Quelle est la configuration SAML/OIDC (assertions, attributs mappés, binding…) ? |
| **Sauvegardes** | Quelle est la fréquence des sauvegardes ? Des tests de restauration sont-ils effectués ? Les sauvegardes sont-elles stockées sur un système distinct de Salesforce ? |
