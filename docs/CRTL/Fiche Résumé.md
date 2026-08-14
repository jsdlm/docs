# Architecture d'un payload CS

```
[ Shellcode Runner ] + [ Loader | Beacon DLL ]
```

**Shellcode Runner (Artifact)** : PE classique visible sur le disque. Son seul rôle est d'extraire le blob, l'allouer en mémoire et sauter dessus. Modifié via l'**Artifact Kit**.

**Loader** : charge la Beacon DLL depuis la mémoire sans passer par le Windows loader. Remplacé par **Crystal Palace** dans le CRTL. Son comportement est aussi partiellement contrôlé par le bloc `stage {}` de Malleable C2.

**Beacon DLL** : l'implant lui-même. Modifié via **Malleable C2** (signatures, comportements...).

---

# Les trois cas d'exécution

**Cas 1 — Double-clic sur .exe CS**

```
Windows loader → Shellcode runner → Loader → Beacon DLL
```

**Cas 2 — spawn/inject depuis Beacon existant**

```
Beacon injecte le blob → Loader → Beacon DLL
```

**Cas 3 — Dropper/injecteur custom (process hollowing...)**

```
Ton dropper → injecte le blob → Loader → Beacon DLL
```

---

# Terminologie clarifiée

|Terme|Définition|
|---|---|
|Shellcode runner|Code qui livre et exécute le blob. Artifact Kit ou ton dropper custom|
|Dropper|Programme qui en délivre un autre (télécharge, extrait...)|
|Injecteur|Code qui injecte un payload dans un processus (process hollowing, injection classique...)|
|Loader réflectif|Code qui charge une DLL depuis la mémoire sans Windows loader|
|Blob / Shellcode (.bin)|Loader + Beacon DLL combinés, format brut|
|PICO|Position-Independent Code Object — Crystal Palace|
|PIC|Position-Independent Code — code sans adresses fixes|

---

# Ce que fait chaque outil

|Outil|Cible|Objectif|
|---|---|---|
|Artifact Kit|Shellcode runner|Bypass AV statique (signatures sur le disque)|
|Crystal Palace|Loader réflectif|Bypass EDR en mémoire|
|Malleable C2 `stage {}`|Loader + Beacon DLL|Modifier comportement du loader et signatures de Beacon|
|Malleable C2 `post-ex {}`|DLLs post-ex + leur loader|Modifier comportements et signatures post-ex|
|Malleable C2 `process-inject {}`|Comportement d'injection de Beacon|Contrôler méthodes et permissions d'injection|
|ThreatCheck|Shellcode runner|Identifier les signatures détectées par Defender|

**Important** : quand Crystal Palace est utilisé, il remplace entièrement le loader — les options `stage {}` de Malleable C2 qui concernent le loader deviennent caduques. C'est pour ça qu'on configure un bloc `stage {}` minimal qui désactive ces fonctionnalités au début du CRTL.

---

# Couches de détection et bypasses

```
Sur le disque
  → AV scanne le shellcode runner
    → Bypass : Artifact Kit (modifier le code compilé)
    → Bypass : Obfuscation, signature numérique, LOLBAS

En mémoire au chargement (load-time)
  → EDR détecte l'allocation mémoire suspecte, le chargement de DLLs
    → Bypass : Crystal Palace loader custom

En mémoire à l'exécution (runtime)
  → EDR analyse la call stack, scanne la mémoire pendant le sleep
    → Bypass : Call stack spoofing, indirect syscalls, memory obfuscation

Au niveau kernel
  → Callbacks kernel (création processus, handles, registre), ETW-TI
    → Bypass : BYOVD (driver vulnérable) pour désactiver les callbacks
```

---

# Windows internals essentiels

**Kernel (ring 0)** : `ntoskrnl.exe`, premier programme au boot, accès total au matériel, espace partagé entre tous les drivers. Un crash = BSOD.

**User mode (ring 3)** : toutes les applications normales, espace mémoire isolé par processus. Un crash n'affecte que le processus.

**Syscall** : instruction CPU qui fait passer du ring 3 au ring 0. Chaque syscall a un numéro (SSN) référencé dans la SSDT.

