
Sur les cartes mères bas de gamme (ex. BIOS AMI), les revendeurs falsifient la table **SMBIOS/DMI** ou flashent une version modifiée du BIOS.
* **Le bidouillage :** Ils réécrivent les chaînes de caractères déclaratives du firmware (nom du modèle CPU, quantité/fréquence de la RAM).
* **Conséquence :** L'OS lit aveuglément ces tables et affiche un composant puissant (ex. Intel i9) alors que la carte mère intègre un composant obsolète (ex. i3).

---
# Détection sous Linux

Contourne les tables déclaratives du BIOS en interrogeant directement le matériel.
```bash
loadkeys fr

# 1. Lire le CPU réel directement depuis le silicium (CPUID)
lscpu

# Autre variante pour lire les données brutes du CPU
cat /proc/cpuinfo

# 2. Lire la table BIOS/SMBIOS (déclarative et potentiellement falsifiée)
sudo dmidecode -t processor
# Compasaron : si dmidecode annonce un i9 mais lscpu indique un i3 -> fraude.

# 3. Vérifier la RAM réelle adressable par le noyau
free -h

# 4. Lire la déclaration SMBIOS de la mémoire
sudo dmidecode -t memory

```

---

# Détection sous Windows

Le Gestionnaire des tâches et les paramètres système étant trompés par le BIOS, il faut utiliser des logiciels lisant directement les puces matérielles :

* **CPU-Z :** lit les instructions `CPUID` réelles du processeur et les puces `SPD` de la RAM.
* **HWiNFO64 :** analyse matérielle bas niveau indépendante des déclarations du BIOS.
