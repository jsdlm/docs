# Latence
```bash
# mettre dans le .vmx
keyboard.vusb.enable = "TRUE"
```
# Pointeur souris invisible
To fix a disappearing mouse pointer in VMware Workstation, upgrade the virtual machine's hardware compatibility version to match your current VMware installation.
# Pointeur qui sort
Edit > Preferences > Input 
# NAT
```bash
C:\ProgramData\VMware\vmnetnat.conf
[incomingtcp]
<port_hote> = <ip_vm>:<port_vm>

net stop "VMware NAT Service" && net start "VMware NAT Service"
```

