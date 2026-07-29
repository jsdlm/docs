
```
ldapsearch (objectClass=groupPolicyContainer) --attributes displayName,gPCFileSysPath
```

- **GptTmpl.inf** → restricted groups (admins locaux définis via GPO) — c'est ce que tu veux pour identifier qui est admin local sur quelles machines.
```
download \\dublin.contoso.com\SysVol\dublin.contoso.com\Policies\{2EE8D52F-E5E2-4C92-B7A6-6AE0C0A0183C}\Machine\Microsoft\Windows NT\SecEdit\GptTmpl.inf
```
- **Registry.pol** → paramètres de registre poussés par GPO, dont les règles AppLocker.
```
download \\dublin.contoso.com\SysVol\dublin.contoso.com\Policies\{2EE8D52F-E5E2-4C92-B7A6-6AE0C0A0183C}\Registry.pol
```

Pour identifier les chemins de lateral movement, commence par **GptTmpl.inf** sur les GPOs `Workstation Admins` et `Web Admins`.

