# Offline Password Cracking

## Méthodologie

1. **Extraire les hashes** - dump DB, fichiers SAM/NTDS, fichiers de config, etc.
2. **Identifier le type de hash** - voir section ci-dessous
3. **Formater le hash** - vérifier que le format correspond à ce qu'attend l'outil (ex: `user:hash` vs hash seul)
4. **Estimer le temps de crack** - keyspace / hash rate. Si trop long → changer d'approche (cloud, règles ciblées)
5. **Préparer la wordlist** - muter la wordlist, appliquer des règles, chercher des leaks en ligne → [[04_wordlists]]
6. **Lancer l'attaque** - copier le hash avec soin (pas d'espace ou newline parasite) → [[02_hashcat]] / [[03_john]]

## Identifier un hash

```bash
hashid '<hash>'
hash-identifier '<hash>'
```

Exemples de formats courants :

| Hash | Longueur | Exemple |
|------|----------|---------|
| MD5 | 32 | `b08ff247dc7c5658ff64c53e8b0db462` |
| SHA1 | 40 | `da39a3ee5e6b4b0d3255bfef95601890afd80709` |
| SHA256 | 64 | `e3b0c44298fc1c149afb...` |
| NTLM | 32 | `31d6cfe0d16ae931b73c59d7e0c089c0` |
| bcrypt | - | `$2y$10$...` |
| SHA512crypt | - | `$6$salt$...` |

> `hashid` ne distingue pas toujours MD2/MD4/MD5 sur un hash de 32 chars - croiser avec [https://hashcat.net/wiki/doku.php?id=example_hashes](https://hashcat.net/wiki/doku.php?id=example_hashes)

## Chercher des fichiers de gestionnaires de mots de passe

Extensions ciblées → voir [[01_offline#Exemples]] pour le crack. : `.kdbx` (KeePass), `.db` (1Password legacy), `.agilekeychain`, `.opvault`, `.dashlane`, `.psafe3` (Password Safe), `.kwallet`

**PowerShell**
```powershell
# KeePass uniquement
Get-ChildItem -Path C:\ -Include *.kdbx -File -Recurse -ErrorAction SilentlyContinue

# Tous les gestionnaires
Get-ChildItem -Path C:\ -Include *.kdbx,*.db,*.agilekeychain,*.opvault,*.dashlane,*.psafe3,*.kwallet -File -Recurse -ErrorAction SilentlyContinue
```

**CMD**
```powershell
# KeePass uniquement
dir /s /b C:\*.kdbx 2>nul

# Tous les gestionnaires
dir /s /b C:\*.kdbx C:\*.db C:\*.agilekeychain C:\*.opvault C:\*.dashlane C:\*.psafe3 C:\*.kwallet 2>nul
```

**Linux**
```bash
# KeePass uniquement
find / -name "*.kdbx" 2>/dev/null

# Tous les gestionnaires
find / \( -name "*.kdbx" -o -name "*.db" -o -name "*.agilekeychain" -o -name "*.opvault" -o -name "*.dashlane" -o -name "*.psafe3" -o -name "*.kwallet" \) 2>/dev/null
```

## Exemples

### KeePass

1. Localiser le fichier → [[01_offline#Chercher des fichiers de gestionnaires de mots de passe]]

```bash
# 2. Convertir en hash crackable
keepass2john Database.kdbx > keepass.hash

# Supprimer le préfixe "Database:" ajouté par keepass2john
sed -i 's/^[^:]*://' keepass.hash
```

3. Identifier le mode → https://hashcat.net/wiki/doku.php?id=example_hashes

```bash
# 4. Cracker
hashcat -m 13400 keepass.hash /usr/share/wordlists/rockyou.txt -r /usr/share/hashcat/rules/rockyou-30000.rule --force
```

### SSH Private Key Passphrase

```bash
# 1. Convertir la clé en hash
ssh2john id_rsa > ssh.hash

# Supprimer le préfixe "id_rsa:" avant le hash
sed -i 's/^[^:]*://' ssh.hash
```

2. Identifier le mode → https://hashcat.net/wiki/doku.php?id=example_hashes

```bash
hashcat -h | grep -i ssh
# $6$ → mode 22921 (RSA/DSA/EC/OpenSSH - aes-256-ctr)
# Note: hashcat mode 22921 ne supporte pas aes-256-ctr → utiliser john
```

```bash
# 3. Préparer règles et wordlist
cat > ssh.rule << 'EOF'
[List.Rules:sshRules]
c $1 $3 $7 $!
c $1 $3 $7 $@
c $1 $3 $7 $#
EOF

# Ajouter les règles à john
sudo sh -c 'cat ssh.rule >> /etc/john/john.conf'
```

```bash
# 4. Cracker
hashcat -m 22921 ssh.hash ssh.passwords -r ssh.rule

# Si "Token length exception" (aes-256-ctr non supporté) → john
john --wordlist=ssh.passwords --rules=sshRules ssh.hash
```

```bash
# 5. Se connecter
chmod 600 id_rsa
ssh -i id_rsa -p 22 user@<target>
```

### Archives

```bash
# RAR
rar2john file.rar > rar_hashes.txt
john --wordlist=passwords.txt rar_hashes.txt

# ZIP
zip2john file.zip > zip_hashes.txt
john --wordlist=passwords.txt zip_hashes.txt

# ZIP Using fcrackzip
fcrackzip -u -D -p rockyou.txt recup.zip
```

### Shadow files

```bash
unshadow passwd shadow > shadowjohn.txt
john --wordlist=/usr/share/wordlists/rockyou.txt --rules shadowjohn.txt
john --show shadowjohn.txt

# Hashcat SHA512 $6$ shadow file
hashcat -m 1800 -a 0 hash.txt rockyou.txt --username

# Hashcat MD5 $1$ shadow file
hashcat -m 500 -a 0 hash.txt rockyou.txt --username
```

### Divers

```bash
# MD5 Apache webdav
hashcat -m 1600 -a 0 hash.txt rockyou.txt

# SHA1
hashcat -m 100 -a 0 hash.txt rockyou.txt --force

# Wordpress
hashcat -m 400 -a 0 --remove hash.txt rockyou.txt

# Cisco Type 5 (MD5)
hashcat -m 500 hash.txt rockyou.txt

# NTLMv2
john --format=netntlmv2 --wordlist=/usr/share/wordlists/rockyou.txt hash.txt
```

### TGS (Kerberoasting)

```bash
john --wordlist=/usr/share/wordlists/rockyou.txt --fork=4 --format=krb5tgs kerberos_hashes.txt
```
