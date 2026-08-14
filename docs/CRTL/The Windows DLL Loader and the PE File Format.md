
Tout exécutable et toute DLL sur Windows partagent un même format de fichier sur disque : le Portable Executable (PE). Quand tu double-cliques sur un programme ou qu'un processus charge une bibliothèque, le Windows loader lit ce fichier PE, le mappe en mémoire, connecte les fonctions dont il dépend, et saute finalement à son point d'entrée. Comprendre la structure du PE et ce que le loader en fait est fondamental pour le reverse engineering, le débogage de problèmes de chargement, et le raisonnement sur une grande famille de techniques d'injection et de hijacking. Cet article parcourt la structure PE champ par champ, puis suit le loader qui transforme un fichier sur disque en code exécutable.

---
# Structure du fichier PE

Un fichier PE commence, pour des raisons historiques, par un DOS header. Ses deux premiers octets sont les caractères ASCII MZ (les initiales de Mark Zbikowski), suivi d'un petit DOS stub — le petit programme qui affiche "This program cannot be run in DOS mode." Le seul champ du DOS header qui compte encore est `e_lfanew`, un offset dans le fichier pointant vers le vrai header.

À cet offset se trouve la PE signature (`PE\0\0`), immédiatement suivie du COFF File Header (type de machine, nombre de sections, timestamp, caractéristiques) et de l'Optional Header — qui, malgré son nom, est obligatoire pour les images. L'Optional Header contient les champs qui intéressent le plus le loader :

- **ImageBase** — l'adresse virtuelle préférée à laquelle l'image veut être chargée.
- **AddressOfEntryPoint** — le RVA de la première instruction à exécuter (le start thunk d'un EXE, ou le DllMain d'une DLL).
- **SectionAlignment et FileAlignment** — comment les sections sont alignées en mémoire versus sur le disque.
- **Le tableau Data Directory** — une table de paires (RVA, taille) localisant la table d'imports, la table d'exports, la table de relocations, les ressources, le répertoire TLS, et plus encore.

Après les headers viennent les section headers puis les sections elles-mêmes : `.text` (code exécutable), `.data` (données initialisées modifiables), `.rdata` (données en lecture seule, incluant les tables d'imports et d'exports), `.rsrc` (ressources), et `.reloc` (relocations de base). Presque toutes les adresses dans un PE sont exprimées en RVA (Relative Virtual Address) — un offset depuis la base de l'image une fois chargée — plutôt qu'en adresse absolue, précisément pour que l'image puisse être placée n'importe où en mémoire.

---

# Imports et l'IAT

Presque aucun programme n'est autonome — il appelle des fonctions dans d'autres DLLs. L'Import Directory liste chaque DLL dont l'image dépend et, pour chacune, les fonctions dont elle a besoin. Pour chaque fonction importée il y a deux tableaux parallèles : l'Import Name Table (les entrées "hint/name", décrivant ce qu'il faut importer) et l'Import Address Table (IAT). Au moment du chargement, le loader résout chaque import vers l'adresse réelle de la fonction et écrit cette adresse dans l'IAT. À partir de là, un appel comme `CreateFileW` est en réalité un appel indirect via le slot IAT que le loader a rempli.