**Windows loader** : code dans `ntdll.dll` qui charge les PE en mémoire, résout les imports, remplit l'IAT, puis saute au point d'entrée.

---

# Format PE
![](img/Pasted%20image%2020260813144222.png)

```
[ DOS Header ]      e_magic (MZ), e_lfanew (offset vers NT headers)
[ DOS Stub ]        "This program cannot be run in DOS mode"
[ NT Headers ]
    [ PE Signature ] PE\0\0
    [ File Header ]  Architecture, nombre de sections
    [ Optional Header ] ImageBase, AddressOfEntryPoint, DataDirectory
[ Sections ]
    .text   → code exécutable (RX)
    .data   → variables globales initialisées (RW)
    .rdata  → données read-only, IAT (R)
    .rsrc   → ressources, métadonnées de version (R)
    .bss    → variables non initialisées (RW)
```

**IAT (Import Address Table)** : dans `.rdata`, remplie par le Windows loader au démarrage avec les adresses réelles des fonctions importées. Cible du IAT hooking par les EDR.

> Un stub c'est un **petit bout de code minimal** dont le seul rôle est de faire une chose très précise et de passer la main à autre chose.

---

# Techniques d'évasion (résumé)

**IAT Hooking (EDR)** : l'EDR remplace les adresses dans l'IAT pour intercepter les appels API.

**Inline Hooking (EDR)** : l'EDR écrase les premières instructions d'une fonction dans ntdll pour rediriger vers son code.

**Direct syscalls** : appel direct au kernel sans passer par ntdll hookée. Détectable via call stack anormale.

**Indirect syscalls** : même principe mais on saute vers l'instruction syscall dans ntdll → call stack légitime.

**Unhooking** : remplacer la section `.text` de ntdll en mémoire par une copie propre lue depuis le disque.

**Hell's/Halo's/Tartarus' Gate** : résolution dynamique des SSN même si les fonctions sont hookées.

**Call stack spoofing** : pousser de faux frames sur la stack pour cacher l'origine d'un appel API.

**API proxying** : déléguer un appel API à un thread Windows légitime (TpAllocWork...).

**Memory obfuscation** : chiffrer la mémoire de Beacon pendant le sleep + passer les permissions de RX à RW.

**BYOVD** : charger un driver vulnérable signé pour accéder au kernel et désactiver callbacks + ETW-TI.

---

# Kernel callbacks (EDR)

|Callback|Rôle EDR|Désactivation|
|---|---|---|
|PsSetCreateProcessNotifyRoutineEx|Bloquer/surveiller création de processus|Écraser le pointeur avec 0 dans la table|
|ObRegisterCallbacks|Retirer des droits sur les handles (ex: LSASS)|Mettre le champ `Active` à 0|
|CmRegisterCallbackEx|Bloquer opérations registre|Déconnecter le nœud de la liste chaînée|
|ETW-TI|Surveillance kernel des opérations mémoire|Mettre `IsEnabled` à 0|

---

# App Control (WDAC)

**Enforced par le kernel** — plus robuste qu'AppLocker.

**Misconfigurations exploitables** :

- Politique en mode audit → pas bloquant
- Règles par attributs fichier → compiler un binaire avec les bons attributs
- Wildcards de chemins → déposer dans un dossier autorisé
- LOLBAS → Microsoft.Workflow.Compiler, MSBuild...
- ADCS → enroller un certificat de code signing si template accessible

**Weaponisation avec admin local** :

- Politique supplémentaire → whitelist tes outils
- Politique de base deny-only → blacklist l'AV/EDR au prochain reboot

---

# Credential Guard

Isole les secrets (hashes NTLM, TGTs) dans une enclave virtuelle `LSAIso.exe`. LSA n'a plus accès aux secrets, seulement à des handles.

**Ce qui ne fonctionne plus** : Mimikatz sekurlsa, Rubeus dump, unconstrained delegation, S4U abuse.

**Ce qui fonctionne encore** :

