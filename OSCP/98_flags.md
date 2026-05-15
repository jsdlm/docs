# Flags

## Trouver les Flags

### Windows CMD

```cmd
dir /s /b /a C:\local.txt

dir /s /b /a C:\proof.txt

dir /s /b /a C:\flag.txt
```

### Windows PowerShell

```powershell
Get-ChildItem -Path C:\ -Filter "local.txt" -Recurse -Force -ErrorAction SilentlyContinue

Get-ChildItem -Path C:\ -Filter "proof.txt" -Recurse -Force -ErrorAction SilentlyContinue

Get-ChildItem -Path C:\ -Filter "flag.txt" -Recurse -Force -ErrorAction SilentlyContinue
```

### Linux

```shell
find / -name "local.txt" 2>/dev/null
find / -name "proof.txt" 2>/dev/null
find / -name "flag.txt" 2>/dev/null
```

---
## Commandes de preuves

### User

**Linux**

```bash
cat /home/user/local.txt && hostname && whoami && ip a
```

**Windows**

```powershell
cmd /c 'type C:\Users\user\Desktop\local.txt && hostname && whoami && ipconfig'
```

### Root / Administrator

**Linux**

```bash
cat /root/proof.txt && hostname && whoami && ip a
```

**Windows**

```powershell
cmd /c 'type C:\Users\Administrator\Desktop\proof.txt && hostname && whoami && ipconfig'
```