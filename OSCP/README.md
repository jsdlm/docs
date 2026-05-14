# OSCP Notes

## Navigation

| Fichier | Contenu |
| :--- | :--- |
| [pre-exam.md](99_pre-exam.md) | Checklist équipement, veille, matin J, connexion VPN |
| [standalone.md](01_standalone.md) | Méthodologie standalone complète — phases + privesc + kill chains |
| [active-directory.md](02_active-directory.md) | Méthodologie AD complète — phases + pivoting + kill chains |
| [enumeration.md](03_enumeration.md) | Techniques générales de recon (nmap, web, services) |
| [initial-access.md](04_initial-access.md) | Payloads, reverse shells, credential spraying |
| [reporting.md](98_reporting.md) | Template rapport, screenshots, checklist soumission |
| [stuck.md](97_stuck.md) | Quand bloqué + pitfalls + mindset |

---

## Scoring Strategy

**Minimum pour passer : 70/100 points**

| Option | Détail | Points |
| :--- | :--- | :---: |
| Conservative | 3 standalone complets (20 pts chacun) | 60 pts |
| **Recommandé** | **2 standalone complets + AD user** | **70 pts** |
| Aggressive | 1 standalone complet + AD complet | 70 pts |

> **Pro Tip** : Viser 2-3 machines complètes plutôt que du partiel sur toutes les 5.

---

## Time Management — 24h

| Phase | Temps | Objectif |
| :--- | :---: | :--- |
| Setup + enum initiale tous les targets | 0h–1h | Identifier les types de services |
| AD Set (priorité max) | 1h–7h | Compléter la chaîne AD en premier |
| Standalone #1 | 7h–10h | Machine la plus facile |
| Standalone #2 | 10h–13h | Machine moyenne |
| Standalone #3 | 13h–17h | Machine difficile |
| Buffer | 17h–20h | Machines bloquées, re-enum |
| Rapport | 20h–24h | Documentation + screenshots |

---

## Règles Exam

| Règle | Détail |
| :--- | :--- |
| Metasploit | **1 seule machine** autorisée — utiliser en dernier recours |
| Screenshots | Obligatoires : proof.txt + hostname + IP dans le **même** screenshot |
| Flags | Soumettre dans le panel **avant** la fin de l'exam (changent après revert) |
| Rapport | Délai : **24h** après la fin de l'exam |
| Metasploit multi | Invalide tous les points si utilisé sur plusieurs machines |

---

## Common Mistakes

- [ ] Ne pas soumettre les flags avant un revert
- [ ] Screenshots avec IP manquante
- [ ] Oublier de documenter les étapes
- [ ] Utiliser Metasploit sur plusieurs machines
- [ ] Ne pas lire les prérequis d'un exploit
- [ ] Trop compliquer (l'OSCP c'est les bases)