- Service tickets en cache → dump + pass-the-ticket
- `Rubeus asktgs /luid` → demande via LSA sans toucher au TGT
- Mot de passe en clair → `asktgt /password` direct au KDC
- Certificats PKINIT → SharpDPAPI + `asktgt /certificate`

# Loaders

## Stomped Loader

![](img/Pasted%20image%2020260813144048.png)

### Le problème de base

Une DLL normale ne peut pas s'exécuter depuis la mémoire seule — elle a besoin du Windows loader pour résoudre ses imports, mapper ses sections, etc. Le loader réflectif résout ça en embarquant cette logique directement dans la DLL.

### Comment ça fonctionne

**1. La DLL exporte `ReflectiveLoader`** C'est une fonction dans la section `.text` qui contient toute la logique pour se recharger elle-même en mémoire — mapper les sections, résoudre les imports, appliquer les relocations, appeler le point d'entrée. Elle réimplémente manuellement ce que le Windows loader fait normalement.

**2. Le stub shellcode dans le DOS Header** Quand CS génère le blob, il écrase les premiers octets de la DLL (le DOS Header) avec un petit stub assembleur. Ce stub a un seul rôle : trouver et appeler `ReflectiveLoader`.

Pourquoi écraser le DOS Header ? Parce que quand le blob est injecté en mémoire et qu'on saute au début, il faut exécuter quelque chose immédiatement. Le DOS Header d'origine ne contient rien d'utile — autant le remplacer par du code exécutable.

**3. Séquence d'exécution**

```
Blob injecté en mémoire
  → on saute au début du blob
    → stub shellcode s'exécute
      → trouve ReflectiveLoader dans .text
        → ReflectiveLoader s'exécute
          → mappe une copie propre de la DLL en mémoire
            → résout les imports
              → applique les relocations
                → appelle DllMain → Beacon démarre
```

### Les problèmes

- Le DOS Header est corrompu → signature détectable
- La DLL doit obligatoirement exporter `ReflectiveLoader` → signature connue
- Le loader est lié à cette DLL spécifique — il ne peut pas charger autre chose
- Peu de flexibilité pour obfusquer la DLL car le loader doit connaître sa structure exacte

---

## Prepended Loader

![](img/Pasted%20image%2020260813144104.png)

### Le principe

Le loader est un blob PIC complètement indépendant, placé **avant** la DLL. Les deux ne se mélangent pas.

### Comment ça fonctionne

**1. Structure du blob**

```
[ Loader PIC ] [ Beacon DLL intacte ]
     ↑                  ↑
  exécuté en       jamais touchée
    premier
```

**2. Le loader sait où est la DLL** Comme on l'a vu avec Crystal Palace, le loader a un marqueur (`_DLL_`) qui pointe vers ce qui est collé juste derrière lui en mémoire. Il sait donc exactement où commence la DLL Beacon.

**3. La DLL peut être transformée** Avant d'être collée au loader, la DLL peut être chiffrée, compressée, encodée — peu importe. Le loader sait comment la décoder avant de la charger. C'est impossible avec le stomped loader car le loader est dans la DLL elle-même et doit pouvoir s'exécuter directement.

**4. Séquence d'exécution**

```
Blob injecté en mémoire
  → on saute au début du blob
    → Loader PIC s'exécute
      → trouve la DLL collée derrière lui
        → décode/déchiffre si nécessaire
          → parse les headers PE de la DLL
            → alloue de la mémoire
              → mappe les sections
                → résout les imports
                  → applique les relocations
                    → appelle DllMain → Beacon démarre
```

**5. La DLL reste intacte** Le DOS Header n'est pas touché. Beacon n'a pas besoin d'exporter quoi que ce soit. Vu de l'extérieur la DLL ressemble à une DLL Windows normale.

### Les avantages concrets

- Pas de DOS Header corrompu → moins de signatures
- Pas de `ReflectiveLoader` exporté → moins de signatures
- La DLL peut être chiffrée → les scanners mémoire ne trouvent rien pendant le sleep
- Le loader est réutilisable pour n'importe quelle DLL — c'est pour ça que Crystal Palace peut charger aussi bien Beacon que les DLLs post-ex avec le même code

---

## Comparaison visuelle

