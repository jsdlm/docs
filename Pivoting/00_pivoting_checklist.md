# Pivoting checklist

## Linux

**Interfaces réseau**
```bash
ip a
ifconfig
```

**Table de routage**
```bash
ip route
route -n
routel
```

**Connexions actives et ports en écoute**
```bash
ss -lnpt          # ports en écoute avec process
ss -apn           # toutes les connexions actives avec process

netstat -lnpt     # ports en écoute avec process
netstat -taupen   # toutes les connexions actives avec process et user
```

`ss` 

| Flag | Description |
|------|-------------|
| `-n` | Ne pas résoudre les noms (affiche les IPs et ports numériques) |
| `-t` | Sockets TCP uniquement |
| `-u` | Sockets UDP uniquement |
| `-l` | Sockets en écoute uniquement |
| `-p` | Affiche le process associé |
| `-a` | Toutes les sockets (écoute + établies) |

`netstat` 

| Flag | Description |
|------|-------------|
| `-t` | Connexions TCP |
| `-a` | Toutes les sockets (écoute + établies) |
| `-u` | Connexions UDP |
| `-p` | Affiche le process associé |
| `-e` | Informations étendues (user, inode) |
| `-n` | Ne pas résoudre les noms |

**Résolution DNS et domaine**
```bash
cat /etc/resolv.conf
cat /etc/hosts
hostname -f
```

**ARP - machines connues sur le réseau local**
```bash
arp -a
ip neigh
```

**Capturer le trafic réseau (root requis)**
```bash
tcpdump -i <interface>
tcpdump -i ens192 -w /tmp/capture.pcap     # sauvegarder pour analyse
tcpdump -i any host <ip>                   # filtrer par IP
tcpdump -i any port 445                    # filtrer par port
```

**Scanner un sous-réseau (sans nmap)**
```bash
for i in $(seq 1 254); do nc -zv -w 1 172.16.50.$i 445; done
```

**Règles firewall**
Nécessite root pour `iptables`, mais les fichiers de config sont souvent lisibles :

```bash
cat /etc/iptables/rules.v4
```

## Windows

**Interfaces réseau**
```cmd
ipconfig /all
```

**Table de routage**
```cmd
route print
```

**Connexions actives et ports en écoute**
```cmd
netstat -ano          # toutes les connexions avec PID
netstat -anob         # idem + nom du binaire (admin requis)
```

| Flag | Description |
|------|-------------|
| `-a` | Toutes les connexions et ports en écoute |
| `-n` | Ne pas résoudre les noms |
| `-o` | Affiche le PID associé |
| `-b` | Affiche le binaire associé (admin requis) |

**ARP - machines connues sur le réseau local**
```cmd
arp -a
```

**Résolution DNS**
```cmd
type C:\Windows\System32\drivers\etc\hosts
ipconfig /displaydns
```

**Scanner un sous-réseau (sans nmap)**
```powershell
1..254 | ForEach-Object { $ip = "172.16.50.$_"; if (Test-Connection -Count 1 -Quiet $ip) { $ip } }
```
