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
ss -ntplu
ss -anp
ss -tln
netstat -taupen
```

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
