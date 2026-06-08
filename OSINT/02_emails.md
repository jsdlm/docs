# Emails

# Vérifier une adresse email sans envoyer de mail

> Utiliser [Google Cloud Shell](https://shell.cloud.google.com) pour éviter que votre IP soit blacklistée.

## Étape 1 -  Trouver le serveur MX

```bash
dig MX domaine.fr
host -t MX domaine.fr
nslookup -type=MX domaine.fr
```

Repérer le hostname MX, ex : `mxa-0071d001.gslb.pphosted.com`

## Étape 2 -  Se connecter au serveur MX

```bash
telnet mxa-0071d001.gslb.pphosted.com 25
nc -nv mxa-0071d001.gslb.pphosted.com 25
```

## Étape 3 -  Séquence SMTP

```
VRFY adresse-a-verifier@domaine.fr   ← quasi désactivé sur les serveurs modernes

EHLO test.com
MAIL FROM:test@test.com
RCPT TO:adresse-a-verifier@domaine.fr
QUIT
```

## Réponses possibles

| Réponse                  | Signification                              |
| ------------------------ | ------------------------------------------ |
| `250 2.1.5 Recipient ok` | Adresse **existe**                         |
| `550 5.1.1 User unknown` | Adresse **n'existe pas**                   |
| `250 OK` (systématique)  | Catch-all -  le serveur ne vérifie jamais   |
