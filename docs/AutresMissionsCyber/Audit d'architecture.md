# 3.1 Présentation générale de l'architecture et des enjeux de sécurité

- Pouvez-vous présenter l'architecture générale ?
- Quel est le rôle de cette architecture, quels services héberge-t-elle ?
- Quelles sont les technologies utilisées ? (serveurs, hyperviseurs, bases de données, équipements réseau)
- Quelles sont les interconnexions avec des systèmes tiers ?
- Quels types de données sont hébergées et/ou traitées au sein de cette infrastructure ?

# 3.2 Documentation

- Documentation à demander :
    - les documents d'architecture technique (DAT) ;
    - les schémas d'architecture de niveau 2 et 3 du modèle OSI ;
    - les matrices de flux ;
    - les inventaires des interconnexions avec des réseaux tiers ou Internet ;
    - l'inventaire des assets (précisant leur nom, rôle, localisation physique, adresse IP, VLAN, composants logiciels et versions).
- Les documents sont-ils à jour ?

# 3.3 Configuration

## 3.3.1 Liste des composants

- Cf. inventaire des assets (et technologies)

## 3.3.2 Identification des composants et services

- Cf. inventaire des assets (et technologies)

## 3.3.3 Processus de veille sur les composants

- Existe-t-il un processus de veille technologique et de gestion des vulnérabilités ?
- Qui réalise cette veille ?
- À quelle fréquence est-elle réalisée ?
- Quelles sources sont consultées ?
- Quels canaux d'alerte sont utilisés ?
- Une procédure de veille est-elle formalisée ?

## 3.3.4 Mises à jour

- Existe-t-il une procédure de gestion des mises à jour ?
- Les mises à jour sont-elles déployées manuellement ou automatiquement ?
- À quelle fréquence sont-elles déployées ?
- Les mises à jour critiques peuvent-elles être déployées rapidement ?
- Des tests sont-ils réalisés avant leur déploiement ?

## 3.3.5 Durcissement des configurations

- Des mesures de durcissement sont-elles appliquées ?
- Sur quels composants sont-elles appliquées ?
- Quel référentiel de durcissement est utilisé : CIS, guide éditeur ou autre référentiel ?
- Sont-elles revues périodiquement ?

## 3.3.6 Déploiement des configurations

- Les configurations sont-elles déployées automatiquement ?
- Quels outils sont utilisés : Ansible, Vagrant, Terraform, Dockerfile, Docker Compose ou Docker Swarm ?
- Les configurations durcies sont-elles appliquées dès le déploiement des composants ?
- Quels comptes de service sont utilisés pour déployer les configurations ?
- Quels privilèges possèdent ces comptes de service ?
- Ces privilèges sensibles sont-ils nécessaires ?

## 3.3.7 Identification de services à décommissionner

- Certains services présents dans l'architecture ne sont-ils plus utilisés, ou sont-ils prévus d'être décommissionnés ?
- Si oui, sont-ils toujours maintenus, suivent-ils toujours les mêmes procédures que les autres composants ? (MAJ, configuration, etc.)

# 3.4 Architecture réseau

## 3.4.1 Description du réseau

- Quelles sont les différentes parties de l'infrastructure ?
- Quelles parties sont accessibles depuis Internet ?
- Quelles parties sont accessibles uniquement depuis un réseau interne ?
- Dans quel environnement ou chez quel hébergeur l'application est-elle déployée ?
- Quels services composent l'application ?
- Quels flux relient ces services ?

## 3.4.2 Segmentation

- Une segmentation / un filtrage est-il appliqué sur les différentes sections de l'infra ?
- Quels flux sont autorisés entre les différentes zones ?
- Le filtrage est-il réalisé selon les adresses IP, ports, protocoles et sens des flux ?
- Les règles de pare-feu peuvent-elles être présentées ?
- L'infra est-elle accessible depuis un VPN ?
    - Si un VPN est utilisé, repose-t-il sur TLS ou IPsec ?
    - Quelle version d'IKE est utilisée ?
    - L'authentification IKE repose-t-elle sur une PKI ou un secret prépartagé ?
- Une micro-segmentation est-elle appliquée au niveau des serveurs ? (pare-feu locaux limitant les flux sur le serveur)

# 3.5 Chiffrement

## 3.5.1 Données au repos

- Dans quels emplacements les données sont-elles stockées : bases de données, fichiers ou services de stockage ?
- Le chiffrement est-il appliqué dans le code applicatif, dans la configuration de la base de données ou au niveau du stockage ?
- Quels algorithmes sont utilisés ?
- Quelles longueurs de clé sont utilisées ?

## 3.5.2 Données en mouvement

- Quels flux transportent des données sensibles ? Ces flux sont-ils chiffrés ?

# 3.6 Contrôle d'accès

- Le contrôle d'accès repose-t-il sur des comptes applicatifs, des comptes locaux, un SSO, un annuaire LDAP ou un mécanisme ZTNA ?
- Quelles populations peuvent accéder à l'application ?

## 3.6.1 Authentification

- Quelles interfaces de l'application nécessitent une authentification : IHM, API, SSH, FTP, SMB ou RDP ?
- Quels facteurs d'authentification sont utilisés ? Une authentification multifacteur est-elle appliquée ?
- Quelle politique de mot de passe est configurée au niveau applicatif ?
- Un mécanisme de blocage des comptes existe-t-il ?
- Comment les comptes système / de service s'authentifient-ils ?

## 3.6.2 Autorisation

- Quels sont les différents niveaux de droits / profils ?
- Comment les autorisations sont-elles vérifiées ?
- Quel référentiel porte les rôles et les droits ?
- Sur quelles données repose la décision d'autorisation ?

