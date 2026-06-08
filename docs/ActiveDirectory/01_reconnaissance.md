# Reconnaissance

> L'objectif est d'identifier :
>
> * La ou les plages réseaux
> * Les protocoles et services utilisés
> * Les domaines / forêts
> * Les principaux serveurs et DC

# Reconnaissance passive

Informations sur le réseau

```bash
ip a
ip route
route -n
```

Faire un Wireshark ou tcpdump pour identifier les différents réseaux / adresses IP et protocoles utilisés

```bash
tcpdump -i eth0 -n -vvv -A not port 22 and not port 53
```

Quelques protocoles intéressants

* Traffic ARP : Trouver des adresses IP valides
* Bails DHCP/DHCPv6 : Trouver les serveurs DNS/configuraon réseau
* Mulcast LLMNR : Découvrir des noms d'hôtes/adresses IP valides
* Mulcast mDNS : Découvrir des noms d'hôtes/adresses IP valides
* Broadcast NBNS : Découvrir des noms d'hôtes/adresses IP valides

# Reconaissance active

## Nmap

```bash
nmap -Pn -sS -n -T4 192.168.56.0/24

nmap --flags <host>

# Options :
# -Pn : Pour ne pas faire les checks ping
# -sV : detecte les services et versions
# -sS : scan furtif (SYN)
# -A : scan agressif avec détection d'OS et de versions
# -T4 : scan rapide
# --script vuln : utilisation des scripts nmap
# -sC: Performs a script scan using the default set of scripts - equivalent to --script=default.
```

**Network sweep + output grepable**

```bash
# Ping sweep -  lister les hôtes actifs, sortie grepable
nmap -v -sn 192.168.50.1-253 -oG ping-sweep.txt

# SYN scan sur tout un subnet, sortie grepable
nmap -sS 192.168.151.0/24 -oG grp1.txt

# Extraire les IPs avec ports ouverts depuis la sortie grepable
grep open grp1.txt | cut -d" " -f2

# Scanner uniquement HTTP/HTTPS et récupérer les titres des pages
nmap -sS 192.168.151.0/24 -p 80,443 --script http-title -oG grp1-http.txt
```

## NetExec

```bash
nxc smb 192.168.56.0/24
```

Générer un fichier de liste d'adresses IP valides

```bash
nxc smb 192.168.56.0/24 | head -n -1 | awk '{print $2}' > ip.txt
```

Générer un fichier hosts

```bash
nxc smb ip.txt --generate-hosts-file /tmp/hosts
```

## Find DC ip

```bash
nslookup -type=srv _ldap._tcp.dc._msdcs.sevenkingdoms.local 192.168.56.10
```

## Autres scanners

```bash
# Port scan TCP avec netcat -  utile quand nmap n'est pas dispo
nc -nvz -w 1 192.168.50.151 1-1024

# SNMP scan -  découverte d'équipements réseau exposant SNMP (community string par défaut : public)
onesixtyone -c community 192.168.127.0/24
```

```powershell
# Port scan PowerShell -  sans nmap sur Windows
1..1024 | % {echo ((New-Object Net.Sockets.TcpClient).Connect("192.168.151.151", $_)) "TCP port $_ is open"} 2>$null
```
