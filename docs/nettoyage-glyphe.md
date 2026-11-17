# Nettoyage du nom Glyphe

Le panneau initial et ses onglets sont réunis dans assistant_spec.py ; une seule entrée SERIES subsiste. Les fichiers créés finaux ont été comparés par assertion à la composition des deux anciennes specs ; les éditions des fichiers existants ont été conservées dans leur ordre puis composées lorsqu'une substitution porte sur le résultat précédent. Application sur l'arbre macOS préparé réussie ; les finitions ultérieures du panneau ont été réappliquées. Aucune compilation.

Conserver les clés glyphe.* : elles portent les préférences des profils installés. Une migration explicite serait nécessaire avant renommage. Conserver également les identifiants d'actions et de panneau (personnalisation persistée), les chemins de sources et patches/glyphe : leur changement exige une mise à jour coordonnée de toutes les specs.

Linux : /root/glyphe apparaît dans autobuild/autobuild.sh (racine de travail, releases, github.env), make-appimage.sh (appimagetool), les scripts de déploiement et services. Ne pas le renommer sans inventorier la machine et déplacer ensemble services, chemins, secrets et historiques. Le verrou /run/glyphe-autobuild.lock doit rester commun aux anciennes et nouvelles installations pour éviter deux builds concurrents.

Le lanceur, le fichier desktop et l'AppImage portent déjà le nom Bluelium ; le profil ~/.config/bluelium ne doit pas changer. Les noms Helium résiduels peuvent désigner le binaire amont et ses interfaces de packaging.

Les commentaires de référence à assistant_tabs_spec.py ont été actualisés. Le reste des noms internes est proposé à une migration coordonnée plutôt qu'à un remplacement global susceptible de casser les ancres ou les profils.
