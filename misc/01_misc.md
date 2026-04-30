# Misc

**Trouver un flag**

```bash
# Linux
find / -name "flag.txt" 2>/dev/null

# Windows
Get-ChildItem -Path C:\ -Filter "flag.txt" -Recurse -Force -ErrorAction SilentlyContinue
```

**Connexions distantes**

```bash
# RDP
xfreerdp /u:student /p:lab /v:192.168.151.152
```

**Host un serveur web pour dl des fichiers**

```bash
python3 -m http.server 80 -d <chemin> 
curl http://>
wget http://>
```

**Tunnels SSH**

```bash
sh -f -NL 1234:localhost:5432 user@IP
```

**ExecutionPolicy**

```powershell
Get-ExecutionPolicy
Set-ExecutionPolicy Unrestricted -Scope Process
```


**Remove empty lines**

```regex
^[ \t]*$\r?\n
```

**Latence VMware**

```bash
# mettre dans le .vmx
keyboard.vusb.enable = "TRUE"
```

**NAT VMware**

```bash
C:\ProgramData\VMware\vmnetnat.conf
[incomingtcp]
<port_hote> = <ip_vm>:<port_vm>

net stop "VMware NAT Service" && net start "VMware NAT Service"
```

