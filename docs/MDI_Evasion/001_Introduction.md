# MDI - Microsoft Defender for Identity
https://learn.microsoft.com/en-us/defender-for-identity/what-is
- "..identify, detect, and investigate advanced threats, compromised identities, and malicious insider actions directed at an organization."
- MDI sensors are installed on DCs and Federation servers. 
- Analysis and alerting is done in the Azure cloud.
- MDI can be used for detecting
	- Recon
	- Compromised credentials (Brute-Force, Kerberoasting etc.)
	- Lateral movement (PTH, OPTH etc.)
	- Domain Dominance (DCSync, Golden ticket, Skeleton key etc.)
	- Exfiltration
- MDI evasion techniques tend to avoid talking to the DC as long as possible and make appear the traffic we generate as attacker normal by emulating genuine legitimate kerberos requests.

![](img/MDIAlerts.png)

![](img/Pasted%20image%2020260423104305.png)

# Kerberos requests – AS-REQ
![](img/ASREQ.png)
# Kerberos requests – TGS-REQ
![](img/TGSREQ.png)
