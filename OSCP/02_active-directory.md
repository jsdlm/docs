# Active Directory Methodology

## Flowchart AD

```text
┌─────────────────────────────────────────────────────────────────┐
│                    OSCP AD SET METHODOLOGY                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────┐    Validate     ┌──────────────┐              │
│  │  Start with  │───────────────▶│   Machine #1  │              │
│  │  Credentials │   WinRM/RDP     │   (WS/Client) │              │
│  └──────────────┘                 └───────┬──────┘              │
│                                           │                      │
│                         BloodHound + WinPEAS + PrivescCheck      │
│                                           ▼                      │
│  ┌────────────────────────────────────────────────────────┐     │
│  │  Look For:                                              │     │
│  │  • SeImpersonatePrivilege → SigmaPotato                │     │
│  │  • SeBackupPrivilege → SAM/SYSTEM dump                 │     │
│  │  • Registry AutoLogon → New creds                      │     │
│  │  • AllExtendedRights → Password reset                  │     │
│  │  • Saved creds → LaZagne                               │     │
│  │  • PowerShell history → Leaked passwords               │     │
│  └────────────────────────────────────────────────────────┘     │
│                                           │                      │
│                                   PrivEsc + Pivot                │
│                                    (Ligolo-ng)                   │
│                                           ▼                      │
│  ┌──────────────┐   Spray creds   ┌──────────────┐              │
│  │  Machine #2  │◀────────────────│   Internal   │              │
│  │  (SRV/Member)│   or new creds  │   Network    │              │
│  └───────┬──────┘                 └──────────────┘              │
│          │                                                       │
│  • Check MSSQL → Query for creds                                │
│  • Check shares → Sensitive files                               │
│  • Check history → PowerShell history                           │
│          │                                                       │
│          ▼                                                       │
│  ┌──────────────┐                                               │
│  │  Machine #3  │  ← SeBackupPrivilege + SAM dump               │
│  │  (DC)        │  ← DCSync si droits suffisants                 │
│  └───────┬──────┘  ← Pass-the-Hash avec NTLM Admin              │
│          │                                                       │
│          ▼                                                       │
│  ┌──────────────┐                                               │
│  │   DOMAIN     │  proof.txt + hostname + ipconfig              │
│  │   ADMIN!     │                                               │
│  └──────────────┘                                               │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Kill Chains AD

### Chain 1 : ACL Abuse

```text
User A (credentials fournis)
    │
    ├─► BloodHound trouve AllExtendedRights sur User B
    │
    ├─► Reset mot de passe de User B
    │
    ├─► User B a GenericAll sur User C (Admin)
    │
    └─► Reset mot de passe de User C → accès Admin
```

### Chain 2 : Credential Hopping

```text
User A (credentials fournis)
    │
    ├─► WinPEAS trouve credentials AutoLogon → User B
    │
    ├─► User B accède à Machine #2
    │
    ├─► MSSQL sur Machine #2 contient creds → User C
    │
    ├─► User C a SeBackupPrivilege sur le DC
    │
    └─► Dump SAM → hash Admin → PTH vers le DC
```

### Chain 3 : Service Abuse

```text
User A (credentials fournis)
    │
    ├─► SeImpersonatePrivilege → SigmaPotato → Local Admin
    │
    ├─► Extraire creds en cache avec mimikatz → User B
    │
    ├─► User B membre de "SQL Admins" → accès MSSQL
    │
    ├─► xp_cmdshell sur Machine #2 → Shell
    │
    └─► Machine #2 a DCSync rights → Domain Admin
```

### Chain 4 : GPO Abuse

```text
User A (credentials fournis)
    │
    ├─► BloodHound trouve accès en écriture sur GPO
    │
    ├─► SharpGPOAbuse → Ajouter User A aux Admins locaux
    │
    ├─► gpupdate /force
    │
    └─► Admin sur toutes les machines affectées par la GPO
```
