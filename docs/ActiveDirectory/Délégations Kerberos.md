# Unconstrained Delegation
Users : ceux dont tu captures le TGT en mémoire
Services : n'importe quel service du domaine

```
ldapsearch (&(samAccountType=805306369)(userAccountControl:1.2.840.113556.1.4.803:=524288)) --attributes samaccountname
```
# Constrained Delegation avec Protocol Transition
Users : n'importe lequel (tu choisis librement)
Services : tous les services types (eg. CIFS/HTTP) des Users/Computers listés dans msDS-AllowedToDelegateTo (with rubeus /altservice)

```
ldapsearch (&(samAccountType=805306369)(msDS-AllowedToDelegateTo=*)) --attributes samAccountName,msDS-AllowedToDelegateTo,userAccountControl

$userAccountControl_value = "16781312"
[System.Convert]::ToBoolean($userAccountControl_value -band 16777216)
```

# Constrained Delegation sans Protocol Transition
Users : uniquement ceux dont tu as déjà un TGS pour le service front-end
Services : tous les services types (eg. CIFS/HTTP) des Users/Computers listés dans msDS-AllowedToDelegateTo (with rubeus /altservice)

# S4U2self Computer Takeover (Resource-Based / abus direct)
Users : n'importe lequel (tu choisis librement, ici Administrator)
Services : uniquement les services types (eg. CIFS/HTTP) de la machine elle-même dont tu possèdes le TGT (with rubeus /self + /altservice)
Le point qui distingue cette section des trois autres : il n'y a aucune entrée dans msDS-AllowedToDelegateTo ni aucune délégation configurée. Tu es limité à la machine dont tu détiens le TGT, car la réécriture de SPN ne fonctionne que sur ses propres services (ceux qu'elle peut déchiffrer avec sa clé de compte).