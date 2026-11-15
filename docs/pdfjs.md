# Lecteur PDF.js de Bluelium

Travail non commité, destiné à la validation. Aucune publication de release.

## Intégration

`specs/pdfjs_spec.py`, ajoutée en fin de `specs/SERIES`, s'applique sur macOS
et Linux. Ses sources lisibles sont dans `specs/pdfjs/`. La distribution
Mozilla PDF.js **6.5.438** est figée dans `downloads.ini` :

- archive : https://github.com/mozilla/pdf.js/releases/download/v6.5.438/pdfjs-6.5.438-dist.zip ;
- SHA-256 : `fcbe9ba21d9911843e3502adc178a7f549a524a4055f887bedc942e5490c6ba1` ;
- cette somme a été comparée au champ `digest` de la release officielle et
  recalculée sur l'archive téléchargée ;
- extraction dans `third_party/pdfjs`, comme Shimmer Tab ;
- lecteur, worker, CMaps, polices, décodeurs WASM, traductions et licences
  sont empaquetés dans les ressources du navigateur.

Le gestionnaire MIME de l'extension PDF intégrée reste responsable des
navigations. Seul son point d'entrée interactif devient
`pdfjs/web/viewer.html`. Le lecteur et PDFium de **l'aperçu d'impression**
Chromium sont conservés : `chrome://print` n'est pas remplacé.

Ce choix conserve l'URL d'origine et les mécanismes d'interception de
Chromium pour les liens, fichiers locaux, documents intégrés et réponses
POST. Une WebUI avec une redirection puis un nouveau `fetch(url)` aurait
perdu le corps d'une réponse POST, les URL temporaires ou certains contextes
d'authentification.

Deux fonctions privées sont ajoutées à `pdfViewerPrivate` :

- `readPdfStream` prend uniquement le flux appartenant au document appelant,
  sans accepter d'URL ou d'identifiant d'un autre document. Le flux est
  consommé une seule fois, en blocs de **256 Kio maximum**, avec
  contre-pression et vérification de `URLLoaderClient::OnComplete` ;
- `getBlueliumTheme` lit les couleurs réelles du navigateur. Les lecteurs
  visibles se mettent à jour toutes les deux secondes et à la reprise de
  focus, sans rechargement du PDF.

Le lecteur Mozilla complet conserve ses fonctions de recherche, formulaires,
annotations, enregistrement et impression. Ses scripts PDF utilisent son bac
à sable QuickJS local et respectent le réglage JavaScript du site. La CSP
n'ajoute pas de permission de lecture générale des URL ; les connexions du
lecteur sont limitées à ses ressources propres, `blob:` et `data:`. Les
fonctions d'IA qui téléchargent un modèle et la vérification distante des
signatures sont désactivées.

L'interface utilise Instrument Sans embarquée (OFL conservée), les couleurs
sémantiques de Bluelium, des commandes arrondies et un focus clavier visible.
Les polices et couleurs du contenu PDF ne sont pas remplacées. Le filtre
Nuit de Bluelium continue à s'appliquer au contenu comme aux autres pages.

## PDF téléchargés

