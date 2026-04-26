# Reconnaissance

## Techniques

* Analyse des headers (faiblesses + technical information disclosure)
* Recherche des fichiers sensibles (robots.txt, sitemap.xml, etc.)
* Directory fuzzing (gobuster, fuzz, etc.)
* Recherche de vulnérabilités (nikto, exploit-db, etc.)
* Test manuel des injections (SQLi, XSS, XXE, etc.)

## Nmap

### Basics

```bash
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


### NSE

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

## Scans http

```bash
# Techno detection
whatweb [options] <URLs>

# Nikto
nikto -host {Web_Proto}://{IP}:{Web_Port}

# Nuclei
go install -v github.com/projectdiscovery/nuclei/v3/cmd/nuclei@latest
export PATH=$PATH:/home/pentester/go/bin
nuclei -ut
nuclei -u <URL>

# Headers
curl -I http://target.com
```

## Scan SSL

```bash
sslscan target.com
testssl target.com
sslyse target.com
```

## Dir Fuzzing

```bash
gobuster dir -u http://target.com -w /path/to/wordlist.txt -f
gobuster dir -u <url> -w /usr/share/wordlists/dirb/<wordlistsouhaité> -f

ffuf -u http://target.com/FUZZ -w /path/to/wordlist.txt
ffuf -u <url> -w /usr/share/seclists/Discovery/Web-Content/common.txt -r -t 7 -rate 70 -H “User-Agent:
```

## Recherche de vulnérabilités

```
https://www.exploit-db.com/
searchsploit
searchsploit -m <EDB-ID>
```

## Plugins browsers

* Wappalyzer
* Retire.js
* Whatruns
* PwnFox
