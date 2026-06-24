# Setup

```bash
# Mettre en azerty de manière permanente sur XFCE:
sudo dpkg-reconfigure keyboard-configuration
sudo systemctl restart keyboard-setup
sudo reboot

# Ajouter un utilisateur pentester en sudoer
sudo adduser pentester
sudo usermod -aG sudo pentester

# Monter le dossier partagé VMWare 'share' dans /mnt:
sudo /usr/bin/vmhgfs-fuse .host:/_share /mnt/_share -o subtype=vmhgfs-fuse,allow_other

# Network reset
sudo ip neigh flush all        # ARP
sudo ip route flush cache      # routes
```

# zsh corrupt history

```bash
zsh: corrupt history file /home/kali/.zsh_history

cd ~
mv .zsh_history .zsh_history.bak
strings .zsh_history.bak > .zsh_history
```

# Misc

```bash
# Backgroung
# Ctrl + Z
jobs
fg %<numéro_job>

# Neo4j
neo4j://127.0.0.1:7687
neo4j:neo4j
:server change-password
neo4j:kali
update /etc/bhapi/bhapi.json with the new password before running bloodhound

# Nessus
/etc/init.d/nessusd 
Usage: /etc/init.d/nessusd {start|stop|restart|status}
https://127.0.0.1:8834/#/

# BURP BROWSER
cd ~/.BurpSuite/burpbrowser
cd 127.0.6533.99
sudo chown -R root:root chrome-sandbox
sudo chmod 4755 chrome-sandbox
```

