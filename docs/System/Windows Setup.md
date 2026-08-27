# Install

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
winget install ShiningLight.OpenSSL.Light lsd-rs.lsd WiresharkFoundation.Wireshark IDRIX.VeraCrypt NirSoft.WifiInfoView Oracle.JDK.21 Gyan.FFmpeg MediaArea.MediaInfo.GUI
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