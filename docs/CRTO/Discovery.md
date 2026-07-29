```
ldapsearch (|(objectClass=domain)(objectClass=organizationalUnit)(objectClass=groupPolicyContainer)) --attributes *,ntsecuritydescriptor

ldapsearch (|(samAccountType=805306368)(samAccountType=805306369)(samAccountType=268435456)) --attributes *,ntsecuritydescriptor
```

```
scp -r attacker@10.0.0.5:/opt/cobaltstrike/logs .
bofhound -i logs/
ls -l

-rwxrwxrwx 1 attacker attacker 16072 Mar 12 12:06 computers_20250312_120659.json
-rwxrwxrwx 1 attacker attacker  1803 Mar 12 12:06 domains_20250312_120659.json
-rwxrwxrwx 1 attacker attacker 13792 Mar 12 12:06 gpos_20250312_120659.json
-rwxrwxrwx 1 attacker attacker 34772 Mar 12 12:06 groups_20250312_120659.json
drwxrwxrwx 1 attacker attacker  4096 Mar 12 12:06 logs
-rwxrwxrwx 1 attacker attacker  5690 Mar 12 12:06 ous_20250312_120659.json
-rwxrwxrwx 1 attacker attacker 21889 Mar 12 12:06 users_20250312_120659.json
```

Every object that is only represented by a SID, or 'no name or id' means that we haven't collected any data on it yet :
```
ldapsearch (objectsid=[SID]) --attributes *,ntsecuritydescriptor
```
