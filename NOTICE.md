# Marques et éléments tiers

- **Helium** est un projet d'imputnet (https://github.com/imputnet/helium).
  Bluelium est un fork non officiel ; il n'utilise pas le logo de Helium comme
  identité propre.
- **Claude** (Anthropic), **ChatGPT** (OpenAI), **Gemini** (Google) et
  **Le Chat** (Mistral AI) sont des marques de leurs propriétaires. Les patchs
  `assistant-*` embarquent leurs favicons (16 et 32 px, `assets/icons/`),
  affichées en monochrome, uniquement pour identifier chaque service dans le
  panneau latéral. Les logos en grand format ne sont pas inclus.
- **Shimmer Tab** (https://github.com/dmitthedazed/shimmer-tab) est téléchargé
  au moment du build (GPL-3.0).
- **Instrument Sans** : SIL Open Font License 1.1, voir
  `assets/OFL-InstrumentSans.txt`.
- **Material Symbols** (Google) : Apache 2.0.

- **PDF.js 6.5.438** (Mozilla Foundation et contributeurs,
  https://github.com/mozilla/pdf.js/releases/tag/v6.5.438) : Apache-2.0.
  La distribution officielle est téléchargée avec vérification SHA-256 dans
  `downloads.ini`, puis embarquée hors ligne. Sa licence `LICENSE`, les avis
  intégrés aux sources et ceux des ressources (CMaps Adobe, polices et
  décodeurs) sont conservés dans le paquet de ressources du navigateur.
  Modifications Bluelium : pont vers le flux PDF de Chromium, entrée du lecteur,
  palette de l’interface et Instrument Sans (SIL OFL 1.1).
