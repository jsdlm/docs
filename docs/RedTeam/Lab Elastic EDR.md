## 1. Serveur (Linux, Docker et Docker Compose installés)

```bash
apt-get update
apt-get install jq git curl
git clone https://github.com/peasead/elastic-container.git
cd elastic-container
```

Adapter `.env` :

- `ELASTIC_PASSWORD` et `KIBANA_PASSWORD` : remplacer `changeme`.
- `STACK_VERSION` : mettre la dernière version stable, visible sur https://www.elastic.co/downloads/elasticsearch (format `x.y.z`).
- ``LICENSE``=``trial``

Lancer :
```
chmod +x elastic-container.sh
./elastic-container.sh start
```

Attendre le message "Browse to https://localhost:5601".

## 2. Kibana

1. Se connecter sur `https://IP_SERVEUR:5601` avec l'utilisateur `elastic` et le mot de passe du `.env`.
2. **Stack Management > License Management** : démarrer l'essai de 30 jours (nécessaire pour Elastic Defend).
3. **Management > Fleet** : si Kibana demande d'ajouter un Fleet Server, ne rien installer. Il est déjà déployé par le script, il suffit de vérifier dans **Fleet > Settings > Fleet Server hosts** que l'adresse est `https://IP_SERVEUR:8220`.

Output Elasticsearch : **Fleet > Settings > Outputs > default**, Hosts = `https://IP_SERVEUR:9200`.
Si l’agent est Unhealthy avec “Elasticsearch connection failure” : l’IP de l’output est mauvaise ou injoignable.

## 3. Ajouter l'agent

1. **Fleet > Agents > Add agent**
2. Laisser la policy **Endpoint Policy** (Elastic Defend)
3. **Enroll in Fleet**, onglet **Windows**

## 4. Sur le Windows

PowerShell en administrateur :
```powershell
mkdir C:\Temp
cd C:\Temp
```

Copier-coller toutes les lignes affichées par Kibana sauf la dernière (téléchargement, extraction, `cd`).

Pour la dernière (`.\elastic-agent.exe install ...`), la copier et ajouter à la fin :
```
--insecure -f
```

## 5. Vérification

- **Fleet > Agents** : le Windows est **Healthy**.
- **Security > Manage > Endpoints** : la machine est **Healthy**.

## Astuces

### Policy Elastic Defend
- **Security > Manage > Policies**, onglet **Windows**.
- Prévention : **Prevent**. Détection seule (sans blocage) : **Detect**.
- Un changement de policy s’applique à l’agent en une à deux minutes, sans réinstallation.
- Fenêtre Elastic Defend visible dans Windows Security : **Register as antivirus** = **Enabled** (en Detect, elle disparaît sinon, car Elastic se désinscrit comme antivirus).
### Alertes
- **Security > Alerts** (ou `/app/security/alerts`)
- La règle **Endpoint Security** doit être activée dans **Security > Rules > Detection rules**, sinon les alertes de l’agent n’apparaissent pas.
- Activer les règles Windows en masse : **Detection rules**, filtre tag `Windows`, **Bulk actions > Enable**.
- Vérifier la remontée des données : Discover, data view `logs-endpoint.alerts-*`.
- Vue par machine : **Security > Manage > Endpoints**, puis **Policy Response**.