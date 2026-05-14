# STUCK

## SPRAY EVERYTHING

- Tu as trouvé un nouvel user ? `AJOUTE-LE À USERS.TXT`
- Tu as trouvé un nouveau mot de passe ? ou quelque chose qui _pourrait_ être un password ? `AJOUTE-LE À PASSWORDS.TXT`
- `SPRAY SPRAY SPRAY`
- FTP, SSH, CME, SMB, KERBEROS, CONSOLES ADMIN, TOUT CE QUI ACCEPTE DES CREDENTIALS → ESSAIE

## TRY DEFAULT CREDS AND DUMB CREDS

- Tu as trouvé un logiciel que t'as jamais vu ? `CHERCHE LES CREDENTIALS PAR DÉFAUT`
- Tu as trouvé un logiciel que tu connais ? `CHERCHE LES CREDENTIALS PAR DÉFAUT`
- Tu as trouvé un nouvel user ? `ESSAIE LE USERNAME COMME PASSWORD` `user:user` `admin:admin`
- Tu n'arrives pas à cracker un password ? `ESSAIE LE USERNAME COMME PASSWORD`

## TRY ALTERNATE CRACKING TECHNIQUES

- Hashcat n'a pas marché ? T'as essayé avec des règles ? `ESSAIE JOHN, ESSAIE CRACKSTATION`
- John n'a pas marché ? `ESSAIE HASHCAT, ESSAIE CRACKSTATION`
- Crackstation n'a pas marché ? `ESSAIE HASHCAT, ESSAIE JOHN`

---

## Les 7 Pitfalls Courants

### Pitfall #1 : Enumération Superficielle

❌ Mauvais : Lancer Nmap une fois, passer à l'exploitation
✅ Bon : Énumérer tous les services, vérifier null sessions, chercher dans les shares

### Pitfall #2 : Oublier le Credential Harvesting

❌ Mauvais : Ignorer les fichiers de credentials
✅ Bon : **Toujours** vérifier :
- PowerShell history : `Get-History`
- Windows vault : `cmdkey /list`
- Fichiers de config : `grep -r "password" /etc/`
- Notes/sticky notes : `C:\Users\*\AppData\Local\...`

### Pitfall #3 : Mauvais Ordre d'Exploitation

❌ Mauvais : Passer 2h sur un service difficile, rater un share SMB facile
✅ Bon : Essayer le low-hanging fruit en premier (SMB, FTP, accès anonyme)

### Pitfall #4 : Pas de Screenshots

❌ Mauvais : Oublier de screenshot proof.txt, impossible de prouver la compromission
✅ Bon : Screenshot immédiatement : `whoami`, `id`, `proof.txt`

### Pitfall #5 : Mal Comprendre ce que Proof Requirement Veut Dire

❌ Mauvais : Shell root sur la machine, mais pas de proof.txt
✅ Bon : Lire `C:\Users\Administrator\Desktop\proof.txt` ET screenshot

### Pitfall #6 : Problèmes de Tunnel

❌ Mauvais : Tunnel qui ne marche pas, impossible d'atteindre le réseau AD interne
✅ Bon : Tester le tunnel tôt : `ping 172.16.x.x` depuis l'attaquant

### Pitfall #7 : Temps Perdu sur des Dead Ends

❌ Mauvais : Passer 4h sur un exploit non viable, rater une cible facile
✅ Bon : **Règle des 30 minutes** : si pas de progrès → changer de cible

---

## Mindset Shifts

**Quand bloqué :**
- "Quelle est la chose la plus simple que je n'ai pas encore essayée ?"
- Passer à une autre cible pendant 30 min
- Relancer des scripts d'enum pas encore vérifiés
- Chercher des fichiers de credentials potentiellement ratés

**Quand la confiance est basse :**
- Tu as passé des machines d'entraînement
- L'OSCP c'est la **méthodologie**, pas la perfection
- 70 points c'est passer (pas 100)
- Une machine entièrement compromise = au moins 30 points

**Quand frustré :**
- Pause 5 min (ne pas penser à l'exam)
- S'hydrater et manger
- Se rappeler pourquoi on a commencé l'OSCP
- Se concentrer sur ce qu'on **a** déjà accompli

---

## Gestion du Stress par Phase

**Premières 8h (Confiance Haute):**
- L'adrénaline est élevée
- Garder le momentum : ne pas s'attarder trop longtemps sur une chose
- Pauses : 5 min toutes les 30 min

**8h–16h (Le Doute s'Installe):**
- C'est normal
- Si bloqué >30 min → changer de cible
- Manger quelque chose de consistant
- Marcher 5 minutes

**16h–24h (Mentalité Finish Line):**
- Push final pour les points manquants
- Ne pas commencer de nouveaux exploits, finir ce qu'on a
- Se concentrer sur la documentation
- Vérifier que tous les screenshots existent
