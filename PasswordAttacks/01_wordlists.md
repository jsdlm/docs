# Wordlists

```bash
cd /usr/share/wordlists/
sudo gzip -d rockyou.txt.gz
/usr/share/wordlists/rockyou.txt
   
/usr/share/wordlists
├── dirb -> /usr/share/dirb/wordlists
├── dirbuster -> /usr/share/dirbuster/wordlists
├── dnsmap.txt -> /usr/share/dnsmap/wordlist_TLAs.txt
├── fasttrack.txt -> /usr/share/set/src/fasttrack/wordlist.txt
├── fern-wifi -> /usr/share/fern-wifi-cracker/extras/wordlists
├── john.lst -> /usr/share/john/password.lst
├── legion -> /usr/share/legion/wordlists
├── metasploit -> /usr/share/metasploit-framework/data/wordlists
├── nmap.lst -> /usr/share/nmap/nselib/data/passwords.lst
├── rockyou.txt
├── sqlmap.txt -> /usr/share/sqlmap/data/txt/wordlist.txt
├── wfuzz -> /usr/share/wfuzz/wordlist
└── wifite.txt -> /usr/share/dict/wordlist-probable.txt
```

- [SecLists - The Pentester’s Companion](https://github.com/danielmiessler/SecLists)
- [Probable Wordlists](https://github.com/berzerk0/Probable-Wordlists)
- [WordList Compendium](https://github.com/Dormidera/WordList-Compendium)
- [Jhaddix Content Discovery All](https://gist.github.com/jhaddix/b80ea67d85c13206125806f0828f4d10)
- [Google Fuzzing Forum](https://github.com/google/fuzzing)
- [CrackStation’s Password Cracking Dictionary](https://crackstation.net/crackstation-wordlist-password-cracking-dictionary.htm)

## Default Credentials

- [DefaultPassword](https://default-password.info/)
- [CIRT.net Password DB](https://www.cirt.net/passwords)
- [Default Router Passwords List](https://192-168-1-1ip.mobi/default-router-passwords-list/)

**Note:** [SecLists](https://github.com/danielmiessler/SecLists) and [WordList Compendium](https://github.com/Dormidera/WordList-Compendium) also include default passwords lists.

## Wordlist Generation

#### CeWL

```sh
cewl example.com -m 3 -w wordlist.txt
```

Parameters

- `-m <length>`: Minimum word length.
- `-w <file>`: Write the output to `<file>`.

#### Crunch

Simple wordlist.

```sh
crunch 6 12 abcdefghijk1234567890\@\! -o wordlist.txt
```

String permutation.

```sh
crunch 1 1 -p target pass 2019 -o wordlist.txt
```

Patterns.

```sh
crunch 9 9 0123456789 -t @target@@ -o wordlist.txt
```

Parameters

- `<min-len>`: The minimum string length.
- `<max-len>`: The maximum string length.
- `<charset>`: Characters set.
- `-o <file>`: Specifies the file to write the output to.
- `-p <charset or strings>`: Permutation.
- `-t <pattern>`: Specifies a pattern, eg: `@@pass@@@@`.
    - `@` will insert lower case characters
    - `,` will insert upper case characters
    - `%` will insert numbers
    - `^` will insert symbols