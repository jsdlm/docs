# 1. Identifier le système cible

```
cat /etc/debian_version        # version Debian
dpkg --print-architecture      # architecture (ex. amd64)
```

Note : Kali rolling suit Debian Testing, prendre la branche `sid`.

# 2. Récupérer le .deb

## Depuis une machine en ligne

```
sudo apt-get install --download-only <paquet>
```

Les .deb (paquet + dépendances) sont dans `/var/cache/apt/archives/`.

## Depuis packages.debian.org

1. Va sur `https://packages.debian.org/<paquet>` (ex. `https://packages.debian.org/flameshot`)
2. Clique sur ta version/branche de Debian (ex. **sid** pour Kali, ou **bookworm** pour Debian 12).
3. En bas de page, section **Download**, clique sur ton architecture (ex. **amd64**).
4. Choisis un miroir pour télécharger le `.deb`.

Lien direct : `https://packages.debian.org/<branche>/<architecture>/<paquet>/download`  
Exemple : `https://packages.debian.org/sid/amd64/flameshot/download`

Note : télécharger manuellement chaque dépendance une par une est fastidieux. La méthode `apt-get install --download-only` récupère le paquet et ses dépendances d'un coup.
# 3. Installer

Transférer les .deb vers la machine cible.
Installer le .deb
```
sudo dpkg -i /chemin/*.deb
```