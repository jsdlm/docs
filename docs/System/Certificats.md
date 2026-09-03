# Prérequis

**Binaire OpenSSL** version 1.1.1 ou supérieure. La 3.x est recommandée (`-addext` y est fiable, la 1.0.2 ne le supporte pas du tout).

```bash
openssl version
```

**Un shell POSIX** pour les continuations de ligne `\` et l'opérateur `cat` de l'étape 6.

| Plateforme    | Installation                        | Remarque                                                                                                                |
| ------------- | ----------------------------------- | ----------------------------------------------------------------------------------------------------------------------- |
| Debian/Ubuntu | `apt install openssl`               | Généralement préinstallé                                                                                                |
| RHEL/Fedora   | `dnf install openssl`               | Généralement préinstallé                                                                                                |
| Arch          | `pacman -S openssl`                 | Préinstallé                                                                                                             |
| macOS         | `brew install openssl@3`            | Le binaire système est LibreSSL, incomplet sur certaines options ; utiliser celui de Homebrew                           |
| Windows       | WSL, Git Bash, ou build Win32/Win64 | En `cmd.exe`/PowerShell natif : remplacer `\` par `^` ou tout mettre sur une ligne, et `cat a b > c` par `type a b > c` |

# Fichier de configuration `cert.cnf`

Un seul fichier suffit pour les deux scénarios (auto-signé et signé par une CA) : `x509_extensions` est utilisé quand on génère directement un certificat x509, `req_extensions` quand on génère une CSR. Les deux pointent vers le même bloc `v3_req`, donc pas besoin de le dupliquer.

```ini
[req]
default_bits       = 2048
prompt             = no
default_md         = sha256
distinguished_name = dn
x509_extensions    = v3_req
req_extensions     = v3_req

[dn]
C  = FR
ST = IDF
L  = Paris
O  = Test
CN = example.local

[v3_req]
basicConstraints = CA:FALSE
keyUsage         = digitalSignature, keyEncipherment
extendedKeyUsage = serverAuth
subjectAltName   = @alt_names

[alt_names]
DNS.1 = example.local
DNS.2 = *.example.local
IP.1  = 127.0.0.1
```

# Auto-signé

## 1. Générer la clé et le certificat

```bash
openssl req -x509 -newkey rsa:2048 -nodes -days 365 \
  -config cert.cnf -keyout key.pem -out cert.pem
```

Fichiers produits : `key.pem` (clé privée non chiffrée) et `cert.pem` (certificat).

## 2. Vérifier le résultat

```bash
openssl x509 -in cert.pem -noout -text
```

## 3. Format PKCS#12 (optionnel)

```bash
openssl pkcs12 -export -inkey key.pem -in cert.pem -out cert.p12
```

# Certificat serveur signé par une CA

## 1. Créer la CA

```bash
openssl req -x509 -nodes -days 3650 -newkey rsa:2048 \
  -keyout demo-ca.key -out demo-ca.crt -subj "/CN=demo-ca" \
  -addext "basicConstraints=critical,CA:TRUE,pathlen:0" \
  -addext "keyUsage=critical,keyCertSign,cRLSign"
```

Produit : `demo-ca.key` (clé CA) et `demo-ca.crt` (certificat racine, à importer dans le magasin de confiance des clients).

## 2. Générer la clé serveur et la CSR

```bash
openssl req -new -nodes -newkey rsa:2048 \
  -keyout demo-key.pem -out demo.csr -config cert.cnf
```

## 3. Signer la CSR avec la CA

```bash
openssl x509 -req -sha256 -days 825 -in demo.csr \
  -CA demo-ca.crt -CAkey demo-ca.key -CAcreateserial \
  -out demo-cert.pem -extensions v3_req -extfile cert.cnf
```

Produit : `demo-cert.pem` (certificat serveur) et `demo-ca.srl` (compteur de numéros de série).

## 4. Vérifier

```bash
openssl x509 -in demo-cert.pem -noout -text
openssl verify -CAfile demo-ca.crt demo-cert.pem
```

## 5. Formats de sortie complémentaires

Chaîne complète (serveur + CA) pour les serveurs qui l'exigent :

```bash
cat demo-cert.pem demo-ca.crt > demo-fullchain.pem
```

PKCS#12 :

```bash
openssl pkcs12 -export -inkey demo-key.pem -in demo-cert.pem \
  -certfile demo-ca.crt -out demo.p12
```
