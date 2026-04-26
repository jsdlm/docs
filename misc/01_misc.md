# Misc

**Trouver un flag**

```bash
# Linux
find / -name "flag.txt" 2>/dev/null

# Windows
Get-ChildItem -Path C:\ -Filter "flag.txt" -Recurse -ErrorAction SilentlyContinue
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

**Phishing - Cloner une page web**

```bash
# -E  : ajuste les extensions (.php → .html)
# -k  : convertit les liens pour navigation locale
# -K  : garde le fichier original en .orig
# -p  : télécharge tous les éléments de la page (CSS, images...)
# -H  : autorise les domaines externes (span hosts)
# -D  : restreint au domaine spécifié
# -nd : pas de sous-dossiers, tout à plat
wget -E -k -K -p -e robots=off -H -Dzoom.us -nd "https://zoom.us/signin#/login"
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
