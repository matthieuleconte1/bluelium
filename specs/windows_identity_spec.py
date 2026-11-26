r"""Bluelium (Windows) : identité propre, pour s'installer à côté de Helium.

Helium Windows (patch change-branding de helium-windows) déclare son mode
d'installation dans chrome/install_static/chromium_install_modes.h : dossier
d'installation et de profil (%LOCALAPPDATA%\imput\Helium), GUID de
l'application, ProgID des documents HTML et PDF, schéma d'URL, CLSID COM
(notifications, service d'élévation, traçage). Avec les mêmes valeurs,
Bluelium écraserait l'installation, le profil et les associations de Helium.

Après :
  - dossier %LOCALAPPDATA%\Bluelium (installation et « User Data »), sans
    dossier de société, comme Chromium ;
  - nom d'application, AppUserModelID et ProgID « Bluelium » ;
  - schéma d'URL bluelium:, nouveaux GUID et CLSID ;
  - stratégies d'entreprise lues sous HKLM\SOFTWARE\Policies\Bluelium.
Les noms internes de l'installateur (helium.7z, Helium-bin) ne changent pas :
on ne les voit pas. L'installateur NSIS est renommé par
scripts/build-windows.py.
Plateforme : win seulement (voir specs/SERIES).
"""

H = 'chrome/install_static/chromium_install_modes.h'
POLICY = 'components/policy/tools/template_writers/writer_configuration.py'

NEW_FILES = {}

EDITS = [
  (H,
   'inline constexpr wchar_t kCompanyPathName[] = L"imput";\n',
   'inline constexpr wchar_t kCompanyPathName[] = L"";  // Bluelium : pas de société\n'),
  (H,
   'inline constexpr wchar_t kProductPathName[] = L"Helium";\n',
   'inline constexpr wchar_t kProductPathName[] = L"Bluelium";\n'),
  (H,
   '        .app_guid =\n'
   '            L"{FB68A146-637A-48C2-A0C4-1565DE45FEBD}",\n',
   '        .app_guid =\n'
   '            L"{6D8633B0-A1F1-4A06-8086-5C623F31B488}",  // Bluelium\n'),
  (H,
   '        .base_app_name = L"Helium",              // A distinct base_app_name.\n'
   '        .base_app_id = L"Helium",                // A distinct base_app_id.\n'
   '        .browser_prog_id_prefix = L"HeliumHTM",  // Browser ProgID prefix.\n',
   '        .base_app_name = L"Bluelium",              // Bluelium\n'
   '        .base_app_id = L"Bluelium",                // Bluelium\n'
   '        .browser_prog_id_prefix = L"BlueliumHTM",  // Bluelium (11 car. max)\n'),
  (H,
   '            L"Helium HTML Document",  // Browser ProgID description.\n'
   '        .direct_launch_url_scheme = "helium",\n'
   '        .pdf_prog_id_prefix = L"HeliumPDF",  // PDF ProgID prefix.\n',
   '            L"Bluelium HTML Document",  // Bluelium\n'
   '        .direct_launch_url_scheme = "bluelium",\n'
   '        .pdf_prog_id_prefix = L"BlueliumPDF",  // Bluelium (11 car. max)\n'),
  (H,
   '            L"Helium PDF Document",  // PDF ProgID description.\n',
   '            L"Bluelium PDF Document",  // Bluelium\n'),
  (H,
   '        .active_setup_guid =\n'
   '            L"{FB68A146-637A-48C2-A0C4-1565DE45FEBD}",  // Active Setup\n',
   '        .active_setup_guid =\n'
   '            L"{6D8633B0-A1F1-4A06-8086-5C623F31B488}",  // Bluelium, Active Setup\n'),
  (H,
   '        .toast_activator_clsid = {0xE9852F6C,\n',
   '        .toast_activator_clsid = {0xE89CC913,  // Bluelium\n'),
  (H,
   '        .elevator_clsid = {0x140DE20F,\n',
   '        .elevator_clsid = {0x4E0096D2,  // Bluelium\n'),
  (H,
   '        .elevator_iid = {0xC89A04FF,\n',
   '        .elevator_iid = {0xB98109FC,  // Bluelium\n'),
  (H,
   '        // {C89A04FF-00C6-4966-94B2-5AFEC6FED93A}.\n',
   '        // {B98109FC-00C6-4966-94B2-5AFEC6FED93A} (Bluelium).\n'),
  (H,
   '        .tracing_service_clsid = {0x83f69367,\n',
   '        .tracing_service_clsid = {0x8AE7D082,  // Bluelium\n'),
  ('chrome/installer/setup/installer_crash_reporter_client.cc',
   r'      L"SOFTWARE\\Policies\\Helium";' '\n',
   r'      L"SOFTWARE\\Policies\\Bluelium";' '\n'),
  ('components/policy/tools/generate_policy_source.py',
   r"CHROMIUM_POLICY_KEY = 'SOFTWARE\\\\Policies\\\\Helium'" '\n',
   r"CHROMIUM_POLICY_KEY = 'SOFTWARE\\\\Policies\\\\Bluelium'" '\n'),
  (POLICY,
   r"          'reg_mandatory_key_name': 'Software\\Policies\\Helium'," '\n',
   r"          'reg_mandatory_key_name': 'Software\\Policies\\Bluelium'," '\n'),
  (POLICY,
   r"          'reg_recommended_key_name': 'Software\\Policies\\Helium\\Recommended'," '\n',
   r"          'reg_recommended_key_name': 'Software\\Policies\\Bluelium\\Recommended'," '\n'),
]
