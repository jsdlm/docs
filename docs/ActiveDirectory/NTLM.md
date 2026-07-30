
Utilisé quand :
- Authentification par **IP** (pas par hostname)
- Hostname non enregistré dans le DNS AD
- Application tierce qui ne supporte pas Kerberos

**Flux d'authentification (7 étapes)**

1. Le client calcule le **hash NTLM** depuis le mot de passe
2. Le client envoie le **username** au serveur
3. Le serveur renvoie un **nonce** (valeur aléatoire = challenge)
4. Le client chiffre le nonce avec le hash NTLM → **response**
5. Le serveur transfère username + nonce + response au **DC**
6. Le DC chiffre le nonce avec le hash NTLM stocké et compare à la response
7. Si égaux → authentification réussie

![](../ActiveDirectory/img/Pasted%20image%2020260512145336.png)

> NTLM est non-réversible mais rapide à craquer (jusqu'à 600 milliards de hash/s avec GPU haut de gamme). Un mot de passe de 8 caractères peut être cracké en ~2,5h.
