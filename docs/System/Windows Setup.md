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
winget install ShiningLight.OpenSSL.Light lsd-rs.lsd WiresharkFoundation.Wireshark IDRIX.VeraCrypt NirSoft.WifiInfoView Oracle.JDK.21 Gyan.FFmpeg MediaArea.MediaInfo.GUI Microsoft.Sysinternals.Suite
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

Deploy a Windows Virtual Machine

   > [Where can I find a Windows 10 Virtual Machine?](https://www.microsoft.com/en-us/software-download/windows10)

   > [Where can I find a Windows 11 Virtual Machine?](https://www.microsoft.com/en-us/software-download/windows11)
## Pre-Install Procedures

**You MUST disable Windows Defender for a smooth install**. The best way to accomplish this is through Group Policy.
In Windows versions 1909 and higher, Tamper Protection was added.
**Tamper Protection must be disabled first, otherwise Group Policy settings are ignored.**

1. Open Windows Security (type `Windows Security` in the search box)
2. Virus & threat protection > Virus & threat protection settings > Manage settings
3. Switch `Tamper Protection` to `Off`

> It is not necessary to change any other setting (`Real Time Protection`, etc.)
> **Important!** Tamper Protection must be disabled before changing Group Policy settings.

To permanently disable Real Time Protection:

1. Make sure you disabled Tamper Protection
2. Open Local Group Policy Editor (type `gpedit` in the search box)
3. Computer Configuration > Administrative Templates > Windows Components > Microsoft Defender Antivirus > Real-time Protection
4. Enable `Turn off real-time protection`
5. **Reboot**

> Make sure to **reboot** before making the next change

To permanently disable Microsoft Defender:

1. Make sure you rebooted your machine
2. Open Local Group Policy Editor (type `gpedit` in the search box)
3. Computer Configuration > Administrative Templates > Windows Components > Microsoft Defender Antivirus
4. Enable `Turn off Microsoft Defender Antivirus`
5. **Reboot**
## Installation

1. Complete the pre-install procedures by disabling Defender
2. Run PowerShell as Administrator
3. `Set-ExecutionPolicy Unrestricted -force`
4. `cd .\winlegion-vm`
5. `Get-ChildItem .\ -Recurse | Unblock-File`
6. `.\install.ps1`


# Bypass NRO

Sur l'écran de configuration réseau (le choix du pays ou de la connexion internet), appuyez sur les touches **Maj + F10** (ou **Maj + Fn + F10**) de votre clavier pour ouvrir l'invite de commandes.
Tapez la commande suivante et validez avec Entrée :  `oobe\bypassnro`