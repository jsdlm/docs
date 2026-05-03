# John

## Cracking Modes <a href="#cracking-modes" id="cracking-modes"></a>

```bash
# Dictionnary attack
./john --wordlist=password.lst hashFile

 # Dictionnary attack using default or specific rules
./john --wordlist=password.lst --rules=rulename hashFile
./john --wordlist=password.lst --rules mypasswd

# Incremental mode
./john --incremental hashFile

# Loopback attack (password are taken from the potfile)
./john --loopback hashFile

# Mask bruteforce attack
./john --mask=?1?1?1?1?1?1 --1=[A-Z] hashFile --min-len=8

# Dictionnary attack using masks
./john --wordlist=password.lst -mask='?l?l?w?l' hashFile
```

