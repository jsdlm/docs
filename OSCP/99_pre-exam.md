# Pre-Exam

## Checklist Technique

- [ ] Kali Linux VM (x86-64, dernière image VMware)
- [ ] Webcam fonctionnelle
- [ ] Navigateur : Chrome/Firefox/Brave/Edge avec plugin Janus
- [ ] Screen sharing configuré — utiliser **Xorg/X11**, PAS Wayland
- [ ] Connexion internet stable
- [ ] OSID et hash MD5 reçus

---

## Checklist Logiciels

```bash
# Vérifier tous les outils d'un coup
for tool in nmap rustscan feroxbuster nxc impacket-psexec bloodhound chisel ligolo-ng; do
  which $tool && echo "[+] $tool OK" || echo "[-] $tool MISSING"
done
```

- [ ] Chisel / Ligolo-ng binaries (Kali + Windows)
- [ ] Mimikatz / Rubeus
- [ ] Impacket tools (secretsdump, psexec, wmiexec, mssqlclient, GetUserSPNs, GetNPUsers)
- [ ] PowerView / SharpHound
- [ ] LinPEAS / WinPEAS téléchargés
- [ ] SigmaPotato / PrintSpoofer binaries
- [ ] Webshells prêts (PHP, ASPX)
- [ ] Burp Suite Community ou Pro
- [ ] BloodHound + Neo4j

---

## Checklist Documentation

- [ ] Outil de notes prêt (Obsidian, CherryTree, VS Code)
- [ ] Outil screenshot configuré (Flameshot ou équivalent)
- [ ] Dossier screenshots organisé par machine
- [ ] Template rapport téléchargé (OffSec template)
- [ ] Accès au panel de contrôle OSCP vérifié

---

## La Veille

- ✅ Dormir 7-8h minimum
- ✅ Préparer les outils (VPN, VM Kali, monitors)
- ✅ Tester la connexion au VPN exam
- ✅ Créer la structure de dossiers exam
- ✅ Backup des scripts importants sur USB
- ❌ Ne pas rester tard à réviser

---

## Le Matin

- ✅ Manger un bon repas (pas de crash caféine)
- ✅ S'hydrater
- ✅ Aller aux toilettes avant de commencer
- ✅ Vider le bureau des distractions
- ✅ Avoir eau et snacks à portée
- ✅ Désactiver notifications téléphone/Discord

---

## Connexion VPN Exam

> Le pack VPN est envoyé au **moment du démarrage** de l'exam, pas avant.

```shell
# Extraire
tar xvfj exam-connection.tar.bz2

# Connecter
sudo openvpn OS-XXXXXX-OSCP.ovpn
```

### Troubleshooting VPN

```shell
# Vérifier les interfaces réseau en conflit
ip addr

# Kill les VPN existants
sudo killall openvpn

# Si toujours des problèmes : re-télécharger un pack VPN frais depuis le panel
```

---

## Structure de Dossiers Recommandée

```
exam/
├── 192.168.x.10/          # Machine 1 (WS - AD)
│   ├── nmap/
│   ├── screenshots/
│   └── loot/
├── 192.168.x.20/          # Machine 2 (SRV - AD)
├── 192.168.x.30/          # Machine 3 (DC - AD)
├── 192.168.x.40/          # Standalone 1
├── 192.168.x.50/          # Standalone 2
├── 192.168.x.60/          # Standalone 3
└── report/
```
