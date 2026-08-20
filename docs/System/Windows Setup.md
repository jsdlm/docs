# Install

**BASE**
```
winget install Mozilla.Firefox 7zip.7zip Notepad++.Notepad++ OpenVPNTechnologies.OpenVPNConnect VideoLAN.VLC Microsoft.WindowsTerminal Microsoft.VisualStudioCode Google.Chrome DominikReichl.KeePass Microsoft.PowerShell Git.Git Greenshot.Greenshot Obsidian.Obsidian Bitwarden.Bitwarden Element.Element
```

**PERSO**
```
winget install Discord.Discord Nextcloud.NextcloudDesktop MullvadVPN.MullvadVPN
```

**JEUX**
```
winget install Nvidia.GeForceExperience Valve.Steam Blizzard.BattleNet RiotGames.LeagueOfLegends.EUW
```

**PRO**
```
winget install ShiningLight.OpenSSL.Light Python.Python.3.13 lsd-rs.lsd
```

**PRO - OLD**
```
winget install Flameshot.Flameshot ksnip.ksnip
```

**MISC**
```
winget install WiresharkFoundation.Wireshark IDRIX.VeraCrypt NirSoft.WifiInfoView Oracle.JDK.21 Gyan.FFmpeg MediaArea.MediaInfo.GUI
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

