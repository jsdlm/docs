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

Deux écosystèmes : .NET Framework (Windows, jusqu'à 4.8) et .NET moderne (6/8/9, multiplateforme). MinGW-w64 / w64devkit ne fournit pas de compilateur C# : passer par le SDK .NET ou Mono.

## Linux

```bash
sudo apt install dotnet-sdk-8.0
sudo apt install mono-complete        # pour cibler .NET Framework
```

```bash
mcs prog.cs -out:prog.exe
mcs -target:library prog.cs -out:prog.dll
mcs -unsafe -platform:x86 prog.cs -out:prog.exe

dotnet new console -o MonApp
cd MonApp && dotnet build -c Release
```

## Windows

```powershell
winget install Microsoft.DotNet.SDK.8
```

```powershell
dotnet build -c Release
```

Compilateur .NET Framework présent nativement, sans installation :

```cmd
C:\Windows\Microsoft.NET\Framework64\v4.0.30319\csc.exe /out:prog.exe prog.cs
csc.exe /target:library /out:prog.dll prog.cs
csc.exe /unsafe /platform:x86 /out:prog.exe prog.cs
```

