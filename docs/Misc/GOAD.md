
https://orange-cyberdefense.github.io/GOAD/installation/windows/#__tabbed_1_2
# 1. Préparer le réseau AVANT toute installation

Virtual Network Editor (lancé en administrateur) : ne conserver que deux réseaux.

|Réseau|Type|Subnet|DHCP|
|---|---|---|---|
|VMnet0|Host-only|192.168.56.0/24|Désactivé|
|VMnet8|NAT|(par défaut)|Activé|

Le DHCP doit rester actif sur le NAT : Vagrant attend une première adresse par ce biais avant de poser les IP statiques. Sur le host-only il doit rester désactivé, les VM ayant des IP fixes.

# 2. Attribuer l'IP à l'adaptateur hôte

Panneau de configuration > Connexions réseau > adaptateur VMware correspondant > Propriétés > IPv4 :

- Adresse : 192.168.56.1
- Masque : 255.255.255.0

Valider avec OK sur les deux fenêtres, sinon le changement n'est pas appliqué.

Vérifier ensuite avec `ipconfig` que l'adaptateur porte bien 192.168.56.1. Sans cette adresse, l'hôte n'a aucune route vers les VM et tous les SSH partent en timeout.

# 3. Lancer GOAD

PowerShell **en administrateur** (Vagrant ne peut pas manipuler les réseaux host-only sans privilèges) :

```powershell
venv\Scripts\activate.ps1
python goad.py -m vm
install
```

# Points de vigilance

**Toujours passer `-m vm`.** Sans ce flag, GOAD retombe sur le provisioner `local`, crée une instance marquée comme telle, et échoue ensuite avec `provisioner does not exist` ou `AttributeError: 'NoneType' object has no attribute 'install'`.

**Une instance créée avec le mauvais provisioner reste cassée.** Soit corriger le champ `provisioner` dans `workspace\<instance>\instance.json`, soit supprimer le dossier et recréer.

**Ne pas accumuler les instances.** Chaque tentative clone ses propres VM. Détruire les instances inutilisées avant d'en relancer une.

**Les VM n'apparaissent pas dans VMware.** Vagrant ne les ajoute pas à la bibliothèque. File > Scan for Virtual Machines sur le dossier `workspace\`, ou ouvrir directement les `.vmx` sous `workspace\<instance>\provider\.vagrant\machines\<VM>\vmware_desktop\`.

**Blocage sur "Waiting for the VM to receive an address".** Vérifier que les services `VMware NAT Service` et `VMware DHCP Service` tournent (`Get-Service VMware*`).

**Vagrant en erreur `cannot load such file -- vagrant`.** Réparer les plugins :

```powershell
vagrant plugin expunge --reinstall
vagrant plugin install vagrant-vmware-desktop vagrant-reload
```