# Install

```
winget install --exact --silent --accept-source-agreements --accept-package-agreements --disable-interactivity Mozilla.Firefox
```

**BASE**
```
winget install Mozilla.Firefox 7zip.7zip Notepad++.Notepad++ OpenVPNTechnologies.OpenVPNConnect VideoLAN.VLC Microsoft.WindowsTerminal Microsoft.VisualStudioCode Google.Chrome DominikReichl.KeePass Microsoft.PowerShell Git.Git Greenshot.Greenshot Obsidian.Obsidian Bitwarden.Bitwarden Nextcloud.NextcloudDesktop Python.Python.3.13
```

**PERSO**
```
winget install Discord.Discord MullvadVPN.MullvadVPN Element.Element
```

**JEUX**
```
winget install Nvidia.GeForceExperience Valve.Steam Blizzard.BattleNet RiotGames.LeagueOfLegends.EUW Corsair.iCUE.5
```

**PRO**
```
winget install ShiningLight.OpenSSL.Light lsd-rs.lsd WiresharkFoundation.Wireshark IDRIX.VeraCrypt NirSoft.WifiInfoView Oracle.JDK.21 Gyan.FFmpeg MediaArea.MediaInfo.GUI Microsoft.Sysinternals.Suite Microsoft.DotNet.Framework.Runtime
```

**OLD**
```
winget install Flameshot.Flameshot ksnip.ksnip
```

**UPGRADE**
```
winget update
winget upgrade --all
```

**REPAIR**
```
Add-AppxPackage -RegisterByFamilyName -MainPackage Microsoft.DesktopAppInstaller_8wekyb3d8bbwe
winget repair
winget source reset --force
winget upgrade --verbose-logs
```

# WSL

```
wsl --install -d Debian
```

During this process, you will need to reboot your computer once. The install will automatically resume on reboot. And, at one point, it may hang at 0% for awhile. Leave it alone. It's not broken. It's just confusing.
If you're running Windows 10 or 11 from a Virtual Machine, make sure to enable nested virtualization (e.g., VT-x, AMD-v) for the VM.
#### Tips

- The Windows c:\ drive is available via /mnt/c
- You can run Windows executables from the WSL Ubuntu environment

# Docker

```
winget install Docker.DockerDesktop
```

# Hardening

- [ ] Dernière version de Windows 10 ou de Windows 11
- [ ] Mot de passe du BIOS configuré
- [ ] Chiffrement BitLocker activé (*Computer > right-click on main drive > Turn on BitLocker*)
- [ ] Code PIN BitLocker configuré :
    - *Windows + R > `gpedit.msc` > Computer Configuration > Administrative Templates > Windows Components > BitLocker Drive Encryption > Operating Systems Drives*
    - Open 'Require additional authentication at startup'
        - Check 'Enabled'
        - Uncheck 'Allow BitLocker without a compatible TPM'
        - 'OK'
    - Open 'Enable use of BitLocker authentication requiring preboot keyboard input on slates'
        - Check 'Enabled'
        - 'OK'
    - Reboot
    - Using PowerShell: `manage-bde -protectors -add c: -TPMAndPIN`
    - Set a PIN
    - Reboot

# Firewall

VM Windows pour dialoguer en host only 
```powershell
Set-NetConnectionProfile -InterfaceAlias "Ethernet0" -NetworkCategory Private
Enable-NetFirewallRule -Name FPS-ICMP4-ERQ-In
```

Ou désactiver temporairement le firewall
```powershell
Set-NetFirewallProfile -Profile Domain,Private,Public -Enabled False
```

# winlegion-vm

Déployer une machine virtuelle Windows

   > [Où puis-je trouver une machine virtuelle Windows 10 ?](https://www.microsoft.com/en-us/software-download/windows10)

   > [Où puis-je trouver une machine virtuelle Windows 11 ?](https://www.microsoft.com/en-us/software-download/windows11)

## Pré-requis

**Vous DEVEZ désactiver Windows Defender pour une installation sans accroc**. La meilleure façon d'y parvenir est via la stratégie de groupe (Group Policy).
Dans les versions de Windows 1909 et supérieures, la protection contre les falsifications (Tamper Protection) a été ajoutée.
**La protection contre les falsifications doit être désactivée en premier, sinon les paramètres de stratégie de groupe sont ignorés.**

1. Ouvrez la Sécurité Windows (tapez `Windows Security` dans la barre de recherche)
2. Protection contre les virus et menaces > Paramètres de protection contre les virus et menaces > Gérer les paramètres
3. Basculez `Protection contre les falsifications` sur `Désactivé`

> **Important !** Ne désactiver aucun autre paramètre (`Protection en temps réel`, etc.)
> **Important !** La protection contre les falsifications doit être désactivée avant de modifier les paramètres de stratégie de groupe.

Pour désactiver définitivement la protection en temps réel :
1. Assurez-vous d'avoir désactivé la protection contre les falsifications
2. Ouvrez l'Éditeur de stratégie de groupe locale (tapez `gpedit` dans la barre de recherche)
3. Configuration ordinateur > Modèles d'administration > Composants Windows > Antivirus Microsoft Defender > Protection en temps réel
4. Activez `Désactiver la protection en temps réel`
5. **Redémarrez**
> Assurez-vous de **redémarrer** avant d'effectuer la modification suivante

Pour désactiver définitivement Microsoft Defender :
1. Assurez-vous d'avoir redémarré votre machine
2. Ouvrez l'Éditeur de stratégie de groupe locale (tapez `gpedit` dans la barre de recherche)
3. Configuration ordinateur > Modèles d'administration > Composants Windows > Antivirus Microsoft Defender
4. Activez `Désactiver l'antivirus Microsoft Defender`
5. **Redémarrez**
> Assurez-vous de **redémarrer** avant d'effectuer la modification suivante
## Installation

1. Effectuez les procédures de pré-installation en désactivant Defender
2. Exécutez PowerShell en tant qu'administrateur
3. `Set-ExecutionPolicy Unrestricted -force`
4. `cd .\winlegion-vm`
5. `Get-ChildItem .\ -Recurse | Unblock-File`
6. `.\install.ps1`


# Bypass NRO

Sur l'écran de configuration réseau (le choix du pays ou de la connexion internet), appuyez sur les touches **Maj + F10** (ou **Maj + Fn + F10**) de votre clavier pour ouvrir l'invite de commandes.
Tapez la commande suivante et validez avec Entrée :  `oobe\bypassnro`