Les fonctions peuvent être importées par nom (le cas habituel) ou par ordinal (par index numérique dans la table d'exports de la DLL cible, ce qui évite la recherche par nom). Comme l'IAT n'est qu'une table de pointeurs de fonctions qui est patchée à l'exécution, elle est une cible naturelle pour l'instrumentation comme pour l'abus, comme nous le verrons.

---

# Exports

L'autre côté du contrat est l'Export Directory, présent dans les DLLs qui exposent des fonctions. Il contient trois tableaux liés : l'Export Address Table (EAT), contenant les RVAs des fonctions exportées ; la table des pointeurs de noms, contenant les noms exportés triés ; et la table des ordinaux, mappant chaque nom à un index dans l'EAT. Quand du code appelle `GetProcAddress(hModule, "SomeFunc")`, le loader effectue une recherche binaire dans la table des noms, utilise l'ordinal correspondant pour indexer l'EAT, ajoute la base du module au RVA, et retourne le pointeur de fonction.

Un export peut aussi être un forwarded export : au lieu d'un RVA vers le code de la DLL elle-même, l'entrée EAT est une chaîne comme `NTDLL.RtlAllocateHeap`, disant au loader de résoudre l'appel dans une autre DLL. C'est ainsi que, par exemple, de nombreuses fonctions de kernel32 sont transparemment forwardées vers ntdll ou les DLLs du schéma API-set.

---

# Le processus de chargement (Loader Process)

Transformer un fichier PE en code exécutable est le travail du loader — les routines `Ldr*` dans ntdll.dll. La séquence, en gros, est :

1. **Mapper l'image.** Le fichier est mappé dans l'espace d'adressage comme une image section, avec chaque section PE placée à son RVA et dotée de la protection de page appropriée (`.text` execute-read, `.data` read-write, etc.).
    
2. **Enregistrer le module.** Le loader enregistre le nouveau module dans les trois listes chaînées accrochées à `PEB_LDR_DATA` — `InLoadOrderModuleList`, `InMemoryOrderModuleList`, et `InInitializationOrderModuleList`.
    
3. **Résoudre les imports.** Pour chaque DLL importée, le loader la charge (en résolvant récursivement ses imports), puis remplit l'IAT avec les adresses résolues.
    
4. **Appliquer les relocations** si l'image n'a pas atterri à son ImageBase préféré (voir ci-dessous).
    
5. **Exécuter les initialiseurs.** Les TLS callbacks s'exécutent en premier, puis le point d'entrée est appelé — pour une DLL, `DllMain` avec `DLL_PROCESS_ATTACH`.
    

Le détail que les TLS callbacks s'exécutent avant le point d'entrée est important pour les analystes : les malwares cachent souvent leurs premières actions dans un TLS callback précisément parce qu'un débogueur configuré pour s'arrêter au point d'entrée les aura déjà exécutés.

---

# Relocations de base et ASLR

Comme les RVAs sont relatives, la plupart d'un PE est position-independent — mais pas tout. Certaines instructions et données embarquent des adresses absolues qui supposent que l'image se trouve à `ImageBase`. Quand l'ASLR charge l'image ailleurs (ce qui est le cas habituel aujourd'hui), ces valeurs absolues sont incorrectes. La section `.reloc`, la base relocation table, est une liste de chaque emplacement qui doit être corrigé. Le loader calcule le delta entre l'adresse de chargement réelle et `ImageBase` et l'ajoute à chaque emplacement listé. Une DLL dont les relocations ont été supprimées ne peut se charger qu'à sa base préférée, et échouera si cette base est déjà occupée — une raison pour laquelle les relocations comptent encore dans un monde ASLR.

---

# Pertinence pour la sécurité

Le format PE et le loader sont à la base d'une quantité remarquable de techniques offensives et défensives :

**DLL search-order hijacking et phantom DLLs.** Quand une application importe une DLL par nom sans chemin complet, le loader cherche dans un ordre défini de répertoires. Si un attaquant peut déposer une DLL malveillante plus tôt dans cet ordre de recherche — ou fournir une DLL que l'application tente de charger mais qui n'existe pas ("phantom" DLL) — son code est chargé dans le processus cible de façon légitime.

**IAT et EAT hooking.** Comme l'IAT n'est qu'une table de pointeurs, écraser un slot redirige chaque appel qui passe par lui. Les produits EDR (pour la visibilité) comme les malwares (pour le contrôle) hookent l'IAT ou l'EAT pour intercepter les appels API en user mode.

**Manual mapping / reflective loading.** Un attaquant peut reproduire les étapes du loader — mapper les sections, résoudre les imports, appliquer les relocations, appeler le point d'entrée — sans appeler le vrai loader. La DLL payload n'est donc jamais enregistrée dans les listes de modules du PEB, donc les outils qui énumèrent les modules de la façon normale ne la voient pas. C'est exactement pourquoi la forensique mémoire croise le VAD tree (vérité terrain de ce qui est mappé) avec la liste de modules annoncée par le loader.

**TLS-callback anti-analysis.** Exécuter du code dans un TLS callback avant le point d'entrée est un truc classique pour s'exécuter avant le breakpoint d'entrée d'un débogueur.

---

# Conclusion

Le format PE est le blueprint et le loader est le constructeur : les headers décrivent où tout va, les tables d'imports et d'exports définissent le contrat entre modules, les relocations réconcilient ce blueprint avec l'ASLR, et le loader assemble tout et passe le contrôle au point d'entrée. Comme une grande partie de tout cela se passe en patchant des tables à l'exécution — l'IAT, les listes de modules, les relocations — c'est aussi là que vit une grande partie de l'injection et de l'évasion.