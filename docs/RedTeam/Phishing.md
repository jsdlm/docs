# Cloner une page web

```bash
# -E  : ajuste les extensions (.php → .html)
# -k  : convertit les liens pour navigation locale
# -K  : garde le fichier original en .orig
# -p  : télécharge tous les éléments de la page (CSS, images...)
# -H  : autorise les domaines externes (span hosts)
# -D  : restreint au domaine spécifié
# -nd : pas de sous-dossiers, tout à plat

wget -E -k -K -p -e robots=off -H -Dzoom.us -nd "https://zoom.us/signin#/login"

wget --mirror -p --convert-links -P ./local https://현진.com/OSCP/Challenge-Labs/
```

[GitHub - fin3ss3g0d/evilgophish: evilginx3 + gophish](https://github.com/fin3ss3g0d/evilgophish)

[GitHub - kgretzky/gophish: Open-Source Phishing Toolkit](https://github.com/kgretzky/gophish)

[API de communication SMS/Voice/e-mail/authentification | Twilio](https://www.twilio.com/fr-fr)
