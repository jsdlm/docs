# Reconnaissance

> L'objectif est d'identifier :&#x20;
>
> * La ou les plages réseaux
> * Les protocoles et services utilisés
> * Les domaines / forêts
> * Les principaux serveurs et DC

## Reconnaissance passive

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

## Reconaissance active

### Nmap

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

### NetExec

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

### Find DC ip

```bash
nslookup -type=srv _ldap._tcp.dc._msdcs.sevenkingdoms.local 192.168.56.10
```
