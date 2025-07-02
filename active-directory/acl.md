# ACL





```bash
# share enum with user
nxc smb 192.168.56.10-23 -u 'jon.snow' -p 'iknownothing' --shares

# Get DC ip
nxc ldap 192.168.56.11 -u 'brandon.stark' -p 'iseedeadpeople' --dc-list

# Get all users from all DCs
nxc ldap 192.168.56.10-23 -u 'brandon.stark' -p 'iseedeadpeople' -d 'north.sevenkingdoms.local' --users

# Export users to file for each DCs
nxc ldap 192.168.56.10 -u 'brandon.stark' -p 'iseedeadpeople' -d 'north.sevenkingdoms.local' --users-export KINGSLANDING.txt
nxc ldap 192.168.56.11 -u 'brandon.stark' -p 'iseedeadpeople' -d 'north.sevenkingdoms.local' --users-export WINTERFELL.txt
nxc ldap 192.168.56.12 -u 'brandon.stark' -p 'iseedeadpeople' -d 'north.sevenkingdoms.local' --users-export MEEREEN.txt
```

### Bloodhound

Avec NetExec (Risque de bug avec BloodHound Community Edition (CE))\
Le problème vient du fichier domains.json qui semble être malformée pour la version CE (Ok pour la version Legacy?)

```bash
nxc ldap 192.168.56.11 -u 'brandon.stark' -p 'iseedeadpeople' -d 'north.sevenkingdoms.local' --bloodhound -c all
nxc ldap 192.168.56.11 -u 'brandon.stark' -p 'iseedeadpeople' -d 'north.sevenkingdoms.local' --bloodhound -c all --dns-server 192.168.56.11
```

Avec l'ingestor de BloodHound Community Edition (CE)\
[https://github.com/dirkjanm/BloodHound.py](https://github.com/dirkjanm/BloodHound.py)

```bash
pipx install bloodhound-ce
bloodhound-ce-python --zip -c All -d north.sevenkingdoms.local -u brandon.stark -p iseedeadpeople -dc winterfell.north.sevenkingdoms.local -ns 192.168.56.11
```
