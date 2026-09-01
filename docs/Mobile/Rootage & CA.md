# Outils

- **platform-tools** (`adb`, `fastboot`)
- **Frija** (ou Samloader) — téléchargement firmware Samsung
- **lz4** — décompression du boot
- **Magisk** (APK) — patch du `boot.img`
- **Odin** (Windows) — flash Samsung
- **Genymotion** + VirtualBox
- **Burp**, **openssl**

---

# 1. Root Samsung (via Odin)

Samsung n'a pas de Fastboot → on flashe en **Download Mode** avec **Odin**.

## 1.1 Activer les options développeur

`Paramètres > À propos > Numéro de build` (7 appuis), puis activer **Débogage USB** + **Déverrouillage OEM**.

## 1.2 Récupérer le firmware exact

Identifier modèle + CSC :

```bash
adb shell getprop ro.product.model      # ex : SM-A505F
adb shell getprop ril.official_cscver   # CSC (région)
```

Télécharger le firmware officiel avec **Frija** (GUI Windows : entrer modèle + CSC) ou **Samloader** (`pip install samloader`). Alternative site : **samfrew.com** / **sammobile.com** (plus lent).

Le firmware doit correspondre **exactement** à la build déjà installée (`Paramètres > À propos > Numéro de build`), sinon bootloop.

## 1.3 Extraire le boot.img

Le `.zip` firmware contient plusieurs `.tar.md5` : **AP**, **BL**, **CP**, **CSC**. Le `boot.img.lz4` est dans le **AP**.

```bash
# extraire AP.tar.md5, puis décompresser
lz4 -d boot.img.lz4 boot.img
```

## 1.4 Installer Magisk et patcher le boot

Magisk est une **APK** classique.

```bash
# dernier Magisk-vXX.apk : github.com/topjohnwu/Magisk/releases
adb install Magisk-vXX.apk

# pousser le boot à patcher
adb push boot.img /sdcard/Download/
```

Dans l'app **Magisk** : `Install` > `Patch a file` (pas "Direct install", tu n'es pas encore root) > choisir `boot.img`. → génère `magisk_patched-xxxx.img` dans `/sdcard/Download/`.

## 1.5 Empaqueter pour Odin

```bash
adb pull /sdcard/Download/magisk_patched-xxxx.img
mv magisk_patched-xxxx.img boot.img
tar -cf boot.tar boot.img       # boot.img à la RACINE du tar, sans dossier, sans 7-Zip
```

## 1.6 Flasher

```bash
adb reboot download             # Download Mode (PAS "reboot bootloader" sur Samsung)
```

Dans **Odin** :

- `AP` → `boot.tar`
- Cocher `F. Reset Time`, **décocher** `Auto Reboot`
- `Start` → attendre `PASS!`

## 1.7 Finaliser

Après reboot, rouvrir **Magisk** : il termine l'installation (parfois un dernier reboot demandé).

```bash
adb shell su -c id              # attendu : uid=0(root)
```

**Pièges** :

- `This file is not AP file` / `Unassigned file` → tar mal fait (nom interne doit être `boot.img`, créé avec `tar`).
- `KG State: Checking` (lisible seulement en Download Mode) bloque le flash → doit être `Active`.
- `adb root` échoue toujours en prod → normal, passe par `su`.

---

# 2. Root Genymotion

**Rien à faire, c'est déjà root.**

```bash
adb shell su -c id              # uid=0(root) → OK
```

Si `adb` ne voit pas le device : `Genymotion > Settings > ADB` → pointer sur ton dossier `platform-tools` (sinon conflit de binaire adb).

---

# 3. CA Burp en CA système

Burp : `Proxy > Options > Export CA certificate > DER` → `cacert.der`

```bash
# conversion + hash (nom de fichier attendu par Android)
openssl x509 -inform DER -in cacert.der -out cacert.pem
openssl x509 -inform PEM -subject_hash_old -in cacert.pem | head -1
# → ex : 9a5ba575  →  fichier cible = 9a5ba575.0

# installation (root)
adb push cacert.pem /sdcard/Download/9a5ba575.0
adb shell
su
mount -o rw,remount /system
cp /sdcard/Download/9a5ba575.0 /system/etc/security/cacerts/
chmod 644 /system/etc/security/cacerts/9a5ba575.0
reboot
```

- `Read-only file system` → `/system` pas remonté (refais le `mount`) ou verity actif → passe par un module **Magisk (AlwaysTrustUserCerts)**.
- **Android 14** : le remount ne suffit pas (CA déplacées dans l'APEX Conscrypt) → module Magisk obligatoire.

---
