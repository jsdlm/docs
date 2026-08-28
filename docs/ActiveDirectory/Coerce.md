# Principe général

Forcer une machine distante (souvent un DC) à s'authentifier avec son **compte machine** vers l'attaquant, en exploitant une fonction RPC qui accepte un chemin UNC fourni par l'appelant. L'authentification NTLM capturée est ensuite relayée (NTLM relay) vers un autre service, typiquement ADCS (ESC8) ou LDAP.

**Workflow commun aux 4 techniques :**
1. Attaquant contacte l'interface RPC de la cible distante.
2. Appelle une fonction en fournissant un chemin UNC pointant vers sa propre machine.
3. Le service cible (SYSTEM) tente de s'y connecter → authentification NTLM du compte machine.
4. Attaquant capture cette authentification (ntlmrelayx ou équivalent).
5. Relay vers ADCS/LDAP pour obtenir un certificat ou modifier des attributs AD au nom du compte machine cible.

# MS-RPRN - PrinterBug (SpoolSample)

Fonction : `RpcRemoteFindFirstPrinterChangeNotificationEx`. 
Usage légitime : abonnement à des notifications d'événements d'impression. 
Abus : identique au principe de PrintSpoofer, mais le chemin UNC pointe vers l'attaquant à distance plutôt qu'un pipe local. Même fonction RPC, deux usages (local = privesc direct, distant = relay).
# MS-EFSR - PetitPotam

Fonction : `EfsRpcOpenFileRaw` (et variantes comme `EfsRpcEncryptFileSrv`). 
Usage légitime : gestion à distance de fichiers chiffrés EFS (sauvegarde/restauration). 
Abus : chemin UNC détourné pour forcer le service EFS à s'authentifier vers l'attaquant.
# MS-FSRVP - ShadowCoerce

Fonction : liée au File Server VSS Agent Service (gestion de snapshots de partages réseau). 
Usage légitime : orchestrer la création de clichés instantanés (VSS) entre un serveur de fichiers et un initiateur distant. 
Abus : détourne la logique de communication du protocole pour forcer le serveur de fichiers à s'authentifier vers l'attaquant.
# MS-DFSNM - DFSCoerce

Fonction : gestion des namespaces DFS (Distributed File System). 
Usage légitime : administration de namespaces agrégeant des partages sur plusieurs serveurs. 
Abus : appel à une fonction de gestion DFS avec un chemin détourné, forçant le service à s'authentifier vers l'attaquant.
# Point commun de conception

Ces trois protocoles (EFSR, FSRVP, DFSNM) n'ont pas d'équivalent local exploitable : leur architecture est pensée nativement pour des interactions entre machines distinctes, contrairement à MS-RPRN qui accepte aussi bien un chemin local que distant.