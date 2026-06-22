# Conclusion
Microsoft Defender for Identity
- "..identify, detect, and investigate advanced threats, compromised identities, and malicious insider actions directed at an organization."
- MDI sensors are installed on DCs and Federation servers ==> avoid talking to the DC as long as possible & emulate genuine legitimate Kerberos requests
- Analysis and alerting is done in the Azure cloud.
- MDI can be used for detecting:
	- Recon ==> avoid noisy bloodHound collection methods like RDP, DCOM, PSRemote and LocalAdmin or better use SOAPHound or ShadowHound over ADWS
	- Compromised credentials (Kerberoasting ==> avoid kerberos eType encryption downgrade and specific kerberoasting LDAP recon, etc.)
	- Lateral movement (PTH ==> use AskTGT & AskTGS, OPTH ==> emulate genuine AS-Req & TGS-Req \[fields & sequences], etc.) 
- Domain Dominance (DCSync ==> using DC account or MSOL_ , Golden ticket ==> emulate genuine PAC or better use Diamond ticket, etc.)