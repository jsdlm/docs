# Reporting

## Screenshot Requirements

> **CRITIQUE** : Sans screenshots valides, les points ne sont PAS accordés.

### Éléments Requis

1. Contenu de `local.txt` ou `proof.txt`
2. Adresse IP affichée via `ifconfig`, `ipconfig`, ou `ip addr`
3. Les **deux dans le même screenshot**

### Commandes

```shell
# Linux
cat /root/proof.txt && hostname && ip addr
cat /home/*/local.txt && hostname && ip addr

# Windows
type C:\Users\Administrator\Desktop\proof.txt && ipconfig
type C:\Users\Administrator\Desktop\proof.txt && hostname && ipconfig
```

### Checklist Screenshot (par machine)

- [ ] output ifconfig/ipconfig
- [ ] output whoami/id
- [ ] proof.txt ou local.txt lu
- [ ] Commande utilisée pour obtenir l'accès
- [ ] Screenshots de l'exploitation (payload SQLi, RCE input, etc.)

---

## Trouver les Flags

### Windows CMD

```cmd
:: Emplacements courants
type C:\Users\Administrator\Desktop\proof.txt
dir /s /b C:\Users\*local.txt 2>nul
dir /s /b C:\Users\*proof.txt 2>nul

:: Chercher sur tout le drive
where /r C:\ proof.txt local.txt 2>nul

:: One-liner : trouver et afficher
for /r C:\Users %i in (proof.txt local.txt) do @if exist "%i" echo %i && type "%i"
```

### Windows PowerShell

```powershell
Get-ChildItem -Path C:\Users -Recurse -Include proof.txt,local.txt -ErrorAction SilentlyContinue |
  foreach { echo $_.FullName; Get-Content $_ }
```

### Linux

```shell
# Emplacements courants
cat /root/proof.txt 2>/dev/null
find /home -name local.txt 2>/dev/null -exec cat {} \;

# Chercher sur tout le système
find / -name "proof.txt" -o -name "local.txt" 2>/dev/null | xargs cat 2>/dev/null
```

---

## Flag Submission

- Soumettre les flags dans le **panel de contrôle** avant la fin de l'exam
- Les flags **changent après un revert** → soumettre immédiatement
- Le panel n'indique **pas** si le flag est correct

---

## Template Rapport

```markdown
## Executive Summary (Non-Technique)
- Vue d'ensemble des findings
- Nombre de machines compromises
- Évaluation de la sévérité

## Methodology

### Phase 1 : Information Gathering
- Résultats du port scanning
- Identification des services

### Phase 2 : Exploitation
- Méthode d'accès initial pour chaque cible
- Commandes exécutées
- Screenshots

### Phase 3 : Privilege Escalation
- Vulnérabilité trouvée
- Étapes d'exploitation
- Preuve de compromission

### Phase 4 : Post-Exploitation
- Données accédées

## Appendix
- Outputs complets des commandes
- Screenshots de support
```

---

## Tips Rédaction

### À FAIRE

- Être précis : `"SQL injection dans le champ 'username' du formulaire de login"`
- Montrer l'output des commandes : copier-coller le terminal
- Screenshot tout ce qui prouve : initial access, privilege escalation, proof.txt
- Être clair : `"J'ai exécuté X, reçu Y, donc Z"`
- Numéroter tous les screenshots

### À NE PAS FAIRE

- Descriptions génériques : `"pentest de l'application web"`
- Supposer que ça a marché : `"j'ai vérifié si SUID existait"` (montrer l'output réel)
- Manquer des screenshots : tout privesc sans proof.txt screenshot = rejeté
- Utiliser des pronoms : utiliser `"The attacker"` ou `"The tester"`, pas `"I"`

---

## Checklist Finale Avant Soumission

- [ ] 6+ screenshots pour l'initial access
- [ ] 6+ screenshots pour le privilege escalation
- [ ] Screenshot proof.txt pour chaque machine compromise
- [ ] Commandes clairement visibles dans le rapport
- [ ] Contenu de proof.txt lisible dans le screenshot
- [ ] Pas d'informations personnelles (vrais noms, IPs hors lab)
- [ ] Format template OffSec respecté
- [ ] Spell-check effectué
- [ ] Nom de fichier : `OSID-OffSecReportTemplate.docx`

> **Délai** : 24h après la fin de l'exam. Soumettre même si pas sûr à 100%.
