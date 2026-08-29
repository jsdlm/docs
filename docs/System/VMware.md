# Latence
```bash
# mettre dans le .vmx
keyboard.vusb.enable = "TRUE"
```
# Pointeur souris invisible
To fix a disappearing mouse pointer in VMware Workstation, upgrade the virtual machine's hardware compatibility version to match your current VMware installation.
# Pointeur qui sort
Edit > Preferences > Input 
# Perte de focus VMware

**Symptôme** : le focus quitte la VM tout seul, toutes VM confondues.
**Logs** (`<dossier VM>\vmware.log`) :
```
mouse Poll timeout: Something may be hung... ungrabbing
Monitor Mode: ULM
```

**Cause** : HVCI ("Intégrité de la mémoire") force Workstation au-dessus d'Hyper-V.
**Vérif** :
```powershell
Get-CimInstance Win32_DeviceGuard -Namespace root\Microsoft\Windows\DeviceGuard |
  Select SecurityServicesRunning
```
`{2}` = actif, `{0}` = désactivé.

**Fix GUI** : Sécurité Windows → Sécurité des appareils → Isolation du noyau → Intégrité de la mémoire → Désactivé → redémarrer.
**Fix CLI** (admin) :
```powershell
Set-ItemProperty -Path 'HKLM:\SYSTEM\CurrentControlSet\Control\DeviceGuard\Scenarios\HypervisorEnforcedCodeIntegrity' -Name Enabled -Value 0
```

**Compromis** : perte de la protection anti-rootkit noyau (BYOVD). WSL2 et Docker restent fonctionnels.
# NAT
```bash
C:\ProgramData\VMware\vmnetnat.conf
[incomingtcp]
<port_hote> = <ip_vm>:<port_vm>

net stop "VMware NAT Service" && net start "VMware NAT Service"
```

