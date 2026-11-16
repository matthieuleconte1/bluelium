# Import Helium dans la bienvenue Bluelium

## Page et sources

La page existante est `chrome://setup` (alias `bluelium://setup`). Helium
l'ouvre pour un profil normal dont `helium.completed_onboarding` est false,
sauf `--no-first-run`. Le contrôleur est
`chrome/browser/ui/webui/onboarding/onboarding_page_ui.cc`, le handler existant
`onboarding_handler.{cc,h}` dans le même dossier. La spec backend
`helium_import_spec.py` y ajoute `BlueliumHeliumImportHandler`.

Le frontend vient de l'archive `onboarding` de `helium/downloads.ini`, version
`202610161403`, extraite dans `components/helium_onboarding/`. Ce sont des sources
Svelte, pas une page Lit de `chrome/browser/resources` :

- `src/pages/Welcome.svelte` : accueil ;
- `src/pages/DataImport.svelte` : étape d'import existante ;
- `src/lib/browser/importer.ts` : appels navigateur et état ;
- `src/lib/browser/setup.ts`, `src/lib/onboarding-flow.ts` et `src/App.svelte` : parcours.

Ajouter l'offre Helium dans Welcome ou DataImport et appeler les messages
ci-dessous depuis importer.ts. Une spec Python séparée peut modifier directement
`components/helium_onboarding/src/...` après `helium-import.patch`. Le GN
`components/helium_onboarding/BUILD.gn` reconstruit ces sources avec Vite, puis
produit le GRD et le pak. Ne pas modifier un JS haché compilé ni l'archive distante.

## Messages et réponses

Utiliser `sendWithPromise` fourni par `src/lib/cr/cr.ts` (export du module cr).
Les identifiants de callback sont ajoutés par cette fonction, pas par le code UI.

```ts
const state = await sendWithPromise('getHeliumImportState');
const result = await sendWithPromise('importHeliumProfile', 'Default');
```

`getHeliumImportState` renvoie :

```ts
{
  status: 'available' | 'not_found' | 'same_profile',
  profiles: Array<{id: string, name: string, items: number}>,
  sourceBusy?: boolean,
  completed: boolean,
  busy: boolean,
}
```

Afficher l'offre si available, non completed, non busy. `name` est actuellement
le nom du dossier (`Default`, `Profile 1`…), pas le nom personnel du compte.
`sourceBusy` demande de fermer Helium. Ne pas retirer cette vérification côté UI.
Les chemins ne sont pas exposés et aucun chemin arbitraire n'est accepté.

`importHeliumProfile(id)` recontrôle le profil sur disque avant de commencer.
La promesse reste en attente pendant l'import : désactiver le bouton et conserver
la page ouverte. Résultat :

```ts
{
  status: 'finished' | 'partial' | 'failed' | 'busy' | 'source_busy' |
          'unavailable' | 'invalid_profile' | 'not_found' | 'same_profile',
  requestedItems?: number,
  finishedItems?: number,
}
```

Masques : historique `1`, favoris `2`, extensions `128`. Les catégories
absentes ne sont pas demandées. `finished` signifie que l'importeur Chromium a
terminé toutes les catégories demandées ; ses notifications ne fournissent ni
comptage ni preuve de succès pour chaque entrée. Ne pas afficher « tout le profil
copié ». `partial` peut avoir déjà ajouté des données. Le backend interdit une
seconde importation terminée (`glyphe.helium_import.completed`, défaut false) et
les imports concurrents d'un même profil. Une fermeture/recharge de la page
annule la suite ; les données déjà importées ne sont pas supprimées.

Les erreurs d'arguments invalides sont ignorées ; le frontend doit respecter
les signatures. L'import n'active aucun service Helium et ne copie aucun
consentement. L'installation d'extensions via l'importeur existant peut exiger
l'activation des services d'extensions dans le parcours Helium ; présenter un
résultat limité aux notifications reçues, sans promettre la restauration de leur
session authentifiée.

## Portée de l'import et migrations intégrales existantes

Sources recherchées : `~/Library/Application Support/net.imput.helium` sur macOS,
`$XDG_CONFIG_HOME/net.imput.helium` (défaut `~/.config/net.imput.helium`) sur Linux.
Dossiers Default/Profile *, non symboliques ; rejet si source et destination
coïncident ou sont imbriquées. Le travail disque est sur ThreadPool, l'écriture
dans les services du profil ouvert utilise `BraveExternalProcessImporterHost` et
`ProfileWriter`, déjà fournis par Helium.

Cette offre importe favoris, historique et extensions prises en charge par
l'importeur Chrome/Helium. Elle ne clone pas les onglets, les cookies, les mots de
passe, les réglages ou les données internes des extensions. La copie intégrale
d'un profil ouvert n'est pas sûre ; la clé macOS est en outre propre à Bluelium.

`tools/migrate-helium-macos.sh` reste l'outil distinct de migration intégrale,
à lancer volontairement avec les deux navigateurs fermés : rsync du profil avec
exclusion des caches/verrous, sauvegarde du profil Bluelium et copie de la clé
« Helium Storage Key » vers « Bluelium Storage Key ». Il exige l'autorisation du
trousseau et n'est pas invoqué par la WebUI.

Le commit Linux `c03092a` copiait automatiquement le répertoire Helium avant
le premier démarrage AppImage, puis supprimait les trois Singleton* ; il copiait
aussi Local State, les caches et le consentement d'onboarding. Ce lot retire cette
copie implicite d'`autobuild/AppRun`, afin que le nouveau profil arrive à l'écran
de choix. Les profils déjà copiés ne sont pas modifiés. `BLUELIUM_NO_IMPORT` n'a
plus d'effet car le lanceur n'importe plus rien.

## Vérification

Application réelle de la spec sur l'arbre Chromium macOS : voir
`docs/verification-lot1.md`. Frontend fourni par `helium_import_ui_spec.py` (Claude), placé juste après la
spec backend. Import à l'exécution et comportement Linux non testés.
Aucun profil utilisateur ni trousseau réel n'a été utilisé pour les vérifications.
