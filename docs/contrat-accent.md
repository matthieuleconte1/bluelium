# Accent personnalisé

Diagnostic : `GetGlyphePrismPalette` renvoyait nullptr pour toute graine
absente de `kThemes`. La pipette quittait donc la palette Prism et utilisait
les couleurs dérivées de Helium. Shimmer et le bouton IA lisaient déjà
`ThemeService::GetUserColor`, créant un rendu incohérent.

La spec custom_accent conserve les surfaces du Prism clair/sombre et remplace
son accent par la couleur utilisateur opaque. Le texte sur accent utilise
GetColorWithMaxContrast. Les thèmes système, contraste élevé, couleurs forcées,
OLED et nuit conservent leur priorité existante.

Frontend : utiliser le sélecteur Chromium existant et son API de couleur
utilisateur ; ne pas créer une préférence parallèle. La persistance reste celle
de Chromium. Shimmer utilise déjà GetUserColor dans shimmer_appearance_spec.py.
Vérifier après compilation : pipette, redémarrage, clair/sombre, bouton IA,
Shimmer, sélection, contraste élevé et retour à une pastille prédéfinie.

Validation réalisée : application de la spec sur l’arbre macOS préparé et
régénération du patch. Aucun build C++, test de persistance ou contrôle visuel.
La durée de vie du pointeur repose sur la consommation synchrone des mixers ;
à contrôler en revue C++ avant intégration.
