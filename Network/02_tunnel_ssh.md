# Tunnel SSH

## Local Port Forwarding

Écoute sur un port du client SSH, forward les paquets via le tunnel vers une destination choisie côté serveur SSH.

```
[LOCAL_IP:]LOCAL_PORT:DEST_IP:DEST_PORT
```

**Créer le tunnel depuis la machine pivot**

```bash
ssh -f -N -L 0.0.0.0:<port_local>:<ip_dest>:<port_dest> <user>@<ssh_server>
```

Exemple : écouter sur le port 4455 de CONFLUENCE01 et forwarder vers le port SMB 445 d'une machine interne :

```bash
ssh -f -N -L 0.0.0.0:4455:172.16.50.217:445 database_admin@10.4.50.215
```

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

**Utiliser le tunnel depuis Kali**

```bash
# SMB
smbclient -p 4455 -L //<ip_pivot>/ -U <user> --password=<password>
smbclient -p 4455 //<ip_pivot>/<share> -U <user> --password=<password>

# SSH
ssh <user>@<ip_pivot> -p 4455

# PostgreSQL
psql -h <ip_pivot> -p 4455 -U <user>
```
