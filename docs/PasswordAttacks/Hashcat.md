# Hashcat

# Usage

```
echo '2cb42f8734ea607eefed3b70af13bbd3' > hashes.txt
hashcat -a 0 -m 0 hashes.txt /usr/share/wordlists/rockyou.txt
```

# Options <a href="#options" id="options"></a>

```bash
-m # Hash type
-a # Attack mode
-r # Rules file
-V # Version
--status # Keep screen updated
-b # Benchmark
--runtime # Abort after X seconds
--session [text] # Set session name
--restore # Restore/Resume session
-o filename # Output to filename
--username # Ignore username field in a hash
--potfile-disable # Ignore potfile and do not write
--potfile-path # Set a potfile path
-d # Specify an OpenCL Device
-D # Specify an OpenCL Device Type
-l # List OpenCL Devices & Types
-O # Optimized Kernel, Passwords <32 chars
-i # Increment (bruteforce)
--increment-min # Start increment at X chars
--increment-max # Stop increment at X chars
```

# Attack modes <a href="#attack-modes" id="attack-modes"></a>

```bash
-a 0 # Straight : hash dict
-a 1 # Combination : hash dict dict
-a 3 # Bruteforce : hash mask
-a 6 # Hybrid wordlist + mask : hash dict mask
-a 7 # Hybrid mask + wordlist : hash mask dict
```

# Charsets <a href="#charsets" id="charsets"></a>

```bash
?l # Lowercase a-z
?u # Uppercase A-Z
?d # Decimals
?h # Hex using lowercase chars
?H # Hex using uppercase chars
?s # Special chars
?a # All (l,u,d,s)
?b # Binary
```

# Hash type

Identifier le type de hash

```
hashid 2cb42f8734ea607eefed3b70af13bbd3
```

[https://hashcat.net/wiki/doku.php?id=example\_hashes](https://hashcat.net/wiki/doku.php?id=example_hashes)

# Examples <a href="#examples" id="examples"></a>

```bash
# Benchmark MD4 hashes
hashcat -b -m 900

# Create a hashcat session to hash Kerberos 5 tickets using wordlist
hashcat -m 13100 -a 0 --session crackin1 hashes.txt wordlist.txt -o output.pot

# Crack MD5 hashes using all char in 7 char passwords
hashcat -m 0 -a 3 -i hashes.txt ?a?a?a?a?a?a?a -o output.pot

# Crack SHA1 by using wordlist with 2 char at the end 
hashcat -m 100 -a 6 hashes.txt wordlist.txt ?a?a -o output.pot

# Crack WinZip hash using mask (Summer2018!)
hashcat -m 13600 -a 3 hashes.txt ?u?l?l?l?l?l?l?d?d?d?d! -o output.pot

# Crack MD5 hashes using dictionnary and rules
hashcat -a 0 -m 0 example0.hash example.dict -r rules/best64.rules

# Crack MD5 using combinator function with 2 dictionnaries
hashcat -a 1 -m 0 example0.hash example.dict example.dict

# Cracking NTLM hashes
hashcat64 -m 1000 -a 0 -w 4 --force --opencl-device-types 1,2 -O d:\hashsample.hash "d:\WORDLISTS\realuniq.lst" -r OneRuleToRuleThemAll.rule

# Cracking hashes from kerberoasting
hashcat64 -m 13100 -a 0 -w 4 --force --opencl-device-types 1,2 -O d:\krb5tgs.hash d:\WORDLISTS\realhuman_phill.txt -r OneRuleToRuleThemAll.rule
```
