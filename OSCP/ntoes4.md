### [[21 - FTP]]

[](https://github.com/intotheewild/OSCP-Checklist/blob/main/02.%20Footholds.md#21---ftp)

- Check version using `searchsploit` for public exploits
- Check for `anonymous` login
- Check for hints within the directory (i.e. `minniemouse.exe`)
- Download the directory `wget -m ftp://anonymous:anonymous@192.168.215.245`
- Check if there's anything that points towards uploads going to the web directory

### [[80 - WEB]]

[](https://github.com/intotheewild/OSCP-Checklist/blob/main/02.%20Footholds.md#80---web)

- Check version using `searchsploit` for public exploits (Traversal, SQLi, RCE)
- Check to see if anything else is running using `whatweb http://10.10.10.10` (searchsploit, wordpress)
- Fully enumerate with directory brute-forcing
    - Run multiple tools and check for file extensions, try from deeper directories
- Visit site in the browser and look for any context clues
    - See if there's any hint for FQDN and put it in `/etc/hosts`
    - See if there's any hints to valid users or software in pages or source code
- Test everything for default credentials or username being the password

### [[161 - SNMP]]

[](https://github.com/intotheewild/OSCP-Checklist/blob/main/02.%20Footholds.md#161---snmp)

- Enumerate community strings on v1 and v2
    - `sudo nmap -sU -p 161 --script snmp-brute 192.168.194.149`
- Try to get useful information from accessible communities
    - `snmpwalk -v 1 -c public 192.168.194.149 NET-SNMP-EXTEND-MIB::nsExtendObjects`
    - `snmpwalk -v2c -c public 192.168.194.149 | grep <string>`