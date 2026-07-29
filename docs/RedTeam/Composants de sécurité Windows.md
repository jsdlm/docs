# Antivirus (Microsoft Defender)

- **Fonctionnement** : scan à l'accès (on-access) et à la demande, moteur signatures + heuristique comportementale + ML cloud (MAPS/Smart Protection).
- **Checks** :
  - Signatures : hash ou pattern de code connu - détecte le payload au moment où il touche le disque ou est chargé en mémoire, avant ou juste après l'exécution.
  - Heuristique comportementale : actions post-exploitation une fois le payload lancé (spawn de nouveaux processus, commandes shell, injection de processus, outils post-exploitation tiers).
  - Réputation cloud du fichier.

# AMSI (Antimalware Scan Interface)

- **Fonctionnement** : interface exposée par Windows, appelée par les interpréteurs (PowerShell, WSH, VBA, JScript) juste avant l'exécution du contenu, qui envoie le buffer au moteur AV enregistré.
- **Checks** : contenu du script en clair (post-désobfuscation/déchiffrement en mémoire) - donc efficace même si le payload est obfusqué sur disque.

AMSI est un standard agnostique de l'éditeur : n'importe quel antivirus tiers peut s'enregistrer comme fournisseur AMSI à l'installation, ce n'est pas spécifique à Defender. Un développeur tiers peut aussi soumettre des requêtes de scan depuis son application (ex. pour scanner une entrée utilisateur non fiable), en chargeant _amsi.dll_ ou en passant par la couche COM.

![](https://lwfiles.mycourse.app/66e95234fe489daea7060790-public/f3aae248a07c30500a417ddedba31b4e.jpg)

Composants natifs "AMSI aware" :
- User Account Control (élévation EXE, COM, MSI, ActiveX)
- PowerShell (scripts, usage interactif, évaluation dynamique de code)
- Windows Script Host (wscript.exe et cscript.exe)
- JavaScript et VBScript
- Macros VBA d'Office

AMSI n'est qu'un vecteur de transmission des données vers l'antivirus : c'est l'antivirus qui décide si le contenu est malveillant, pas AMSI lui-même.

La plupart des bypass AMSI consistent à casser ce « pont » entre l'application et le moteur AV - patch mémoire, breakpoints matériels - soit pour empêcher son initialisation, soit pour l'empêcher de soumettre l'échantillon et lui faire renvoyer un faux « no threat ».

Beaucoup de ces bypass sont eux-mêmes détectés ou laissent des indicateurs exploitables par une blue team. Mieux vaut donc traiter ses scripts PowerShell comme n'importe quel artefact : identifier et modifier les portions de code détectées comme malveillantes plutôt que de casser AMSI.

# SmartScreen

- **Fonctionnement** : intervient au moment du téléchargement/lancement d'un fichier marqué Mark-of-the-Web (MOTW), interroge un service cloud Microsoft.
- **Checks** : réputation du fichier (hash), réputation de l'éditeur/certificat de signature, réputation de l'URL source.

Le Mark of the Web (MOTW) est un identifiant de zone qui marque les fichiers téléchargés depuis Internet comme potentiellement dangereux. Visible dans les propriétés du fichier sous l'Explorateur, ou via PowerShell.

![](https://lwfiles.mycourse.app/66e95234fe489daea7060790-public/e2924df834b666c79c4d677ad723d63f.png)
![](img/Pasted%20image%2020260729235535.png)

# AppLocker

- **Fonctionnement** : moteur de règles (whitelist/blacklist) appliqué via GPO, intercepte les tentatives de lancement de binaires/scripts/installeurs.
- **Checks** : chemin du fichier, éditeur (certificat de signature), hash du fichier - selon les règles définies (Executable, Script, Windows Installer, DLL, Packaged apps).

![](img/Pasted%20image%2020260729235423.png)
