
1. Télécharger la [Salesforce cli](https://developer.salesforce.com/tools/salesforcecli)
2. Ajouter dans le PATH : `export PATH=$PATH:/home/pentester/Downloads/sf/bin`
3. S'authentifier : `sf org login web --alias monorg --instance-url https://moninstance.salesforce.com`
4. Initialiser un projet : `sf project generate --name monprojet`
5. Se déplacer dans le dossier projet : `cd monprojet`
6. Récupérer les metadata : `sf project retrieve start --manifest package.xml --target-org monorg`