# 3.7 Hébergement des noms de domaine

- Qui possède et gouverne les noms de domaine utilisés par l'application ?
- Quels noms de domaine et sous-domaines sont utilisés ?
- Qui assure leur administration et leur hébergement ?
- Les domaines connexes sont-ils possédés ou protégés ?
- Leur absence de possession pourrait-elle permettre des attaques de phishing ?
- Les enregistrements SPF, DKIM et DMARC sont-ils configurés lorsque cela est pertinent ?

# 3.8 Administration

- Quelles populations administrent l'application : équipes métier, techniques, hébergeur ou prestataire cloud ?

## 3.8.1 Postes d'administration

- Des postes dédiés à l'administration sont-ils utilisés ?
- Ces postes sont-ils homologués ?
- Sont-ils audités régulièrement ?
- Leurs configurations sont-elles durcies ?

## 3.8.2 Accès administration

- Quel est le chemin complet suivi par un administrateur pour atteindre l'environnement ?
- Machine de rebond / bastion ?
- Quels protocoles sont utilisés à chaque étape : RDP, SSH ou interface web ?
- Expliquer les mécanismes d'authentification à chaque étape (mot de passe, MFA, certificats)
- Les certificats SSH sont-ils individuels ?
- Les comptes utilisés sur les serveurs cibles sont-ils nominatifs ou génériques ?
- Les actions peuvent-elles être rattachées à un administrateur précis ?
- Un VPN est-il utilisé ? L'infra d'administration est-elle accessible depuis un VPN ?
    - Si un VPN est utilisé, repose-t-il sur TLS ou IPsec ?
    - Quelle version d'IKE est utilisée ?
    - L'authentification IKE repose-t-elle sur une PKI ou un secret prépartagé ?

# 3.9 Haute disponibilité

- Quelles sont les exigences de disponibilité de l'application ?
- Le service doit-il être accessible 24 h/24 et 7 j/7 ?
- Quel objectif de disponibilité a été défini ?
    - RTO (Recovery Time Objective) : X heures
    - RPO (Recovery Point Objective) : X heures

## 3.9.1 Mise à l'échelle

- L'application fonctionne-t-elle en cluster en situation nominale ?
- Quels mécanismes de mise à l'échelle sont utilisés ?
- La mise à l'échelle est-elle verticale ou horizontale ?
- Est-elle déclenchée manuellement ou automatiquement ?
- Des seuils de déclenchement sont-ils définis ?
- Plusieurs instances de bases de données sont-elles actives ?
- Quels mécanismes empêchent un split brain ?

## 3.9.2 Redondance des sites

- Combien d'exemplaires de l'application existent par datacenter ?
- L'architecture est-elle répartie sur au moins deux datacenters ?
- Quelle distance sépare les datacenters ?
- Les sites fonctionnent-ils en actif/actif ou en actif/passif ?
- Le site de secours est-il un cold site, warm site ou hot site ?
- En actif/passif, la bascule est-elle manuelle ou automatique ?
- En actif/actif, comment le trafic est-il réparti ?
- Comment les bases de données sont-elles synchronisées entre les sites ?
- Quels mécanismes préviennent un split brain ?

## 3.9.3 Plan de Continuité d'Activité et Plan de Reprise d'Activité

- Un PCA et un PRA sont-ils formalisés ? → si oui, analyse de la documentation
- Les procédures sont-elles testées régulièrement ?

# 3.10 Sauvegardes

- Quelle politique de sauvegarde est appliquée ?
- Quelles données et quels composants sont sauvegardés ?
- Comment les sauvegardes sont-elles gérées ?
- Quelle durée de conservation est appliquée ?
- Les sauvegardes sont-elles immuables ?
- Le principe 3-2-1-1 est-il respecté : trois copies, deux supports, une copie hors ligne et une copie testée ?
- Des tests de restauration sont-ils réalisés ?

# 3.11 Journalisation et supervision de sécurité

## 3.11.1 Journalisation

- Quels journaux système/applicatifs sont collectés ?
- Les journaux sont-ils externalisés ou centralisés ?
- Les journaux sont-ils conservés de manière sécurisée ?
- Quelles durées de conservation sont appliquées ?

## 3.11.2 Supervision

- La supervision est-elle assurée par l'entité auditée, un autre service ou un prestataire ?
- Un SIEM est-il utilisé ?
- Des scénarios de détection sont-ils définis ?
- Quels journaux et événements sont exploités par la supervision ?
- Un EDR est-il utilisé pour détecter et contenir les comportements suspects ?

# 3.12 Gestion des secrets

- Où sont stockés les mots de passe/clés API ?

# 3.13 Défense en profondeur

## 3.13.1 Pare-feu applicatif

- Un pare-feu applicatif protège-t-il les interfaces web ou les API ?

## 3.13.2 Antivirus & EDR

- Un antivirus est-il installé sur tous les serveurs ?
- Un EDR est-il installé sur tous les serveurs ?
- Un IDS ou un IPS est-il également utilisé ?
- Les fichiers téléversés sont-ils analysés par un antivirus ?

## 3.13.3 Protection anti-DDoS

- Une protection anti-DDoS est-elle en place ? Quelle solution ?

# 3.14 Sécurité des développements

- La sécurité est-elle intégrée dans le cycle de développement ?
- Une démarche DevSecOps est-elle mise en œuvre ?
- Des revues de code source sont-elles réalisées ? Manuelles / automatiques ?
    - Quels outils ? Statique / dynamique ?
- Des scans de vulnérabilités sont-ils réalisés pendant le développement ?
