# 1. Reconnaissance

- [ ] Cartographier le réseau : plages IP, VLAN accessibles, hosts up → [Reconnaissance](Reconnaissance.md)
- [ ] Scanner les services exposés et identifier les DC, les serveurs applicatifs (SQL, web, print...) → [Reconnaissance](Reconnaissance.md)
- [ ] Zone DNS : tenter un transfert de zone → [DNS](DNS.md)

# 2. Black box (exceptionnel) — énumération anonyme

- [ ] Null session SMB (partages, users, policy de mdp) → [Enumération LDAP](Enumération%20LDAP.md)
- [ ] Bind LDAP anonyme (users, groupes, description...) → [Enumération LDAP](Enumération%20LDAP.md)
- [ ] Null session RPC (rpcclient) → [Enumération LDAP](Enumération%20LDAP.md)
- [ ] Shares accessibles sans auth (SYSVOL/NETLOGON) : scripts de login, GPP cpassword (Groups.xml), unattend.xml → [Enumération LDAP](Enumération%20LDAP.md)

# 3. Quick Wins

- [ ] Collecte complète LDAP + BloodHound/SharpHound → [Enumération LDAP](Enumération%20LDAP.md) / [ACL](ACL.md)
- [ ] Descriptions LDAP
- [ ] Explorer les Shares -> [Shares](Shares.md)
- [ ] Sniffer/empoisonner LLMNR, NBNS, mDNS pour capturer des hash NetNTLM (Responder) → [Poison and Relay](Poison%20and%20Relay.md)
- [ ] NTLMv1 autorisé (downgrade LM/NTLMv1) : hash trivialement crackable/relayable → [NTLM](NTLM.md), [Poison and Relay](Poison%20and%20Relay.md)
- [ ] SMB signing désactivé → [Poison and Relay](Poison%20and%20Relay.md) / [Coerce](Coerce.md)
- [ ] mitm6 si IPv6 activé par défaut (quasi toujours) : usurper le DNS IPv6, forcer les machines à s'authentifier → relayer → [Poison and Relay](Poison%20and%20Relay.md)
- [ ] [ADCS](ADCS.md)
- [ ] AS-REP Roasting / Kerberoasting → [Kerberos](Kerberos.md)
- [ ] [Password Spraying](Password%20Spraying.md)
- [ ] [GPO](GPO.md)
- [ ] [Délégations Kerberos](Délégations%20Kerberos.md)
- [ ] [[MSSQL]]