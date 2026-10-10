## Installation

| Outil          | Installation                                                            |
| -------------- | ----------------------------------------------------------------------- |
| PE-bear        | `winget install hasherezade.PE-bear`                                    |
| pestudio       | [winitor.com/download](https://www.winitor.com/download) (zip portable) |
| Detect It Easy | https://github.com/horsicq/detect-it-easy                               |
| CFF Explorer   | https://ntcore.com/explorer-suite/                                      |
| objdump        | Inclus avec MinGW (`x86_64-w64-mingw32-objdump`)                        |

## Commandes rapides

```bash
# IAT
objdump -p loader.exe | grep -A 500 "Import Tables"

# Comparaison IAT
objdump -p loader1.exe | grep "DLL Name" -A 100 > imports1.txt
objdump -p loader2.exe | grep "DLL Name" -A 100 > imports2.txt
fc.exe .\imports1.txt .\imports2.txt
# -> Comaprer avec notepad++ module compare

# headers de sections
objdump -h loader.exe

# Strings suspectes
strings loader.exe | findstr /i "Virtual Alloc Process Thread"
```

## Quoi regarder

| Outil | Usage principal |
|-------|----------------|
| PE-bear | IAT visuelle, sections, headers PE |
| pestudio | Score de suspicion, strings flaggees, indicateurs ML |
| DiE | Compilateur, packer, entropie globale |
| CFF Explorer | Edition de headers PE, vue detaillee des directories |
| objdump | Check rapide en CLI sans quitter le terminal |
