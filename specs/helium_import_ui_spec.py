"""Bluelium : écran de bienvenue (chrome://setup) — reprendre le profil Helium.

Carte en tête de la page « Importer » de l'onboarding Helium (Svelte), visible
avant la détection générale des navigateurs (elle ne demande pas
l'autorisation d'accès aux autres navigateurs). Choix du profil s'il y en a
plusieurs, détail des données, états : Helium ouvert, import en cours,
partiel, échec, terminé. Contrat : helium_import_spec.py (placé avant).
Le polyfill de développement (vite dev, hors navigateur) répond aux deux
messages pour vérifier l'écran sans compiler Chromium.
"""
from pathlib import Path

REF = Path(__file__).parent / 'reference' / 'bluelium' / 'onboarding'
OB = 'components/helium_onboarding/src/'

NEW_FILES = {
  OB + 'components/HeliumImportCard.svelte':
      (REF / 'HeliumImportCard.svelte').read_text(),
}

EDITS = [
  (OB + 'pages/DataImport.svelte',
   '    import BrowserImportGraphic from "../components/BrowserImportGraphic.svelte";\n',
   '    import BrowserImportGraphic from "../components/BrowserImportGraphic.svelte";\n'
   '    // Bluelium : reprendre le profil Helium.\n'
   '    import HeliumImportCard from "../components/HeliumImportCard.svelte";\n'),
  (OB + 'pages/DataImport.svelte',
   '            Icon={IconTransferIn}\n'
   '        />\n'
   '        <div class="import-content">\n',
   '            Icon={IconTransferIn}\n'
   '        />\n'
   '        <!-- Bluelium -->\n'
   '        <div class="helium-import-slot">\n'
   '            <HeliumImportCard />\n'
   '        </div>\n'
   '        <div class="import-content">\n'),
  (OB + 'pages/DataImport.svelte',
   '    .import-content {\n'
   '        display: grid;\n'
   '    }\n',
   '    .import-content {\n'
   '        display: grid;\n'
   '    }\n\n'
   '    /* Bluelium */\n'
   '    .helium-import-slot {\n'
   '        width: 100%;\n'
   '    }\n\n'
   '    .helium-import-slot:not(:empty) {\n'
   '        margin-bottom: var(--gap-2);\n'
   '    }\n'),

  # Polyfill de développement : profil Helium simulé.
  (OB + 'lib/chrome-send-polyfill.ts',
   "    } else if (msg === 'getExtensions') {\n",
   "    } else if (msg === 'getHeliumImportState') {\n"
   "        // Bluelium : deux profils Helium simulés, Helium fermé.\n"
   "        cr.webUIResponse(params![0], true, {\n"
   "            status: 'available',\n"
   "            sourceBusy: false,\n"
   "            completed: heliumImported,\n"
   "            busy: false,\n"
   "            profiles: [\n"
   "                { id: 'Default', name: 'Default', items: 0b10011011 },\n"
   "                { id: 'Profile 1', name: 'Profile 1', items: 0b00000011 },\n"
   "            ],\n"
   "        });\n"
   "    } else if (msg === 'importHeliumProfile') {\n"
   "        setTimeout(() => {\n"
   "            heliumImported = true;\n"
   "            cr.webUIResponse(params![0], true, {\n"
   "                status: 'finished', requestedItems: 155, finishedItems: 155,\n"
   "            });\n"
   "        }, 1500);\n"
   "    } else if (msg === 'getExtensions') {\n"),
  (OB + 'lib/chrome-send-polyfill.ts',
   "const prefs: Record<string, unknown> = {\n",
   "// Bluelium : état simulé de l'import Helium.\n"
   "let heliumImported = false;\n\n"
   "const prefs: Record<string, unknown> = {\n"),
]
