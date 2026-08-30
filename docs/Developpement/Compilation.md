# MinGW-w64 via w64devkit

**Téléchargement**
https://github.com/skeeto/w64devkit/releases
Récupérer `w64devkit-x64-x.y.z.7z.exe` depuis les releases GitHub du projet (skeeto/w64devkit).

**Installation**  
Décompresser dans `C:\w64devkit` (chemin sans espace ni accent).

**PATH**

```powershell
[Environment]::SetEnvironmentVariable(
  "Path",
  [Environment]::GetEnvironmentVariable("Path", "User") + ";C:\w64devkit\bin",
  "User"
)
```

**Vérification**
```
gcc --version
g++ --version
make --version
gdb --version
```

---
# C

**Extensions**

- `.c` source, `.h` en-tête
- `.o` objet (Linux), `.obj` objet (MSVC)
- `.a` bibliothèque statique, `.lib` (MSVC)
- `.so` bibliothèque dynamique (Linux), `.dll` (Windows)

## Linux

```bash
sudo apt install build-essential
gcc prog.c -o prog
gcc -static prog.c -o prog
gcc -shared -fPIC lib.c -o lib.so
```

## Windows (MinGW-w64 / w64devkit)

`gcc`, `make` et `gdb` sont fournis par w64devkit (voir installation en haut de page), aucune installation supplémentaire n'est nécessaire.

```powershell
gcc prog.c -o prog.exe
gcc -static prog.c -o prog.exe
gcc -shared lib.c -o lib.dll
```

Le binaire produit est natif Windows, sans dépendance à un environnement tiers (contrairement à MSYS2 qui peut lier `msys-2.0.dll` si compilé depuis l'environnement `MSYS`).

## Cross-compilation Linux vers Windows

```bash
sudo apt install mingw-w64
```

```bash
x86_64-w64-mingw32-gcc prog.c -o prog.exe
i686-w64-mingw32-gcc prog.c -o prog32.exe
x86_64-w64-mingw32-gcc -shared lib.c -o lib.dll

# si : undefined reference to _imp__WSAStartup@8
i686-w64-mingw32-gcc prog.c -o prog32.exe -lws2_32
```

---

# C++

**Extensions**

- Sources : `.cpp`, `.cc`, `.cxx`
- En-têtes : `.h`, `.hpp`, `.hxx`, `.inl`
- Modules C++20 : `.cppm` (Clang), `.ixx` (MSVC)
- Objets et bibliothèques identiques au C

## Linux

```bash
sudo apt install build-essential cmake
g++ -std=c++17 prog.cpp -o prog
g++ -std=c++17 -static prog.cpp -o prog
```

## Windows (MinGW-w64 / w64devkit)

`g++` est fourni par w64devkit (voir installation en haut de page), aucune installation supplémentaire n'est nécessaire.

```powershell
g++ -std=c++17 prog.cpp -o prog.exe
g++ -std=c++17 -static prog.cpp -o prog.exe
```

Sans `-static`, le binaire réclame `libstdc++-6.dll` et `libgcc_s_seh-1.dll`.

## Cross-compilation Linux vers Windows

```bash
sudo apt install mingw-w64
```

```bash
x86_64-w64-mingw32-g++ prog.cpp -o prog.exe -static
i686-w64-mingw32-g++ prog.cpp -o prog32.exe -static
```

---

# C\#

**Extensions**

- `.cs` source, `.csx` script
- `.csproj` projet, `.sln` solution
- `.dll` assembly bibliothèque, `.exe` assembly exécutable
- `.pdb` symboles de debug

**Prérequis**

Visual Studio Community
```
winget install Microsoft.VisualStudio.Community
```

Puis installer la charge de travail .NET Desktop.

**Procédure**

1. Cloner ou décompresser le projet.
2. Ouvrir le `.sln` dans Visual Studio (double-clic).
3. Si VS propose de **retarget** ou de mettre à jour, accepter.
4. Clic droit sur le projet > **Gérer les packages NuGet**.
5. **Restaurer** les paquets.
6. Choisir la configuration **Release** dans la barre d'outils.
7. **Générer > Générer la solution** (`Ctrl+Maj+B`).

Le binaire sort dans `bin\Release\`.

## Troubleshooting

En cas d'échec "Erreur **Fody** ou `MsBuildMajorVersion` vide" : dans Gérer les packages NuGet, **mettre à jour** le paquet fautif (Fody/Costura), puis rebuild.


**Erreur "pack de ciblage vX.Y introuvable"**
Vérifier les versions installées :

```powershell
Get-ChildItem "C:\Program Files (x86)\Reference Assemblies\Microsoft\Framework\.NETFramework\"
```

Fix : dans le `.csproj`, mettre `TargetFrameworkVersion` sur une version listée ci-dessus.
```xml
<TargetFrameworkVersion>v4.8.1</TargetFrameworkVersion>
```
