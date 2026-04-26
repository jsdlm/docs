# DNS

## Résolution basique

```bash
host www.megacorpone.com
host -t mx megacorpone.com    # serveurs mail
host -t txt megacorpone.com   # enregistrements TXT (SPF, DMARC...)
```

## nslookup

```bash
nslookup mail.megacorptwo.com
nslookup -type=TXT info.megacorptwo.com 192.168.50.151   # interroger un DNS spécifique
```

## Enumération automatisée

```bash
# dnsrecon — énumère les enregistrements, tente le transfert de zone, brute-force sous-domaines
dnsrecon -d megacorpone.com

# dnsenum — similaire, aussi transfert de zone + brute-force
dnsenum megacorpone.com
```
