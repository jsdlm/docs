# UFW

# Tutoriel UFW (Uncomplicated Firewall)

## 1. Installation d'ufw

```bash
sudo apt update
sudo apt install ufw
```

***

## 2. Activer/Désactiver ufw

### Activer le pare-feu :

```bash
sudo ufw enable
```

Cela active **ufw** et applique les règles définies. Toutes les connexions entrantes seront **bloquées** par défaut sauf celles autorisées.

### Désactiver le pare-feu :

```bash
sudo ufw disable
```

Cela désactive **ufw** et supprime ses règles du système.

***

## 3. Vérification du statut d'ufw

Pour vérifier si **ufw** est activé et afficher les règles en cours :

```bash
sudo ufw status
```

Pour afficher les règles détaillées avec les numéros de ligne :

```bash
sudo ufw status numbered
```

***

## 4. Configurer les règles

### a. **Règles de base**

Les commandes suivantes permettent d'autoriser ou de bloquer des connexions :

*   Autoriser un port spécifique (ex. SSH, port 22) :

    ```bash
    sudo ufw allow 22
    ```
*   Autoriser un port spécifique en précisant le protocole (TCP ou UDP) :

    ```bash
    sudo ufw allow 80/tcp  # HTTP (TCP)
    sudo ufw allow 53/udp  # DNS (UDP)
    ```
*   Bloquer un port spécifique :

    ```bash
    sudo ufw deny 25
    ```
*   Autoriser une plage de ports (ex. 1000 à 2000) :

    ```bash
    sudo ufw allow 1000:2000/tcp
    ```
*   Bloquer une plage de ports :

    ```bash
    sudo ufw deny 3000:4000/udp
    ```

### b. **Règles par adresse IP**

*   Autoriser une adresse IP spécifique à se connecter à tous les ports :

    ```bash
    sudo ufw allow from 192.168.1.100
    ```
*   Autoriser une adresse IP à un port spécifique :

    ```bash
    sudo ufw allow from 192.168.1.100 to any port 22
    ```
*   Bloquer une adresse IP spécifique :

    ```bash
    sudo ufw deny from 192.168.1.200
    ```

### c. **Règles par réseau**

*   Autoriser un sous-réseau entier (ex. 192.168.1.0/24) :

    ```bash
    sudo ufw allow from 192.168.1.0/24
    ```

***

## 5. Supprimer une règle

Pour supprimer une règle, vous devez connaître son numéro de ligne (voir `ufw status numbered`).

*   Supprimer une règle en utilisant son numéro :

    ```bash
    sudo ufw delete [NUMERO]
    ```

Exemple :

```bash
sudo ufw delete 1
```

***

## 6. Règles par défaut

Vous pouvez définir le comportement par défaut pour les connexions entrantes et sortantes :

*   Bloquer toutes les connexions entrantes par défaut :

    ```bash
    sudo ufw default deny incoming
    ```
*   Autoriser toutes les connexions sortantes par défaut :

    ```bash
    sudo ufw default allow outgoing
    ```
*   Bloquer les connexions sortantes par défaut (si nécessaire) :

    ```bash
    sudo ufw default deny outgoing
    ```

***

## 7. Autoriser des services par leur nom

**ufw** intègre des profils pour les services courants. Vous pouvez les lister avec :

```bash
sudo ufw app list
```

Exemple :

```bash
Available applications:
  OpenSSH
  Apache
  Nginx Full
  Nginx HTTP
  Nginx HTTPS
```

Pour autoriser un service comme SSH ou Nginx :

```bash
sudo ufw allow OpenSSH
sudo ufw allow "Nginx Full"
```

***

## 8. Logs d'ufw

Pour activer les logs d'ufw (utile pour le dépannage ou la vérification des connexions) :

```bash
sudo ufw logging on
```

Les logs seront enregistrés dans le fichier :

```
/var/log/ufw.log
```

***

## 9. Réinitialiser la configuration d'ufw

Si vous voulez repartir de zéro :

```bash
sudo ufw reset
```

Cela désactive **ufw** et supprime toutes les règles existantes.

***

## 10. Exemples de configuration

*   Autoriser SSH, HTTP et HTTPS :

    ```bash
    sudo ufw allow 22
    sudo ufw allow 80
    sudo ufw allow 443
    ```
*   Bloquer toutes les connexions sauf SSH :

    ```bash
    sudo ufw default deny incoming
    sudo ufw allow 22
    sudo ufw enable
    ```
*   Autoriser un sous-réseau (192.168.1.0/24) à accéder à un port spécifique (3306 pour MySQL) :

    ```bash
    sudo ufw allow from 192.168.1.0/24 to any port 3306
    ```
