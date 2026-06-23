# Upgrade to Fully Interactive TTYs

**Note:** To check if the shell is a TTY shell use the `tty` command.
# Shell to Bash

Upgrade from shell to bash.

```sh
SHELL=/bin/bash script -q /dev/null
```

# Python PTY Module

Spawn `/bin/bash` using [Python’s PTY module](https://docs.python.org/3/library/pty.html), and connect the controlling shell with its standard I/O.

```sh
python -c 'import pty; pty.spawn("/bin/bash")'
```

## Fully Interactive TTY

Background the current remote shell (`^Z`), update the **local** terminal line settings with `stty` bring the remote shell back.

```sh
# Étape 1 -  dans le reverse shell
python -c 'import pty; pty.spawn("/bin/bash")'

# Étape 2 -  mettre en arrière-plan
Ctrl-Z

# Étape 3 -  sur Kali
stty raw -echo && fg

# Étape 4 -  dans le reverse shell
reset
```

After bringing the job back the cursor will be pushed to the left. Reinitialize the terminal with `reset`.