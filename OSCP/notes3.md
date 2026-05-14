## 🔍 Enumeration Methodology

[](https://github.com/jeffaf/oscp-prep-checklist#-enumeration-methodology)

### Initial Scan

[](https://github.com/jeffaf/oscp-prep-checklist#initial-scan)

1. [ ]  Full port scan: `nmap -p- --min-rate 1000 <target>`
2. [ ]  Service scan on open ports: `nmap -sC -sV -p <ports> <target>`
3. [ ]  Check for low-hanging fruit: anonymous FTP, SMB null sessions, default creds

### Web (80/443)

[](https://github.com/jeffaf/oscp-prep-checklist#web-80443)

1. [ ]  Browse manually first and check source code
2. [ ]  Directory bust with feroxbuster/gobuster
3. [ ]  Check for CMS (WordPress, Drupal, etc.) and run specific scanners
4. [ ]  Test for SQLi, LFI, file upload vulns
5. [ ]  Check `/robots.txt`, `/.git/`, /backup/, and /api

### SMB (139/445)

[](https://github.com/jeffaf/oscp-prep-checklist#smb-139445)

1. [ ]  Null session: `netexec smb <target> -u '' -p ''`
2. [ ]  List shares: `smbclient -L //<target>/ -N`
3. [ ]  Check for read/write access on shares
4. [ ]  Enum users: `enum4linux -a <target>`

### Active Directory

[](https://github.com/jeffaf/oscp-prep-checklist#active-directory)

1. [ ]  Get domain info: `ldapsearch` or `enum4linux`
2. [ ]  Find users: kerbrute [https://github.com/ropnop/kerbrute](https://github.com/ropnop/kerbrute)
3. [ ]  Find SPNs for Kerberoasting
4. [ ]  Check for AS-REP roastable users
5. [ ]  BloodHound if you have creds