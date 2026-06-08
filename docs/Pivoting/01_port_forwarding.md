# Port Forwarding

# Linux

## Socat

**Port forward simple -  rediriger un port local vers une cible distante**

```bash
socat -ddd TCP-LISTEN:<port_local>,fork TCP:<ip_cible>:<port_cible>
```

![](img/Pasted%20image%2020260509180627.png)

Exemple : écouter sur le port 2345 et forwarder vers PostgreSQL sur une machine interne :

```bash
socat -ddd TCP-LISTEN:2345,fork TCP:10.4.50.215:5432
```

Exemple : écouter sur le port 2222 et forwarder vers SSH sur une machine interne :

```bash
socat -ddd TCP-LISTEN:2222,fork TCP:10.4.50.215:22
```

**Se connecter à travers le port forward**

```bash
# PostgreSQL
psql -h <ip_pivot> -p 2345 -U postgres

# SSH
ssh <user>@<ip_pivot> -p 2222
```

## Alternatives

- **rinetd** : daemon, mieux adapté aux forwards long terme
- **Netcat + FIFO** : `mkfifo /tmp/f; nc -l -p <port> < /tmp/f | nc <cible> <port> > /tmp/f`
- **iptables** (root requis) : forward permanent via règles kernel, nécessite aussi `echo 1 > /proc/sys/net/ipv4/conf/<interface>/forwarding`
