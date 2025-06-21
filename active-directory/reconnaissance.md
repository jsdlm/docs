# Reconnaissance

## Sans authentification

### Scan réseau&#x20;

```bash
nmap -Pn -sS -n -T4 192.168.56.0/24
```

### NetExec

```bash
# Scan réseau global avec SMB
nxc smb 192.168.56.0/24

# Lister des users
nxc smb 192.168.56.10-23 --users
nxc smb 192.168.56.10-23 -u 'a' -p '' --users

# Lister les shares
nxc smb 192.168.56.10-23 --shares
nxc smb 192.168.56.10-23 -u 'a' -p '' --shares
```

### Identifier une liste de users possible (Kerberos)

```bash
sudo nmap -p 88 --script=krb5-enum-users --script-args="krb5-enum-users.realm='sevenkingdoms.local',userdb=possible_usernames.txt" 192.168.56.10
```

## Avec authentification

### NetExec

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

### Export Bloodhound avec NetExec

```bash
nxc ldap 192.168.56.11 -u 'brandon.stark' -p 'iseedeadpeople' -d 'north.sevenkingdoms.local' --bloodhound -c all
nxc ldap 192.168.56.11 -u 'brandon.stark' -p 'iseedeadpeople' -d 'north.sevenkingdoms.local' --bloodhound -c all --dns-server 192.168.56.11
```
