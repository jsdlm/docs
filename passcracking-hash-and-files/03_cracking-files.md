# Cracking files

> [Offensive Security Cheatsheet](https://cheatsheet.haax.fr/passcracking-hashfiles/cracking_files/)

## Cracking archives <a href="#cracking-archives" id="cracking-archives"></a>

```bash
# RAR
rar2john file.rar > rar_hashes.txt
john --wordlist=passwords.txt rar_hashes.txt

# ZIP
zip2john file.rar > zip_hashes.txt
john --wordlist=passwords.txt zip_hashes.txt

# ZIP Using fcrackzip
fcrackzip -u -D -p rockyou.txt recup.zip
```

## Cracking shadow files <a href="#cracking-shadow-files" id="cracking-shadow-files"></a>

```bash
unshadow passwd shadow > shadowjohn.txt
john --wordlist=/home/user/Desktop/Certifs/OSCP/Tools/Wordlist/Bruteforce/rockyou.txt --rules shadowjohn.txt
john --show shadowjohn.txt

# Hashcat SHA512 $6$ shadow file  
hashcat -m 1800 -a 0 hash.txt rockyou.txt --username

#Hashcat MD5 $1$ shadow file  
hashcat -m 500 -a 0 hash.txt rockyou.txt --username
```

## Various cracking techniques <a href="#various-cracking-techniques" id="various-cracking-techniques"></a>

```bash
# Hashcat MD5 Apache webdav file  
hashcat -m 1600 -a 0 hash.txt rockyou.txt

# Hashcat SHA1  
hashcat -m 100 -a 0 hash.txt rockyou.txt --force

# Hashcat Wordpress  
hashcat -m 400 -a 0 --remove hash.txt rockyou.txt

# SSH Key
ssh2john id_rsa  > sshtocrack
john --wordlist=/usr/share/wordlists/rockyou.txt sshtocrack

# Cracking Cisco passwords
# Type 5 → MD5
# Type 7 → Easy reversible
hashcat -m 500 c:\temp\ciscohash.txt C:\DICS\english-dic.txt

# Cracking NTLVMv2 hashes
john --format=netntlmv2 --wordlist="/usr/share/wordlists/rockyou.txt" hash.txt 
```

## Cracking TGS <a href="#cracking-tgs" id="cracking-tgs"></a>

```bash
# Using John from bleeding repo:

Go here /home/user/Desktop/Certifs/OSCP/Tools/PasswordCracking/JohnTheRipper/run
./john --wordlist=/home/user/Desktop/Certifs/OSCP/Tools/Wordlist/Bruteforce/rockyou.txt --fork=4 --format=krb5tgs /home/user/Desktop/HackTheBox/VM/Active/kerberos_hashes.txt
```
