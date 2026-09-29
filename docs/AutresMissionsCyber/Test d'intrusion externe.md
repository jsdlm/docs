# Nmap

```bash
nmap --flags <host>

# Options :
# -Pn : Pour ne pas faire les checks ping
# -sV : detecte les services et versions
# -sS : scan furtif (SYN)
# -A : scan agressif avec détection d'OS et de versions
# -T4 : scan rapide
# -n :Never do DNS resolution
# --script vuln : utilisation des scripts nmap
# -sC : effectue un scan de scripts avec le set par défaut - équivalent à --script=default.
```

## Scan de port (TCP)

```bash
nmap -T4 -Pn --open -p- -oA nmap_full -iL ip.txt

ports=$(grep -oP '\d+/open[^/]*/tcp' nmap_full.gnmap | cut -d'/' -f1 | sort -u | tr '\n' ',' | sed 's/,$//')

nmap -T4 -Pn -sC -sV --open -p $ports -oN nmap_full_detailed.txt -iL ip.txt
```
## Scan de port (UDP)
```bash
nmap -T4 -Pn -sU --open --top-port=20 -oA nmap_udp -iL ip.txt

ports=$(grep -oP '\d+/open[^/]*/udp' nmap_udp.gnmap | cut -d'/' -f1 | sort -u | tr '\n' ',' | sed 's/,$//')

nmap -T4 -Pn -sU -sC -sV --open -p $ports -oN nmap_udp_detailed.txt -iL ip.txt
```

**Liste d'adresse IP**
```bash
grep open nmap_full_G.txt | cut -d" " -f2
```

## NSE

```bash
# Scripts
# https://www.it-connect.fr/chapitres/nmap-utilisation-des-scripts-nse/

# Lister tous les scripts dont le nom commence par “ftp-”
nmap --script-help=ftp-*

# Lister tous les scripts de la catégorie “discovery”
nmap --script-help=discovery

# Lister les scripts ciblant le service “ssh”
ls -al /usr/share/nmap/scripts/ssh*

# Lister les scripts de la catérogie “dos”
grep -rl 'dos' /usr/share/nmap/scripts/

# Scripts http
nmap -p80 --script='http-enum' <host>

# Detect WAF - https://nmap.org/nsedoc/scripts/http-waf-detect.html
nmap -p80 --script http-waf-detect <host>
nmap -p80 --script http-waf-detect --script-args="http-waf-detect.aggro,http-waf-detect.uri=/testphp.vulnweb.com/artists.php" www.modsecurity.org
```

# FTP (21)

```shell
# Version et exploits
searchsploit ftp <version>
```

**Upload**
```bash
ftp <IP>
# login anonyme
Username: anonymous
Password: (vide/anonymous)

passive      # désactiver le mode passif si besoin
binary       # obligatoire pour les exécutables
put file.exe
```

**Download folder**
```bash
ftp <IP>
cd folder
mget *

wget -r ftp://anonymous:anonymous@192.168.189.157/backup/
wget -m ftp://anonymous:anonymous@$target
```

Chercher :
- Fichiers avec indices (ex: `minniemouse.exe`)
- Uploads qui vont vers un répertoire web ?

# SSH (22)

```shell
nmap -p 22 -sV --script=ssh2-enum-algos,ssh-hostkey $target
# Bannière, version OS, indices de réutilisation de clé faible
# Ignorer jusqu'à avoir des credentials
```

# Telnet (23)

```shell
nmap -p 23 --script=telnet-brute,telnet-ntlm-info $target
telnet $target 23
```

# SMTP (25)

```shell
nc -nv $target 25
telnet $target 25

# VRFY pour vérifier si un user existe
VRFY root
VRFY admin

# Nmap enum users
nmap -p 25 --script smtp-enum-users --script-args smtp-enum-users.methods={VRFY,EXPN} $target
```

# SMB (139/445)