La valeur par défaut de `download.open_pdf_in_system_reader` devient `true`.
Les chemins existants de Chromium gèrent la bulle, `chrome://downloads` et
l'ouverture à la fin du téléchargement avec l'application système.
Sous Linux, l'ouverture est déléguée au mécanisme système existant
(`xdg-open` selon l'environnement) ; aucune commande shell n'est ajoutée.

Chromium associe cette préférence à l'ouverture automatique des PDF : avec
la valeur `true`, un PDF téléchargé peut donc s'ouvrir dès sa fin. Le menu du
téléchargement « Toujours ouvrir avec le lecteur système » permet de
revenir au comportement précédent. Une valeur `false` explicitement
préexistante dans un profil n'est pas écrasée. Le réglage qui force le
**téléchargement de tous les PDF** reste distinct et n'est pas changé.

## Reproduire le build sur l'arbre existant

`SKIP_FETCH=1` ne réapplique **pas** la série. Il faut télécharger/vérifier la
nouvelle dépendance, puis appliquer la nouvelle spec explicitement. Ne pas
relancer la série complète sur cet arbre : son premier patch figé n'est pas
idempotent.

```sh
# Depuis le dépôt, après extraction vérifiée de l'archive dans third_party/pdfjs :
python3 tools/apply_spec.py /Volumes/BlueliumBuild/helium-macos/build/src \
  specs/pdfjs_spec.py /Volumes/BlueliumBuild/pdfjs.patch
# Donner un suffixe de test à /Volumes/BlueliumBuild/series.version, puis :
BLUELIUM_MAC_WORK=/Volumes/BlueliumBuild SKIP_FETCH=1 PUBLISH=0 scripts/build-macos.sh
```

Sur un arbre Linux neuf, le téléchargement passe par `downloads.ini` puis la
série habituelle : aucune copie manuelle n'est nécessaire à l'auto-build.

## Vérifications reproductibles

```sh
node --test tools/tests/pdfjs-bridge.test.mjs
python3 tools/pdfjs-smoke-server.py
```

Le serveur écoute uniquement `127.0.0.1:8765` et écrit un PDF local dans
`/tmp/bluelium-test.pdf`. La page d'essai propose : un PDF de deux pages avec
champ AcroForm et annotation, un téléchargement forcé, une redirection, une
réponse POST dont un GET retourne 405 et une réponse volontairement tronquée.
Le PDF local sert aussi à vérifier une ouverture ou un glisser-déposer.

## Résultats réels du 15 novembre 2026

- Chromium **157.0.8103.50**, Helium **0.21.2.1**, arbre macOS arm64
  existant dans `/Volumes/BlueliumBuild/helium-macos/build/src`.
- Deux builds aboutis avec `SKIP_FETCH=1`, PGO conservé et `PUBLISH=0` :
  `0.21.2.1-g655a096-pdf1` puis `0.21.2.1-g655a096-pdf2`. Le second est
  le livrable final ; il inclut les dernières corrections du lecteur.
- La nouvelle spec seule a été appliquée explicitement à l'arbre existant.
  Les autres travaux apparus en parallèle dans la série n'ont pas été
  réappliqués par cette tâche.
- Quatre tests Node passent : octets et sauvegarde par instance, erreur
  réseau, titre d'un PDF intégré et blocage JavaScript du site.
- Ancres uniques ; application depuis les fichiers restaurés à leur état
  antérieur et réapplication donnent le même patch.
- Inventaire des 419 ressources vérifié ; licence PDF.js présente dans le
  `about_credits.html` généré par Chromium.

Un lancement natif de la copie de `out/Default/Helium.app`, avec un profil
jetable et les URL d'essai, a permis de vérifier **par les journaux**, sans
pilotage d'un autre navigateur :

- cinq chargements PDF.js réussis : HTTP, fichier local, réponse POST,
  PDF intégré à la page HTML et document de 2 Mio (plusieurs blocs) ;
- un seul POST vers `/post.pdf`, aucun GET de rechargement vers cette URL ;
- refus du document volontairement tronqué avec
  `net::ERR_CONTENT_LENGTH_MISMATCH` ;
- téléchargement de `bluelium-test.pdf` puis ouverture automatique par le
  système : l'historique du profil indique `state=1`, `opened=1`,
  `received_bytes=total_bytes=1497`, et `lsof` constate qu'**Aperçu** détient
  ce fichier. La préférence PDF n'avait pas été définie dans ce profil :
  c'est bien la nouvelle valeur par défaut qui a été exercée.

Le serveur et le navigateur de test ont été arrêtés après ces contrôles.
Le document de test ouvert dans Aperçu n'a pas été fermé.

**Vérification visuelle non réalisée.** Computer Use a échoué à sélectionner
la fenêtre Helium compilée (`cgWindowNotFound`, puis résolution ambiguë de
l'identité d'application). Aucun basculement vers Chrome ou un navigateur
intégré. L'aspect clair/sombre, les clics dans la bulle et `chrome://downloads`,
la recherche interactive, l'édition/sauvegarde des formulaires et annotations,
le glisser-déposer et le dialogue d'impression n'ont donc pas été validés
manuellement. Les fonctions PDF.js correspondantes sont conservées, mais il
reste nécessaire de les essayer dans l'interface avant adoption.

### DMG final

`/Volumes/BlueliumBuild/releases/bluelium-0.21.2.1-g655a096-pdf2-macos-arm64.dmg`

SHA-256 : `ceb68541772b576b38c8fb0b16025e84a5b28430dd5afd20745ee38ec80f5489`.

La somme `.sha256` a été vérifiée et `hdiutil verify` déclare l'image valide.
Le script de paquet a signé l'application ad hoc et vérifié sa signature.
Aucun commit, push ou publication de release.

Journaux locaux : `/Volumes/BlueliumBuild/pdf1-build.log`,
`/Volumes/BlueliumBuild/pdf2-build.log`, `/Volumes/BlueliumBuild/pdf2-runtime.log`
et `/Volumes/BlueliumBuild/pdfjs-smoke-server.log`.

## Limites

- Les blocs sont bornés dans le navigateur, mais le document complet est
  réassemblé dans le renderer avant son ouverture par PDF.js. Les très gros
  PDF nécessitent donc davantage de mémoire et attendent la fin du flux ;
  cette version ne conserve pas le chargement HTTP par plages de PDFium.
- Les boutons et menus PDF.js sont conservés ; ce travail n'essaie pas de
  reproduire toutes les API de scripting du plugin PDFium pour les pages
  qui le pilotent par `postMessage`.
- La mise à jour de l'interface PDF.js n'est pas automatique : changer la
  version exige de vérifier le SHA-256, les ancres de la spec et l'inventaire
  `specs/pdfjs/files.txt`, puis de refaire les essais.
- Linux est visé par la même spec mais doit être compilé et testé sur la
  machine Linux avant toute validation de cette plateforme.
- PDF.js refuse une base `file:` pour les liens relatifs : le PDF local
  se charge, mais cette résolution de liens reste limitée (avertissement
  observé dans le worker).
- Les fichiers PDF protégés, XFA complexes, signatures cryptographiques et
  fonctions d'accessibilité nécessitent des essais supplémentaires.

Licence : Apache-2.0, avis conservés dans les ressources et dans `NOTICE.md`.
Les modifications locales sont indiquées dans `third_party/pdfjs/README.chromium`.
