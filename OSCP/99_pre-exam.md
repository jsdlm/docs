# Pre-Exam

## Checklist Technique

- [ ] Kali Linux VM (x86-64, dernière image VMware)
- [ ] Webcam fonctionnelle
- [ ] Connexion internet stable
- [ ] OSID et hash MD5 reçus

---

## Checklist Logiciels

- [ ] Ligolo-ng binaries (Kali + Windows)
- [ ] NetExec
- [ ] Nmap
- [ ] Mimikatz / Rubeus
- [ ] Impacket
- [ ] PowerView / SharpHound
- [ ] LinPEAS / WinPEAS
- [ ] SigmaPotato / PrintSpoofer binaries
- [ ] Webshells prêts (PHP, ASPX)
- [ ] Burp Suite Community
- [ ] BloodHound + Neo4j

---

## Checklist Documentation

- [ ] Outil de notes
- [ ] Outil screenshot
- [ ] Dossier screenshots organisé par machine
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

## Troubleshooting VPN

```shell
# Vérifier les interfaces réseau en conflit
ip addr

# Kill les VPN existants
sudo killall openvpn

# Si toujours des problèmes : re-télécharger un pack VPN frais depuis le panel
```
