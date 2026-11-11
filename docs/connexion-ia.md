# Extensions IA et connexion des outils — Linux

Les panneaux Glyphe restent des vues web natives du profil. Ils sont indépendants
 des extensions Claude/ChatGPT et ne remplacent pas leurs connecteurs.

## Recherche des Native Messaging Hosts

Inspection des sources Chromium 157 de CT 118 le 11 novembre 2026 :
`chrome/browser/extensions/api/messaging/launch_context_posix.cc`.

Ordre effectif après `native-messaging` :

1. `<user-data-dir>/NativeMessagingHosts` (donc
   `~/.config/helium-glyphe/NativeMessagingHosts` avec le lanceur Glyphe) ;
2. dossier utilisateur Google Chrome, déjà pris en charge par Helium ;
3. `$XDG_CONFIG_HOME/chromium/NativeMessagingHosts`, sinon
   `~/.config/chromium/NativeMessagingHosts` (ajout Glyphe) ;
4. `/etc/chromium/native-messaging-hosts`, déjà pris en charge ;
5. `/etc/opt/chrome/native-messaging-hosts`, déjà pris en charge.

La politique `NativeMessagingUserLevelHosts` continue de s'appliquer aux trois
emplacements utilisateur. Le premier fichier trouvé gagne ; un manifeste primaire
invalide n'est pas contourné. Aucun changement des `allowed_origins`, permissions
`nativeMessaging`, validations de nom/JSON ni de lancement de l'exécutable.

`python3 tools/native-messaging.py` affiche les hôtes existants et la disponibilité
de leurs exécutables. `--link` lie les manifestes disponibles vers le profil Glyphe,
sans écraser un fichier ou un lien existant. Ce mode est facultatif avec le patch.
`--target` accepte le dossier NativeMessagingHosts d'un profil personnalisé.
Ce script ne fabrique pas de connecteur et ne modifie aucun identifiant d'extension.

## Claude Code

CLI présent : `/usr/bin/claude` (lanceur vers `/opt/claude-code/bin/claude`).
Après le setup utilisateur, les manifestes existent dans les dossiers Chrome et
Chromium et pointent vers `~/.claude/chrome/chrome-native-host`. Un test réel avec
l'extension officielle 1.0.106 a obtenu `pong` de cet hôte dans un profil isolé
(`validation/claude-native-ping.json`). La recherche de manifeste et le lancement
fonctionnent. L'utilisateur a toutefois signalé que `/chrome` ne détectait pas
l'extension de son profil habituel ; cette détection complète reste non validée.

1. Ouvrir le profil Helium Glyphe habituel et installer [Claude officiel](https://chromewebstore.google.com/detail/claude/fcoeoabgfenejglbffodgkkbkcdhcgfn).
2. S'identifier dans l'extension avec son compte Claude.
3. Lancer `claude --chrome`, puis `/chrome`. L'intégration doit indiquer
   Enabled / Installed. Choisir le navigateur connecté si plusieurs apparaissent.
4. Si le connecteur manque toujours, suivre le setup `/chrome`, redémarrer Helium,
   puis relancer le diagnostic Python. Un manifeste installé côté Chrome sera
   découvert automatiquement par Helium.

La [documentation Claude Code](https://code.claude.com/docs/en/chrome) exige une
connexion directe au compte Anthropic ; l'authentification par clé API, jeton
longue durée ou fournisseur tiers ne suffit pas. Elle cite plusieurs navigateurs
Chromium mais pas Helium : la compatibilité de transport ne vaut donc pas une
certification de prise en charge par Anthropic.

## ChatGPT / Codex

Codex CLI est installé. Le script de diagnostic OpenAI embarqué
`check-native-host-manifest.js --browser chrome --json` signale l'absence de
`~/.config/google-chrome/NativeMessagingHosts/com.openai.codexextension.json`.
Les scripts de détection OpenAI installés énumèrent des familles de navigateurs et
leurs exécutables connus ; Helium n'est pas dans cette liste. Le patch Chromium
ne peut pas modifier cette détection effectuée par l'application externe.

L'[extension ChatGPT officielle](https://chromewebstore.google.com/detail/chatgpt/hehggadaopoacecdllhhajmbjkdcmajg)
se configure depuis **ChatGPT bureau → Settings → Computer Use**. Installer le
connecteur proposé, se connecter et vérifier que l'application affiche **Manage**.
Helium ne fait pas partie des navigateurs annoncés dans la
[documentation officielle](https://learn.chatgpt.com/docs/chrome-extension).
Ne pas remplacer les exécutables de Chrome ni modifier le cache du plugin pour
faire passer Helium pour Chrome : ces changements seraient fragiles.

La [documentation Browser](https://learn.chatgpt.com/docs/browser) précise que le
navigateur intégré n'est pas disponible dans Codex CLI ou l'extension IDE. La
connexion de l'application bureau et un éventuel serveur MCP configuré pour la CLI
sont des intégrations distinctes. Le partage des manifestes ne crée pas à lui seul
une fonctionnalité navigateur dans la CLI. Une connexion Codex CLI complète n'est
pas revendiquée ici.

## Vérification du transport

`node tools/validate-native-messaging.mjs /chemin/helium resultat.json`
lance un profil jetable, une extension MV3 avec une clé aléatoire et un hôte Python
à protocole longueur+JSON. Le test compare Chrome, Chromium et une origine refusée.
Tout est créé sous `/tmp`, sans toucher aux manifestes ou comptes utilisateur.
Ce test prouve le transport du binaire ; il ne prouve pas une connexion aux comptes.

## Web Store et services Helium

L'installation de Claude 1.0.106 a réussi dans le profil de validation. Le bouton
« Supprimer de Helium » et les fichiers du CRX dépaqueté ont été contrôlés.
Un profil lancé avec `--no-first-run` peut avoir `helium.services.user_consented`
à false : le téléchargement est alors volontairement renvoyé vers l'URL
« services désactivés ». Activer les services d'extensions dans les réglages
Helium et suivre l'onboarding avant l'installation. Le test a activé ce réglage
uniquement dans son profil jetable ; aucun choix de consentement du profil
utilisateur n'a été modifié par cette validation.

Le patch `webstore-install` autorise en outre les CRX HTTPS des chemins officiels
Google (`clients2.google.com/service/update2/crx` et
`clients2.googleusercontent.com/crx/blobs/`), sans modifier les autres sources,
les confirmations natives ni les contrôles CRX.

La vérification utilisateur `/chrome` (lignes **Status** et **Extension**) est
reportée à la fin du chantier, à sa demande. Le diagnostic d'authentification
Claude Code confirme un compte `claude.ai` / `firstParty`, sans clé API ; aucun
identifiant personnel n'est conservé dans ce rapport.
