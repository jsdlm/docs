
# Cassage de mots de passe

Se connecter à la crackstation @IP : 172.18.126.20
Ouvrir un terminal virtuel sur la crackstation
https://tmuxcheatsheet.com/

```bash
# Lister les terminaux virtuels tmux
tmux ls

# Créer un terminal virtuel avec tmux
tmux new -s mysession

# Quitter le terminal virtuel tmux sans fermer la session
Ctrl + B -> D 

# Ouvrir un terminal virtuel existant tmux
tmux a -t mysession

# Lancer hashcat
hashcat
```

Voir les résultats une fois fini

```bash
# Voir les résultats avec Hashcat
hashcat --show myhash.txt

# Voir les résultats avec John
john --show myhash.txt
```