```
Stomped loader :
┌─────────────────────────────────────────┐
│ [Stub shellcode] [.text avec            │
│  ReflectiveLoader + code Beacon]        │
│ [.data] [.rdata] [...]                  │
└─────────────────────────────────────────┘
  ↑ tout dans un seul blob, DOS Header écrasé

Prepended loader :
┌──────────────┐ ┌─────────────────────────┐
│  Loader PIC  │ │  Beacon DLL intacte     │
│  (Crystal    │ │  [DOS Header]           │
│   Palace)    │ │  [NT Headers]           │
│              │ │  [.text] [.data] [...] │
└──────────────┘ └─────────────────────────┘
  ↑ deux blobs séparés collés ensemble
```


# Etapes Windows loader

**Étape 0 — Le kernel crée le processus**  
Avant même que le loader intervienne, le kernel crée un processus vide avec son propre espace mémoire virtuel et charge `ntdll.dll` dedans — c'est la seule DLL chargée par le kernel lui-même. Le loader (`LdrInitializeThunk`) qui est dans `ntdll.dll` prend ensuite le relais entièrement en user mode.

**Étape 1 — Lire les headers du PE**  
Le loader lit le DOS header → suit `e_lfanew` → trouve les NT headers → lit l'Optional Header pour récupérer `ImageBase`, `AddressOfEntryPoint`, `SizeOfImage`, et le tableau `DataDirectory`.

**Étape 2 — Mapper l'image en mémoire**  
Le loader alloue un bloc de mémoire de la taille de `SizeOfImage`. Il copie ensuite chaque section à son `VirtualAddress` (son RVA) avec les bonnes permissions :

- `.text` → RX (Read + Execute)
- `.data` → RW (Read + Write)
- `.rdata` → R (Read seul)

**Étape 3 — Enregistrer le module dans le PEB**  
Le loader ajoute le module aux trois listes chaînées dans `PEB_LDR_DATA` :

- `InLoadOrderModuleList`
- `InMemoryOrderModuleList`
- `InInitializationOrderModuleList`

C'est ce qui rend le module visible aux outils comme Process Explorer. Un module chargé manuellement sans passer par le loader n'apparaît pas ici — c'est la base de la détection par forensique mémoire.

**Étape 4 — Résoudre les imports**  
Le loader lit l'Import Directory. Pour chaque DLL listée :

- Si la DLL est déjà en mémoire → il récupère son adresse directement
- Si elle n'est pas encore en mémoire → il la charge depuis le disque (récursivement, en recommençant depuis l'étape 1 pour cette DLL)

Ensuite pour chaque fonction importée, il trouve son adresse réelle et l'écrit dans le slot IAT correspondant. Après cette étape l'IAT est entièrement remplie.

**Étape 5 — Appliquer les relocations**  
Le loader compare l'adresse réelle de chargement avec `ImageBase`. Si elles diffèrent (ce qui est quasiment toujours le cas avec l'ASLR), il lit la section `.reloc` qui liste tous les endroits dans le PE qui contiennent des adresses absolues, et ajoute le delta à chacun.

**Étape 6 — Exécuter les TLS callbacks**  
Si le PE a des TLS callbacks (dans le TLS Directory), ils sont appelés avant le point d'entrée. Utilisés par certains malwares pour exécuter du code avant qu'un débogueur puisse intercepter.

**Étape 7 — Appeler le point d'entrée**  
Le loader saute à `AddressOfEntryPoint`. Pour un `.exe` c'est le start thunk du runtime C qui finit par appeler ton `main()`. Pour une DLL c'est `DllMain` appelé avec `DLL_PROCESS_ATTACH`.

**En résumé visuel**

```
Kernel crée le processus + charge ntdll
  → Loader lit les headers PE
    → Mappe les sections en mémoire avec les bonnes permissions
      → Enregistre le module dans le PEB
        → Résout les imports (charge les DLLs dépendantes si nécessaire)
          → Remplit l'IAT avec les adresses réelles
            → Applique les relocations si nécessaire
              → Exécute les TLS callbacks
                → Saute au point d'entrée
```