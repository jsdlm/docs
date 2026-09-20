# Workflow Général

```text
┌──────────────────────────────────────────┐
│        1. INFORMATION GATHERING          │
│------------------------------------------│
│ - Identifier le scope                    │
│ - Découvrir les hôtes actifs             │
│ - Énumérer les ports et services ouverts │
└──────────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                         2. ENUMERATION                                  │
│-------------------------------------------------------------------------│
│ - Récupérer les détails de services (versions, banners)                 │
│ - Inspecter les web apps, shares, endpoints                             │
│ - Identifier les misconfigurations et fonctionnalités exposées          │
└─────────────────────────────────────────────────────────────────────────┘
                    │
                    ▼
      ┌────────────────────────────────────────────────┐
      │             3. VULNERABILITY ANALYSIS          │
      │------------------------------------------------│
      │ - Mapper les services aux faiblesses connues   │
      │ - Analyser configs, permissions, frameworks    │
      │ - Identifier les chemins d'attaque réalistes   │
      └────────────────────────────────────────────────┘
```

---
# Vecteurs par Fréquence

|Vecteur|Fréquence|Temps|Outils|
|:--|:-:|:-:|:--|
|Anonymous SMB/Web Share|60%|5–10 min|smbclient, curl|
|WordPress/CMS Vulnerability|40%|10–20 min|WPScan, Burp, manual|
|Weak Credentials (Default/Brute-force)|35%|5–15 min|Hydra, Medusa|
|Credential in File/Share|30%|10–20 min|grep, manual search|
|Unpatched Service (CVE)|25%|10–30 min|Exploit-DB, Metasploit|
|LDAP Null Bind|20%|5–10 min|ldapsearch, Python|
|SQL Injection|15%|15–30 min|SQLMap, manual|

---
# Checklist Initial Access

- Web app (WordPress, Joomla, custom app)
    
    - [ ] WPScan pour WordPress
    - [ ] Vérifier /admin, /login, /config
    - [ ] Chercher upload de fichiers
    - [ ] SQL injection, LFI
- SMB shares
    
    - [ ] Accès anonyme ?
    - [ ] Default credentials ?
    - [ ] Fichiers backup avec mots de passe ?
- LDAP
    
    - [ ] Null bind possible ?
    - [ ] Récupérer la liste d'utilisateurs
    - [ ] Comptes sans pre-auth ?
- Default credentials
    
    - [ ] Creds par défaut des applications
    - [ ] Mots de passe de service accounts dans les configs
- Code/fichiers manuels
    
    - [ ] Source code dans un dossier .git ?
    - [ ] Credentials hardcodés dans des fichiers
    - [ ] Commentaires dans HTML/PHP

---
# Checklist Web

- [ ] Identifier le stack (framework, serveur, CMS)
- [ ] Vérifier headers HTTP (Server, X-Powered-By, cookies)
- [ ] Vérifier SSL/TLS (cert info, hostnames SAN)
- [ ] robots.txt / sitemap.xml / changelog / readme
- [ ] Chercher des backups exposés (.zip, .tar, .old, .bak)
- [ ] Login pages / Admin panels / Upload functionality
- [ ] Search boxes / Filtering / Hidden form fields
- [ ] JavaScript : chemins cachés, credentials hardcodés, routes dépréciées
- [ ] Stack traces et messages d'erreur verbeux
- [ ] API endpoints, réponses pour champs cachés
- [ ] Version numbers dans les commentaires HTML
- [ ] Screenshot chaque page intéressante

---

# Low Hanging Fruit

- [ ] CMS/framework version obsolète
- [ ] Accès anonymous/guest sur des services
- [ ] Fichiers de config lisibles dans des shares
- [ ] Backups exposés (zip, tar, old)
- [ ] Test d'upload (type + contraintes de taille)
- [ ] Endpoints dépréciés
- [ ] Pages admin par défaut
- [ ] Réutilisation de mot de passe (username = password)
- [ ] Bases de données ouvertes sans credentials
- [ ] Répertoires world-readable ou shares mal configurés

---
# Rescanning

- [ ] Rescanner si bloqué - la précision de l'enum compte
- [ ] Ajuster le timing Nmap (T2/T3 vs T4/T5)
- [ ] Essayer des scanners ou wordlists différents
- [ ] Vérifier :
    - Utilisation de root/admin là où nécessaire
    - Outils non bloqués par firewall ou timeout
    - VPN/connexion stable
- [ ] Re-lancer des scans ciblés sur les ports "bizarres"
- [ ] Vérifier les changements après avoir interagi avec des services

---

# Mental Rules OSCP

- [ ] Ne pas sauter de machines au hasard - finir l'enum complète d'abord
- [ ] Documenter TOUT, surtout les anomalies
- [ ] Si bloqué : refaire la recon, élargir l'enum, rester systématique
- [ ] Mémo : Enumeration → Enumeration → Enumeration
- [ ] Identifier le rôle probable de la machine (dev box, file server, CMS host)
- [ ] Déduire le modèle de privileges (BD backend ? AD ? API interne ?)
- [ ] Construire une liste de :
    - Misconfigurations potentielles
    - Points d'authentification faibles
    - Artefacts de développement
    - Logique interne exposée
- [ ] Prioriser les cibles par simplicité et faisabilité
