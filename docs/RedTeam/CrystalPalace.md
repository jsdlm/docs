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