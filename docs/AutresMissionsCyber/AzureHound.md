
https://github.com/SpecterOps/AzureHound

Télécharger la dernière release `windows-amd64` et placer le binaire dans un dossier whitelist par l'antivirus.
# Récupérer un refresh token

Script qui passe par le device code flow d'Azure AD (compatible MFA) pour récupérer un refresh token, exploitable par AzureHound / BloodHound sans mot de passe.

https://github.com/jsdlm/scripts/blob/main/azure/get_az_refresh_token.ps1

```powershell
.\get_az_refresh_token.ps1

# Ou pour ouvrir directement le navigateur par défaut à la bonne page
.\get_az_refresh_token.ps1 -OpenBrowser
```

Valider le code affiché sur https://microsoft.com/devicelogin, le script sauvegarde les tokens dans `tokens.json` et affiche la commande AzureHound à lancer.

# Collecte

```powershell
azurehound -r "<refresh_token>" list --tenant "<tenant_id>" -o azurehound_output.json
```

Uploader ensuite `azurehound_output.json` dans BloodHound.
