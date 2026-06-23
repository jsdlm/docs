# Standalone Machine Methodology

# Flowchart

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                      STANDALONE MACHINE METHODOLOGY                         │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────┐
│  START      │
│  nmap scan  │
└──────┬──────┘
       │
       ▼
┌──────────────────────────────────────────────────────────────┐
│              Identifier les Services                          │
├──────────────────────────────────────────────────────────────┤
│  FTP(21) │ SSH(22) │ HTTP(80) │ SMB(445) │ RDP(3389) │ Other │
└────┬─────┴────┬────┴────┬─────┴────┬─────┴────┬──────┴───────┘
     │          │         │          │          │
     ▼          │         ▼          ▼          │
┌──────────┐    │    ┌─────────┐ ┌─────────┐    │
│ Anonymous│    │    │ WebApp  │ │  Null   │    │
│  Login?  │    │    │  Enum   │ │ Session?│    │
└────┬─────┘    │    └────┬────┘ └────┬────┘    │
     │          │         │           │          │
     ▼          │         ▼           ▼          │
┌──────────┐    │    ┌─────────┐ ┌─────────┐    │
│ Download │    │    │ Default │ │ Download│    │
│  Files   │    │    │  Creds? │ │  Files  │    │
└────┬─────┘    │    └────┬────┘ └────┬────┘    │
     │          │         │           │          │
     ▼          │         ▼           ▼          │
┌──────────┐    │    ┌─────────┐ ┌─────────┐    │
│ Crack    │    │    │ LFI/RCE │ │  NTLM   │    │
│ Hashes   │    │    │ Exploit │ │  theft  │    │
└────┬─────┘    │    └────┬────┘ └────┬────┘    │
     └──────────┴────┬────┴───────────┴──────────┘
                     │
                     ▼
          ┌──────────────────┐
          │  Got Credentials │
          │    or Shell?     │
          └────────┬─────────┘
                   │
          ┌────────┴────────┐
          │                 │
          ▼                 ▼
   ┌────────────┐    ┌────────────┐
   │ Credential │    │   Shell    │
   │   Spray    │    │  Obtained  │
   └─────┬──────┘    └─────┬──────┘
         └────────┬────────┘
                  │
                  ▼
         ┌────────────────┐
         │  Privilege     │
         │  Escalation    │
         ├────────────────┤
         │Linux:          │
         │• sudo -l       │
         │• SUID          │
         │• Disk group    │
         │• Cron jobs     │
         ├────────────────┤
         │Windows:        │
         │• SeImpersonate │
         │• SeBackup      │
         │• DLL Hijack    │
         │• Unquoted Svc  │
         └───────┬────────┘
                 │
                 ▼
         ┌────────────────┐
         │   ROOT/ADMIN   │
         │   proof.txt    │
         └────────────────┘
```

---

# Kill Chains

## Chain 1 : FTP → Keychain Crack → RDP

```text
Target: 192.168.87.111 (Windows)
1. FTP anonymous login → download .keychain file
2. keychain2john → john → crack password
3. RDP avec les credentials trouvés
4. Privilege escalation → SysaxScheduler exploit
5. SYSTEM → proof.txt
```

## Chain 2 : WordPress LFI → Config Creds → SSH

```text
Target: 192.168.122.112 (Linux)
1. nmap → Port 80 WordPress
2. WPScan → plugin Mail Masta
3. LFI via php://filter → wp-config.php (base64)
4. Décoder → database credentials
5. SSH avec les credentials trouvés
6. sudo mawk → GTFOBins → root
```

## Chain 3 : File Manager → Webshell → Disk Group

```text
Target: Extplorer (Linux)
1. gobuster → répertoire /eXtplorer
2. Default credentials: admin:admin
3. Upload PHP webshell
4. id → utilisateur dans le groupe "disk"
5. debugfs /dev/sda1 → lire /root/.ssh/id_rsa
6. SSH en tant que root
```

## Chain 4 : Default Creds → ZIP Password → DLL Hijack

```text
Target: 192.168.122.111 (Windows)
1. HTTP → File Management System (default creds)
2. Download backup.zip
3. zip2john → john → crack password
4. exiftool → trouver username dans les métadonnées
5. RDP spray avec les credentials trouvés
6. DLL Hijacking (Wondershare Dr.Fone) → SYSTEM
```

## Chain 5 : GlassFish → WAR Deploy → Root

```text
Target: Fish (Linux)
1. Port 4848 → GlassFish admin
2. Path traversal (CVE-2017-1000028) → mot de passe admin
3. Login sur la console admin
4. Déployer un fichier WAR malveillant
5. Reverse shell en tant qu'utilisateur glassfish
6. LinPEAS → vecteur privesc → root
```

## Chain 6 : LibreOffice Macro → ODT Upload

```text
Target: Craft (Linux)
1. Web app permet l'upload de fichiers ODT
2. Créer un ODT avec macro Python (reverse shell)
3. Upload et attendre l'exécution
4. Shell en tant qu'utilisateur
5. LinPEAS → privesc → root
```
