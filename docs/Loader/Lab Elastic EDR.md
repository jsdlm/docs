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