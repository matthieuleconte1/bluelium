"""Bluelium : Shimmer cherche avec le moteur du navigateur, et raccourcis IA.

Moteur : le réglage par défaut de Shimmer est « Celui du navigateur »
(engine `browser`), qui appelle chrome.search.query. Cette API n'existe que
pour les extensions ; dans la page interne de Bluelium, Shimmer retombait donc
sur DuckDuckGo. glyphe-shim.js fournit chrome.search.query : le gestionnaire
natif construit l'adresse avec le moteur par défaut du profil
(TemplateURLService), et la page y navigue. Sans moteur par défaut (politique),
Shimmer garde son repli.

Raccourcis : les profils neufs commencent avec Claude et ChatGPT, puis GitHub
et YouTube. Les raccourcis déjà enregistrés ne changent pas.

S'applique après shimmer-sessions et shimmer-appearance (même fichier).
"""

UI = 'chrome/browser/ui/webui/new_tab_page/glyphe_shimmer_ui.cc'
JS = 'third_party/shimmer/assets/index-kwRkEiyG.js'

NEW_FILES = {}
EDITS = [
  (UI,
   '#include "content/public/browser/web_ui_message_handler.h"\n',
   '#include "content/public/browser/web_ui_message_handler.h"\n'
   '#include "chrome/browser/search_engines/template_url_service_factory.h"  // nogncheck\n'
   '#include "components/search_engines/template_url.h"\n'
   '#include "components/search_engines/template_url_service.h"\n'),
  (UI,
   '  chrome.runtime = chrome.runtime || {};\n',
   '  // Bluelium : recherche avec le moteur par défaut du navigateur.\n'
   '  chrome.search = {\n'
   '    query({text}) {\n'
   '      return call(\'glypheSearchUrl\', String(text || \'\')).then((url) => {\n'
   '        location.href = url ||\n'
   '            \'https://duckduckgo.com/?q=\' + encodeURIComponent(text || \'\');\n'
   '      });\n'
   '    },\n'
   '  };\n'
   '  chrome.runtime = chrome.runtime || {};\n'),
  (UI,
   '        "glypheRestore",\n',
   '        "glypheSearchUrl",\n'
   '        base::BindRepeating(&GlypheShimmerHandler::HandleSearchUrl,\n'
   '                            base::Unretained(this)));\n'
   '    web_ui()->RegisterMessageCallback(\n'
   '        "glypheRestore",\n'),
  (UI,
   '  raw_ptr<Profile> profile_;\n'
   '  base::CancelableTaskTracker favicon_tasks_;\n',
   '  // Bluelium : adresse de recherche du moteur par défaut, vide sans moteur.\n'
   '  void HandleSearchUrl(const base::ListValue& args) {\n'
   '    AllowJavascript();\n'
   '    std::string url;\n'
   '    TemplateURLService* service =\n'
   '        TemplateURLServiceFactory::GetForProfile(profile_);\n'
   '    const TemplateURL* engine =\n'
   '        service ? service->GetDefaultSearchProvider() : nullptr;\n'
   '    if (engine && args.size() > 1 && args[1].is_string()) {\n'
   '      url = engine->url_ref().ReplaceSearchTerms(\n'
   '          TemplateURLRef::SearchTermsArgs(\n'
   '              base::UTF8ToUTF16(args[1].GetString())),\n'
   '          service->search_terms_data());\n'
   '    }\n'
   '    ResolveJavascriptCallback(args[0], base::Value(url));\n'
   '  }\n'
   '\n'
   '  raw_ptr<Profile> profile_;\n'
   '  base::CancelableTaskTracker favicon_tasks_;\n'),
  (JS,
   'links:[{title:`GitHub`,url:`https://github.com/`},{title:`YouTube`,url:`https://www.youtube.com/`},{title:`Helium`,url:`https://helium.computer/`}]',
   'links:[{title:`Claude`,url:`https://claude.ai/`},{title:`ChatGPT`,url:`https://chatgpt.com/`},{title:`GitHub`,url:`https://github.com/`},{title:`YouTube`,url:`https://www.youtube.com/`}]'),
]
