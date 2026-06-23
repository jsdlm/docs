# Hashcat Rules

https://github.com/stealthsploit/OneRuleToRuleThemStill
# Rule Functions

| Fonction | Description                                              | Exemple                  |
| -------- | -------------------------------------------------------- | ------------------------ |
| `$X`     | Ajoute le caractère X en fin de mot                      | `$1` → `password1`       |
| `^X`     | Ajoute le caractère X en début de mot                    | `^3` → `3password`       |
| `c`      | Capitalise la première lettre, met le reste en minuscule | `c` → `Password`         |
| `u`      | Met tous les caractères en majuscule                     | `u` → `PASSWORD`         |
| `d`      | Duplique le mot                                          | `d` → `passwordpassword` |

---

# Syntaxe des fichiers de règles

## Fonctions sur la même ligne = appliquées consécutivement

```
$1 c $!
```

Résultat : `Password1!`

## Fonctions sur des lignes séparées = règles indépendantes

```
$1
c
```

Résultat : deux mots générés par entrée (`password1` et `Password`)

Les fonctions sont appliquées **de gauche à droite**.

---

# Commandes

## Mode debug (affiche les mots mutés sans cracker)

```bash
hashcat -r demo.rule --stdout wordlist.txt
```

## Cracker un hash MD5 avec une règle

```bash
hashcat -m 0 hash.txt /usr/share/wordlists/rockyou.txt -r demo.rule
```

## Avec --force (si pas de GPU disponible)

```bash
hashcat -m 0 hash.txt /usr/share/wordlists/rockyou.txt -r demo.rule --force
```

---

# Exemples de fichiers de règles

## demo1.rule - capitalisation + append "1" + append "!"

```
$1 c $!
```

Sorties : `Password1!`, `Iloveyou1!`, `Princess1!`

## demo2.rule - append "!" + append "1" + capitalisation

```
$! $1 c
```

Sorties : `Password!1`, `Iloveyou!1`, `Princess!1`

## demo3.rule - plusieurs règles pour politique complexe

```
$1 c $!
$2 c $!
$1 $2 $3 c $!
```

Sorties : `Password1!`, `Password2!`, `Password123!`

## demo4.rule

```
$1 $@ $3 $$ $5
```

Sorties : `Password1@3$5`, ``Iloveyou1@3$5``, `Princess1@3$5`

## demo5.rule

```
u d
```

Sorties : `PASSWORDPASSWORD`, `ILOVEYOUILOVEYOU`, `PRINCESSPRINCESS`

---

# Règles prédéfinies Hashcat

Situées dans `/usr/share/hashcat/rules/` :

|Fichier|Description|
|---|---|
|`best66.rule`|66 règles les plus efficaces|
|`combinator.rule`|Combinaison de mots|
|`d3ad0ne.rule`|Règles avancées (~200k)|
|`dive.rule`|Très large couverture (~788k)|
|`generated.rule`|Règles générées automatiquement|
|`generated2.rule`|Variante de generated.rule|
|`Incisive-leetspeak.rule`|Substitutions leet speak|
|`InsidePro-HashManager.rule`|Règles InsidePro|
|`InsidePro-PasswordsPro.rule`|Règles InsidePro variante|
|`leetspeak.rule`|Leet speak basique|
|`oscommerce.rule`|Politique osCommerce|
|`rockyou-30000.rule`|30 000 règles basées sur rockyou|
|`specific.rule`|Règles ciblées|
|`T0XlC-insert_00-99_1950-2050_toprules_0_F.rule`|Insertion d'années et nombres|

---

# Préparation de la wordlist

```bash
# Extraire les 10 premiers mots de rockyou
head /usr/share/wordlists/rockyou.txt > demo.txt

# Supprimer les lignes commençant par "1"
sed -i '/^1/d' demo.txt
```