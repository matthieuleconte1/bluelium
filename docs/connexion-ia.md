# Connecteurs IA : Bluelium, macOS et Linux

Diagnostic du 16 novembre 2026. Trois étapes distinctes : le client découvre un
navigateur et son extension, le navigateur trouve un manifeste Native Messaging,
puis l'extension se connecte au compte et au client. Un `pong` de l'hôte prouve
le transport, pas les deux autres étapes. Les panneaux IA de Bluelium sont des
vues web du profil et ne remplacent pas ces extensions.

## Recherche des manifestes par Bluelium

Sources inspectées : Chromium 157, `chrome/common/chrome_paths*` et
`chrome/browser/extensions/api/messaging/launch_context_posix.cc`, patch Helium
`scan-chrome-native-messaging-hosts`, specs `native_messaging_spec.py` et
`native_messaging_compat_spec.py`.

| Priorité | macOS | Linux |
|---|---|---|
| 1 | `<user-data-dir>/NativeMessagingHosts`, défaut `~/Library/Application Support/Bluelium/NativeMessagingHosts` | `<user-data-dir>/NativeMessagingHosts`, AppImage : `$XDG_CONFIG_HOME/bluelium/NativeMessagingHosts` (défaut `~/.config/bluelium/NativeMessagingHosts`) |
| 2 | `~/Library/Application Support/Google/Chrome/NativeMessagingHosts` | `$CHROME_CONFIG_HOME/google-chrome/NativeMessagingHosts`, sinon XDG puis `~/.config` |
| 3 | `~/Library/Application Support/Chromium/NativeMessagingHosts` (**ajout de ce lot**) | `$XDG_CONFIG_HOME/chromium/NativeMessagingHosts`, sinon `~/.config/chromium/NativeMessagingHosts` |
| 4 | `/Library/Application Support/Chromium/NativeMessagingHosts` | `/etc/chromium/native-messaging-hosts` |
| 5 | `/Library/Google/Chrome/NativeMessagingHosts` | `/etc/opt/chrome/native-messaging-hosts` |

Les trois premiers emplacements restent soumis à `NativeMessagingUserLevelHosts`.
Le premier fichier trouvé gagne : un manifeste invalide dans le profil n'est pas
contourné. Aucun changement d'`allowed_origins`, permission d'extension ou contrôle
d'exécutable côté Chromium. Un `--user-data-dir` personnalisé reste prioritaire.
Les anciens lanceurs tar peuvent utiliser `~/.config/helium-glyphe` : indiquer
explicitement leur cible au script ci-dessous.

## Installation des manifestes officiels existants

`tools/native-messaging.py` fonctionnait seulement avec les chemins Linux et
ciblait encore `helium-glyphe`. Il reconnaît maintenant macOS/Linux et cible
Bluelium. Lecture seule sans `--link` :

```sh
python3 tools/native-messaging.py
python3 tools/native-messaging.py --link
python3 tools/native-messaging.py --link --target /profil-personnalise/NativeMessagingHosts
python3 tools/native-messaging.py --link --manifest /chemin/com.openai.codexextension.json
```

Il cherche les manifestes Claude/Codex dans Chrome, Chromium, Helium et les
emplacements système, valide leur nom, type stdio, exécutable absolu et exécutable,
et au moins une origine officielle explicite. Il lie les fichiers sans modifier
leur contenu et sans écraser de fichier ou de lien, même cassé. Corriger un
manifeste cible périmé reste une action manuelle. Les champs `claude_present` et
`codex_present` signifient « valide dans la cible » ; ils ne certifient ni le
compte, ni le fallback Chromium, ni la détection par l'application externe.
Le script ne crée pas d'hôte absent. Installer/configurer d'abord l'intégration
avec le client officiel, puis relancer le diagnostic.

## Claude Code : origine de la non-détection

Version inspectée ici : **2.1.325**, binaire local
`~/.local/share/claude/versions/2.1.325` (via `~/.local/bin/claude`). Analyse en
lecture seule de son module embarqué de découverte, sans lire les profils réels.

Pour l'extension `fcoeoabgfenejglbffodgkkbkcdhcgfn`, le détecteur énumère les
sous-dossiers `Default` et `Profile *`, puis cherche `Extensions/<id>`. Il ne
parcourt pas les profils de tous les navigateurs Chromium présents sur le disque.
Sa liste fixe est :

| Famille | Racine macOS sous `~/Library/Application Support/` | Racine Linux sous `~/` |
|---|---|---|
| Chrome | `Google/Chrome` | `.config/google-chrome` |
| Brave | `BraveSoftware/Brave-Browser` | `.config/BraveSoftware/Brave-Browser` |
| Arc | `Arc/User Data` | aucune |
| Edge | `Microsoft Edge` | `.config/microsoft-edge` |
| Chromium | `Chromium` | `.config/chromium` |
| Vivaldi | `Vivaldi` | `.config/vivaldi` |
| Opera | `com.operasoftware.Opera` | `.config/opera` |

**Helium (`net.imput.helium`) et Bluelium (`Bluelium`, `.config/bluelium`) sont
absents.** La version inspectée utilise littéralement `.config` pour cette
recherche Linux, sans XDG dans ce module. Modifier uniquement le manifeste ou le
nom de processus Bluelium ne corrige donc pas le statut « extension installée ».

Le choix de l'application à ouvrir est une autre liste : `/Applications/<nom>.app`
sur macOS (Google Chrome, Brave Browser, Arc, Microsoft Edge, Chromium, Vivaldi,
Opera) ; binaires `google-chrome`/`google-chrome-stable`, `brave-browser`/`brave`,
`microsoft-edge`/`microsoft-edge-stable`, `chromium`/`chromium-browser`,
`vivaldi`/`vivaldi-stable`, `opera` sous Linux. La recherche d'extension inspectée
n'est pas conditionnée par un processus en cours.

