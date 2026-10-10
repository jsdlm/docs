> Résolution d'API sans import suspecte
## Le probleme avec GetProcAddress

Quand un PE est chargé en mémoire, Windows construit l'**IAT** (Import Address Table) : la liste de toutes les fonctions que le binaire importe depuis des DLL externes. Un EDR ou un analyste peut lire cette table **statiquement** (sans exécuter le binaire) et voir exactement ce qu'il utilise.

Le code original faisait :
```cpp
GetProcAddress(GetModuleHandleA("kernel32.dll"), "WriteProcessMemory")
```

C'est de la résolution dynamique — `WriteProcessMemory` n'apparait pas dans l'IAT. Mais `GetProcAddress` et `GetModuleHandleA` **elles-mêmes** y apparaissent. Et un binaire qui importe `GetProcAddress` c'est un signal fort : il essaie de cacher ses vrais appels.

## Le PEB — Process Environment Block

Chaque processus Windows possède une structure interne appelée **PEB**. Elle est accessible directement via un registre CPU :
- **x64** : `gs:[0x60]`
- **x86** : `fs:[0x30]`

Pas besoin d'appeler une API — c'est une lecture mémoire brute, invisible pour un EDR.

Le PEB contient un pointeur vers le **Ldr** (loader data), qui maintient une liste chaînée de tous les modules (DLL) chargés dans le processus.

## Structure en mémoire

```
CPU Register (gs:0x60)
 └─ PEB
     └─ Ldr (PEB_LDR_DATA)  [offset 0x18 sur x64, 0x0C sur x86]
         └─ InMemoryOrderModuleList (liste chaînée doublement liée)
              ├─ ntdll.dll      → DllBase, BaseDllName
              ├─ kernel32.dll   → DllBase, BaseDllName
              ├─ kernelbase.dll → DllBase, BaseDllName
              └─ ...
```

Chaque entrée de la liste contient :
- `BaseDllName` — le nom du module (en Unicode)
- `DllBase` — l'adresse de base en mémoire (= ce que retourne GetModuleHandle)

## peb_get_module — remplace GetModuleHandleA

```
1. Lire le PEB via gs:0x60
2. Suivre le pointeur Ldr → InMemoryOrderModuleList
3. Parcourir la liste chainee
4. Pour chaque entree, comparer BaseDllName avec le nom cherché
5. Si match → retourner DllBase (= HMODULE)
```

Résultat : on obtient l'adresse de base de kernel32.dll (ou ntdll.dll, etc.) **sans aucun appel d'API**.

## peb_get_function — remplace GetProcAddress

Une fois qu'on a l'adresse de base d'un module, on peut parser sa structure PE pour trouver ses exports :

```
DllBase (HMODULE)
 └─ DOS Header
     └─ e_lfanew → NT Headers
         └─ OptionalHeader.DataDirectory[IMAGE_DIRECTORY_ENTRY_EXPORT]
              └─ IMAGE_EXPORT_DIRECTORY
                   ├─ AddressOfNames     — tableau des noms de fonctions (char*)
                   ├─ AddressOfNameOrdinals — ordinal de chaque nom
                   └─ AddressOfFunctions — tableau des RVA de chaque fonction
```

```
1. Parser le DOS header → NT headers → Export Directory
2. Parcourir AddressOfNames
3. Pour chaque nom, strcmp() avec le nom cherche
4. Si match → lire l'ordinal correspondant → lire le RVA dans AddressOfFunctions
5. Retourner DllBase + RVA = adresse absolue de la fonction
```

C'est exactement ce que fait `GetProcAddress` en interne — on refait la même chose nous-mêmes.

## Avant / Après dans l'IAT

```
AVANT (visible dans l'IAT)          APRES (visible dans l'IAT)
──────────────────────────          ──────────────────────────
kernel32.dll:                       kernel32.dll:
  GetProcAddress        ← suspect    CreateMutexA
  GetModuleHandleA      ← suspect    (... fonctions non-suspectes)
  CreateMutexA
  ...

Fonctions sensibles resolues       Fonctions sensibles resolues
dynamiquement via GetProcAddress    dynamiquement via PEB walk
(invisible dans l'IAT mais          (invisible dans l'IAT ET
GetProcAddress trahit l'intention)  rien ne trahit l'intention)
```

## Limites

- Les fonctions "normales" appelées directement (CreateMutex, ShellExecute, etc.) restent dans l'IAT — c'est OK, elles ne sont pas suspectes
- `strcmp` et `_wcsicmp` (CRT) restent dans l'IAT — c'est inoffensif
- Le PEB walk ne contourne pas les **hooks EDR** sur les fonctions elles-mêmes — pour ça il faut des **syscalls directs** (phase suivante)
