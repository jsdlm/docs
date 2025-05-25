# Misc

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
