# Tunnel SSH

## Local Port Forwarding

Écoute sur un port du client SSH, forward les paquets via le tunnel vers une destination choisie côté serveur SSH.

```
ssh -f -N -L [LOCAL_IP:]LOCAL_PORT:DEST_IP:DEST_PORT user@ssh_server
```

`LOCAL_IP` est optionnel, par défaut `127.0.0.1` (accessible uniquement en local). Mettre `0.0.0.0` pour exposer le port sur toutes les interfaces.


| Flag | Description |
|------|-------------|
| `-f` | Passe SSH en arrière-plan juste avant l'exécution (libère le terminal) |
| `-N` | Ne pas ouvrir de shell distant — juste maintenir le tunnel |
| `-L` | Définit la règle de port forwarding local `[LOCAL_IP:]LOCAL_PORT:DEST_IP:DEST_PORT` |
| `-v` | Mode verbose pour débugger la connexion |
**Vérifier que le port écoute sur la machine pivot**

```bash
ss -ntplu
```

### Accéder à un service localhost de la machine distante

Accéder depuis sa propre machine à un service qui écoute uniquement sur `localhost` côté serveur distant (ex: PostgreSQL sur 5432) :

```bash
ssh -f -N -L 1234:localhost:5432 user@<ip>
```

Se connecter ensuite avec `psql -h localhost -p 1234`.

### Accéder à une machine d'un réseau interne via un pivot

Depuis une machine pivot qui a accès à un réseau interne inaccessible directement, forwarder un port local vers un service sur une autre machine du réseau interne. Exemple : écouter sur le port 4455 de CONFLUENCE01 et forwarder vers le port SMB 445 d'une machine interne :

```bash
ssh -f -N -L 0.0.0.0:4455:<IP_MACHINE_DISTANTE>:445 user@<IP_PIVOT>
```


**Utiliser le tunnel depuis Kali**

```bash
# SMB
smbclient -p 4455 -L //<IP_PIVOT>/ -U <user> --password=<password>
smbclient -p 4455 //<IP_PIVOT>/<share> -U <user> --password=<password>

# SSH
ssh <user>@<IP_PIVOT> -p 4455

# PostgreSQL
psql -h <IP_PIVOT> -p 4455 -U <user>
```