```shell
# Null session et liste des shares
smbclient -L //$target -N
nxc smb $target -u '' -p '' --shares

# Accéder à un share
smbclient //$target/share -N

# Enum complet
enum4linux-ng $target

# OS discovery
nmap -v -p 139,445 --script smb-os-discovery $target

# RPC
rpcclient -U "" -N $target
# Dans rpcclient :
# enumdomusers
# srvinfo
# querydispinfo

# Nmap null session
nxc smb $target -u '' -p '' --shares

smbclient -L //$target -N               # Lister les shares
smbclient //$target/share -N -c 'mget *' # Download tout
nxc smb $target -u '' -p '' --shares    # Null session
```

# SNMP (161)

```shell
# Brute-force community strings
sudo nmap -sU -p 161 --script snmp-brute $target

# Nmap complet
nmap -sU -p 161 --script=snmp-info,snmp-interfaces,snmp-processes $target
```

https://hacktricks.wiki/en/network-services-pentesting/pentesting-snmp/index.html

```bash
echo public > community
echo private >> community
echo manager >> community
onesixtyone -c community -i ip.txt

hydra -P /usr/share/wordlists/seclists/Discovery/SNMP/common-snmp-community-strings.txt snmp://192.168.162.149

snmpwalk -c public -v1 192.168.243.149 .1 > snmp.txt

snmpwalk -c public -v1 -t 10 192.168.50.151

snmpwalk -c public -v1 192.168.50.151 1.3.6.1.4.1.77.1.2.25

snmpwalk -v2c -c public $target | grep <string>
```

**OIDs Windows**
```
1.3.6.1.2.1.25.4.2.1.2       # processus
1.3.6.1.2.1.25.4.2.1.5       # arguments des processus
1.3.6.1.2.1.25.6.3.1.2       # logiciels installés
1.3.6.1.2.1.25.1.6.0         # nombre de processus
1.3.6.1.4.1.77.1.2.25        # utilisateurs locaux
1.3.6.1.4.1.77.1.2.3.1.1     # services en cours
1.3.6.1.4.1.77.1.2.27        # partages réseau
1.3.6.1.2.1.6.13.1.3         # ports TCP ouverts
1.3.6.1.2.1.25.2.3.1.4       # taille des unités de stockage
1.3.6.1.2.1.25.2.3.1.3       # nom des mountpoints/disques
1.3.6.1.2.1.1.5.0             # hostname
1.3.6.1.2.1.1.1.0             # sysDescr (OS, version)
1.3.6.1.2.1.4.34.1            # adresses IP
```

**OIDs Linux**
```
1.3.6.1.2.1.1.1.0             # sysDescr (OS, version)
1.3.6.1.2.1.1.5.0             # hostname
1.3.6.1.2.1.25.4.2.1.2       # processus
1.3.6.1.2.1.25.4.2.1.5       # arguments des processus
1.3.6.1.2.1.25.6.3.1.2       # logiciels installés
1.3.6.1.2.1.25.2.3.1.3       # mountpoints/disques
1.3.6.1.2.1.6.13.1.3         # ports TCP ouverts
1.3.6.1.2.1.4.34.1            # adresses IP
1.3.6.1.2.1.4.22.1.2         # table ARP
1.3.6.1.2.1.17.4.3.1.2       # table MAC (bridge)
1.3.6.1.4.1.8072.1.3.2       # nsExtendObjects (scripts custom)
```

# MSSQL (1433)
[MSSQL](../Database/MSSQL.md)

# RDP (3389)

```shell
nmap -p 3389 --script=rdp-enum-encryption $target
# Check encryption → indice sur la version Windows

xfreerdp3 /u:user /p:password /v:$target /cert-ignore
xfreerdp3 /cert-ignore /u:user /p:password /v:$target /drive:/var/www/html
nxc rdp $target -u users.txt -p 'Password123'  # Spray
```

# Ports inconnus

```bash
nc -nv <IP> <PORT>
telnet <IP> <PORT>
help
```
