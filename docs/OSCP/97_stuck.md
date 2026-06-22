# Bloqué

- Relire le scan nmap : ports inconnus -> nc / telnet
- énumérer tous les services, vérifier les null sessions, explorer les shares
- Commencer par le low-hanging fruit (SMB, FTP, accès anonyme)
- Relancer les scripts d'énumération pas encore vérifiés
- Chercher des fichiers de credentials potentiellement manqués
- Creds par défaut sur le service ?
- Nouvel utilisateur trouvé → l'ajouter à `users.txt`
- Nouveau mot de passe trouvé (ou quelque chose qui pourrait en être un) → l'ajouter à `passwords.txt`
- Sprayer sur tous les services : FTP, SSH, SMB, Kerberos, consoles d'administration, tout service acceptant des credentials
- Quelle est la chose la plus simple que je n'ai pas encore essayée ?
- règle des 30 minutes — si aucun progrès, changer de cible
