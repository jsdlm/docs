
# To check if MDI is in use
```bash
# to find if MDI is in use, check for
https://<your-workspace-name>sensorapi.atp.azure.com
ex:
https://yhp0wsensorapi.atp.azure.com
```
# OPSEC BLOODHOUND - LDAP
## Sharphound
- To make BloodHound collection stealthy, remove noisy collection methods like RDP, DCOM, PSRemote and LocalAdmin.
- Use the -ExcludeDCs to avoid detection by MDI

```bash
# Detected by MDI
SharpHound.exe --collectionmethods All

# More opsec friendly, but still detected by MDI
# --excludedcs           (Default: false) Exclude domain controllers from session/localgroup enumeration
SharpHound.exe --collectionmethods Group,GPOLocalGroup,Session,Trusts,ACL,Container,ObjectProps,SPNTargets,CertServices --excludedcs
```
- MDI alerts
![](imgachments/Pasted%20image%2020260417161913.png)

![](imgachments/Pasted%20image%2020260421161950.png)

![](imgachments/Pasted%20image%2020260421162024.png)

## ADExplorer
- ADExplorer from MS is a better alternative for LDAP Recon
- It is MS signed tool for AD viewing and editing: [https://learn.microsoft.com/en-us/sysinternals/downloads/](https://learn.microsoft.com/en-us/sysinternals/downloads/adexplorer)[adexplorer](https://learn.microsoft.com/en-us/sysinternals/downloads/adexplorer)
- A user can take a snapshot of the AD to process it offline
- The snapshot can be then converted into BloodHound JSON files: [https://github.com/c3c/](https://github.com/c3c/ADExplorerSnapshot)[ADExplorerSnapshot](https://github.com/c3c/ADExplorerSnapshot)
Drawbacks:
- It might fail in large domains when dealing with poor connectivity.
- when Active Directory Federation Services (ADFS) is deployed, creating a snapshot with ADExplorer can trigger an alert because it reads the ADFS LDAP container
![](imgachments/Pasted%20image%2020260421164605.png)

![](imgachments/Pasted%20image%2020260421164615.png)

![](imgachments/Pasted%20image%2020260421164621.png)

- To be stealthier and avoid MDI detection, prefer ADWS over LDAP when possible !!!!!!
# Opsec BloodHound - ADWS
## SoapHound
Use [SOAPHound](https://github.com/FalconForceTeam/SOAPHound) for more stealth.
	- It talks to Active Driectory Web Services (ADWS - Port 9389) in place of sending LDAP queries - just like the AD Module.
	- Almost no network-based detection (like MDI).
	- It retrieves information about all objects (objectGuid=\*) and then process them. 
	- It means limited LDAP queries - less chance of endpoint detection.

![](imgachments/SoapHoundDoc.png)

```bash
# Build a cache that includes basic info about domain objects.
SOAPHound.exe --buildcache -c c:\users\vagrant\desktop\cache.txt
# Collect BloodHound compatible data
SOAPHound.exe -c c:\users\vagrant\desktop\cache.txt --bhdump -o c:\users\vagrant\desktop\bloodhound-output --nolaps
```

![](imgachments/SoaPHoundAction.png)
- MDI detected Soaphound due to the ldap filter (!soaphound=\*) 
![](imgachments/Pasted%20image%2020260417134217.png)

![](imgachments/Pasted%20image%2020260421170602.png)
- The source code
![](imgachments/Pasted%20image%2020260417145354.png)
- After modifying (!soaphound=\*) in the source code and recompiling, soaphound bypassed MDI detections

![](imgachments/Pasted%20image%2020260417145713.png)

![](imgachments/Pasted%20image%2020260421171341.png)

Drawbacks:
- Another binary that we need to introduce to monitored endpoints
- It might fail when used against very large domains.
## ShadowHound-ADM
ShadowHound-ADM is a PS script that uses AD Module over ADWS
- [https://github.com/Friends-Security/ShadowHound/blob/main/ShadowHound-ADM.](https://github.com/Friends-Security/ShadowHound/blob/main/ShadowHound-ADM.ps1)[ps1](https://github.com/Friends-Security/ShadowHound/blob/main/ShadowHound-ADM.ps1)
- A set of PowerShell scripts for Active Directory enumeration without the need for introducing known-malicious binaries like SharpHound.
- It leverages native PowerShell capabilities to minimize detection risks
- It uses the AD Module over Active Driectory Web Services (ADWS - Port 9389) instead of sending LDAP queries.
![](imgachments/Pasted%20image%2020260421175443.png)
```bash
# AD Recon
Import-Module .\ShadowHound-ADM.ps1
ShadowHound-ADM -OutputFilePath "C:\users\consultant\documents\mhd\ldap_output.txt" -SplitSearch -LetterSplitSearch -Recurse

# ADCS Recon
ShadowHound-ADM -OutputFilePath "C:\users\consultant\documents\mhd\cert_output.txt" -Certificates
```
- MDI detected it due to some ldap filters
![](imgachments/Pasted%20image%2020260420101505.png)
- For AD Recon, MDI detected
![](imgachments/Pasted%20image%2020260420111459.png)
![](imgachments/Pasted%20image%2020260421180249.png)
- For ADCS Recon, MDI detected
![](imgachments/Pasted%20image%2020260421180720.png)
![](imgachments/Pasted%20image%2020260421180754.png)
![](imgachments/Pasted%20image%2020260421181527.png)

- After modifying these filters in the code, ShadowHound-ADM bypassed MDI detections
![](imgachments/Pasted%20image%2020260420111907.png)

![](imgachments/Pasted%20image%2020260420132551.png)

![](imgachments/Pasted%20image%2020260420113302.png)
![](imgachments/Pasted%20image%2020260420113345.png)

![](imgachments/Pasted%20image%2020260420113541.png)


- Use bofhound to convert the outputs into BloodHound JSON files
```bash
# venv
python -m venv .venv  
source .venv/bin/activate
pip3 install bofhound
bofhound -i ~/workspace/ldap_output.txt -p All --parser ldapsearch 
bofhound -i ~/workspace/certs_output.txt -p All --parser ldapsearch
```

![](imgachments/Pasted%20image%2020260422103701.png)

![](imgachments/Pasted%20image%2020260422110128.png)

