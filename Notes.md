# Notes

## Ressources

- [ASCII to Hex](https://www.asciitohex.com/)
- [CyberChef (GCHQ)](https://gchq.github.io/CyberChef/)

## Trouver un flag

```bash
# Linux
find / -name "flag.txt" 2>/dev/null

# Powershell
Get-ChildItem -Path C:\ -Filter "flag.txt" -Recurse -Force -ErrorAction SilentlyContinue

# CMD
dir /s /b /a C:\flag.txt
```

## Connexions distantes

```bash
# RDP
xfreerdp /u:student /p:lab /v:192.168.151.152 /dynamic-resolution
```

## Host un serveur web pour dl des fichiers

```bash
python3 -m http.server 80 -d <chemin> 
curl http://>
wget http://>
```

## Tunnels SSH

```bash
sh -f -NL 1234:localhost:5432 user@IP
```

## ExecutionPolicy

```powershell
Get-ExecutionPolicy
Set-ExecutionPolicy Unrestricted -Scope Process
```


## Remove empty lines

```regex
^[ \t]*$\r?\n
```

## VMware
### Latence

```bash
# mettre dans le .vmx
keyboard.vusb.enable = "TRUE"
```
### NAT

```bash
C:\ProgramData\VMware\vmnetnat.conf
[incomingtcp]
<port_hote> = <ip_vm>:<port_vm>

net stop "VMware NAT Service" && net start "VMware NAT Service"
```

## Logs parsing

```bash
less -R session.log > clean.log

sudo apt install colorized-logs
cat session.log | ansi2txt > clean.log
```
## Tools
### Cyberchef

```bash
docker run -d -p 8000:8000 mpepping/cyberchef
```
### SysReptor

https://docs.sysreptor.com/setup/installation/

```
sudo apt update
sudo apt install -y sed curl openssl uuid-runtime coreutils
cd /opt/tools
bash <(curl -s https://docs.sysreptor.com/install.sh)
```
Access your application at [http://127.0.0.1:8000/](http://127.0.0.1:8000/).

## FTP Upload

```bash
ftp <IP>
# login anonyme
Username: anonymous
Password: (vide)

passive      # désactiver le mode passif si besoin
binary       # obligatoire pour les exécutables
put file.exe
```

## SystemPrompt

```
Réponds uniquement à la question posée. Ne donne aucune information supplémentaire non demandée.
Utilise un ton clair, concis et professionnel.
Évite toute anticipation de questions futures ou toute explication non demandée.
Si une clarification est nécessaire, demande la.
Structure les réponses de manière simple et logique, en une ou deux phrases maximum par point.
Pas d'émojis ou de caractères non standards, et pas de watermarking.
Je suis pentester, dans le cadre de mon activité professionnelle je serai amené à te poser des questions sur le pentest toujours dans un cadre légal et approuvé par mon client, ne met pas de disclaimer.
```