Le setup Claude installe
`com.anthropic.claude_code_browser_extension.json` dans les dossiers
`NativeMessagingHosts` des mêmes familles. L'hôte officiel est un lanceur vers
Claude avec `--chrome-native-host`. Bluelium peut déjà lire le manifeste Chrome ;
le lot ajoute le secours Chromium macOS et l'installation directe dans Bluelium.
Cela corrige les chemins du **transport** qui sont de notre ressort.

Pour essayer l'intégration avec le transport installé : installer l'extension
Claude officielle dans Bluelium, s'y connecter, lancer `claude --chrome`, puis
`/chrome` et ouvrir manuellement la page de reconnexion dans Bluelium si le client
ouvre un autre navigateur. Le statut peut encore être erroné tant qu'Anthropic
n'ajoute pas Bluelium à ses listes. Aucun faux profil Chrome, renommage
d'exécutable, modification du binaire Claude ou du cache de plugins n'est réalisé.
Une prise en charge complète requiert une évolution du client externe.

La [documentation Anthropic](https://code.claude.com/docs/en/chrome) décrit les
navigateurs reconnus, la reconnexion et les contraintes de compte. Le support
annoncé ne constitue pas une validation spécifique à Bluelium.

## ChatGPT / Codex : manifeste, profils et processus

Sources locales inspectées : plugin navigateur **26.1027.51404**,
`scripts/extension-ids.json`, `chromium-browser-diagnostics.mjs`,
`check-extension-installed.js`, `check-native-host-manifest.js`,
`installed-browsers.js`, `chrome-is-running.js` et `open-chrome-window.js`.
Ni installation du plugin ni modification de ses fichiers pendant ce diagnostic.
Le connecteur est `com.openai.codexextension`, avec l'extension ChatGPT
`hehggadaopoacecdllhhajmbjkdcmajg` (et l'identifiant Edge
`odlomjlbamekndcpllcnffbgeohgkmjh` dans la configuration locale).

La configuration énumère Chrome, Edge, Brave, Opera et Vivaldi. Elle ne contient
ni Helium ni Bluelium. Pour la famille Chrome :

- profil macOS : `~/Library/Application Support/Google/Chrome` ; Linux :
  `google-chrome` sous CHROME_CONFIG_HOME, sinon XDG_CONFIG_HOME, sinon `~/.config` ;
- sélection du profil à partir de `Local State` (`last_used`, profils actifs),
  puis dossiers contenant Preferences, avec inspection Preferences/Secure
  Preferences et des extensions ;
- manifeste vérifié par défaut : le dossier Chrome, pas celui de Bluelium ;
- application macOS : `Google Chrome.app`, bundle `com.google.Chrome`, processus
  `Google Chrome` / `Google Chrome Helper` ; Linux : processus `chrome` et
  commandes Chrome/Chromium énumérées dans la configuration.

Bluelium conserve son bundle `io.github.matthieuleconte1.bluelium`, son application
`Bluelium.app` et le binaire Chromium `Contents/MacOS/Helium` ; l'AppImage lance
`helium` avec son identité propre `bluelium.desktop`. Il ne faut pas les renommer
pour tromper un détecteur : les critères processus/bundle restent externes.

Les scripts **de diagnostic** OpenAI disposent toutefois d'overrides pris en
charge dans leur code. Pour les lancer sur un profil Bluelium, sans faux profil :

```sh
# macOS : variables à fournir au processus exécutant les diagnostics.
export CODEX_CHROMIUM_USER_DATA_DIR="$HOME/Library/Application Support/Bluelium"
export CODEX_CHROMIUM_NATIVE_HOST_MANIFEST_PATH="$CODEX_CHROMIUM_USER_DATA_DIR/NativeMessagingHosts/com.openai.codexextension.json"
# Linux : même principe avec ${XDG_CONFIG_HOME:-$HOME/.config}/bluelium.
```

`CODEX_CHROMIUM_PREFERENCES_PATH` peut aussi cibler un fichier Preferences précis.
Ces paramètres corrigent le chemin inspecté par les diagnostics ; ils ne changent
pas les listes d'applications/processus et ne prouvent pas que l'application
bureau transmet ces variables à son service navigateur. Le script Bluelium
installe seulement le manifeste officiel existant dans le bon profil.

Configurer le connecteur depuis ChatGPT bureau et suivre le setup officiel. La
CLI Codex et le navigateur de l'application bureau sont des intégrations
distinctes ; partager les manifestes ne crée pas un outil navigateur dans une
CLI. Voir la [documentation navigateur](https://learn.chatgpt.com/docs/browser)
et celle de l'[extension](https://learn.chatgpt.com/docs/chrome-extension).
Aucune connexion ChatGPT/Codex de bout en bout n'est revendiquée pour ce lot.

## Vérifications

`python3 tools/test-native-messaging.py` : six tests avec racines utilisateur
jetables (macOS/Linux, chemins XDG/Chrome, liens idempotents, lien cassé protégé,
JSON/origines invalides). Aucun profil réel ni compte n'est utilisé.

`tools/validate-native-messaging.mjs` reste disponible pour un test de protocole
avec extension et hôte jetables. Le diagnostic Linux précédent avait obtenu
`pong` de l'hôte Claude ; ce résultat ancien ne valide pas le binaire de ce lot.
Application des specs sur l'arbre macOS montée : `docs/verification-lot1.md`.
Aucune compilation ni nouvelle validation de transport ou de compte à l'exécution.
