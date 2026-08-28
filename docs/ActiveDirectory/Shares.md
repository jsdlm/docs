
# Automatique
https://github.com/SnaffCon/Snaffler
https://github.com/zh54321/SnafflerParser
https://github.com/jsdlm/scripts

```bash
wget https://github.com/SnaffCon/Snaffler/releases/download/1.0.244/Snaffler.exe
.\Snaffler.exe -o snafflerout.txt -s -y
.\Snaffler.exe -o snafflerout.txt -s -y -i C:\
.\snafflerparser.ps1 -in snafflerout.txt
```

- Snaffler-ng
https://github.com/totekuh/snaffler-ng

```bash
pipx install snaffler-ng

nxc smb 10.0.0.0/24 -u user -p pass --shares | snaffler -u user -p pass --stdin

snaffler -u USER -p PASS --computer 10.0.0.5 --computer 10.0.0.6
snaffler -u USER -p PASS --computer 10.0.0.0/24
snaffler -u USER -p PASS --computer-file targets.txt

snaffler -u USER -p PASS -d DOMAIN.LOCAL
snaffler -k --use-kcache -d DOMAIN.LOCAL --dc-host CORP-DC02
```

# Manuel

```powershell
# SYSVOL -  accessible par tous les users du domaine, contient scripts et GPO
ls \\dc1.corp.com\sysvol\corp.com\
ls \\dc1.corp.com\sysvol\corp.com\Policies\
```
