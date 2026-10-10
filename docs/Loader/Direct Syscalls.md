### Le problème actuel

Quand ton code appelle `WriteProcessMemory`, voici ce qui se passe :

```
Ton code (loader.exe)
  → kernel32.dll!WriteProcessMemory      ← wrapper haut niveau
    → ntdll.dll!NtWriteVirtualMemory     ← prépare le syscall
      → instruction "syscall"            ← transition vers le kernel
        → noyau Windows                  ← exécution réelle
```

L'EDR pose ses **hooks dans ntdll.dll** — il remplace les premiers octets de `NtWriteVirtualMemory` par un `jmp` vers son propre code. Quand ton appel arrive dans ntdll, l'EDR intercepte, inspecte les paramètres (quel processus ? quelle mémoire ? quelles permissions ?), et décide de bloquer ou laisser passer.

Le PEB walk qu'on a fait contourne les hooks sur **kernel32** (on ne passe plus par `GetProcAddress`), mais l'appel finit toujours dans **ntdll** où l'EDR attend.

### Ce que fait un syscall direct

Au lieu de passer par ntdll, on exécute l'instruction `syscall` nous-mêmes :

```
AVANT (via ntdll — hookable) :
  ton code → kernel32 → ntdll (HOOK EDR ICI) → syscall → kernel

APRES (syscall direct — pas de hook) :
  ton code → syscall → kernel
```

Concrètement, `NtWriteVirtualMemory` dans ntdll fait juste ça :

```asm
mov r10, rcx              ; convention d'appel syscall
mov eax, 0x3A             ; numéro du syscall (SSN)
syscall                   ; transition vers le kernel
ret
```

C'est tout — 4 instructions. Si on fait la même chose dans notre code, on saute ntdll complètement et l'EDR ne voit rien.

### Le SSN (System Service Number)

Chaque fonction ntdll a un **numéro de syscall** (SSN) — le `0x3A` dans l'exemple. Le problème : ce numéro **change entre les versions de Windows**. `NtWriteVirtualMemory` peut être `0x3A` sur Windows 10 21H2 et `0x3B` sur Windows 11 23H2.

Pour trouver le bon SSN au runtime, on peut :
- **Lire les octets de ntdll en mémoire** — même si la fonction est hookée, le SSN est souvent encore lisible quelques octets plus loin
- **Trier les exports ntdll** — les SSN sont attribués dans l'ordre alphabétique des `Nt*` exports (technique "Hell's Gate" / "Halo's Gate")

### Direct vs Indirect

**Syscall direct** : on exécute `syscall` depuis notre propre code. Problème : certains EDR vérifient que l'instruction `syscall` vient bien de ntdll (vérification de l'adresse de retour).

**Syscall indirect** : on saute au milieu de la vraie fonction ntdll, juste sur l'instruction `syscall`. L'adresse de retour pointe vers ntdll → l'EDR est satisfait.

```
Direct :    ton code → mov eax,SSN → syscall (depuis ton .exe)     ← détectable
Indirect :  ton code → mov eax,SSN → jmp ntdll!syscall_instruction ← furtif
```

### Ce qu'on va implémenter

Les fonctions à remplacer par des syscalls (celles qui déclenchent les alertes Elastic) :

| Win32 API | Fonction ntdll | Alerte actuelle |
|-----------|---------------|-----------------|
| `WriteProcessMemory` | `NtWriteVirtualMemory` | Remote Memory Write |
| `QueueUserAPC` | `NtQueueApcThread` | Injection via APC |
| `VirtualAllocEx` | `NtAllocateVirtualMemory` | — |
| `VirtualProtectEx` | `NtProtectVirtualMemory` | — |
| `CreateProcessA` | `NtCreateUserProcess` (ou garder) | — |
| `ResumeThread` | `NtResumeThread` | — |
