"""Bluelium : détection et import Helium à la demande depuis chrome://setup.
L'importeur Helium/Brave écrit dans les services du profil ouvert ; aucun
remplacement de profil ni accès au trousseau. Pas de rendu frontend ici.
"""
NEW_FILES = {
'chrome/browser/ui/webui/onboarding/bluelium_helium_import_handler.h': r'''// Bluelium : contrat de bienvenue, données importables de Helium.
#ifndef CHROME_BROWSER_UI_WEBUI_ONBOARDING_BLUELIUM_HELIUM_IMPORT_HANDLER_H_
#define CHROME_BROWSER_UI_WEBUI_ONBOARDING_BLUELIUM_HELIUM_IMPORT_HANDLER_H_

#include <string>
#include <vector>
#include "base/memory/raw_ptr.h"
#include "base/memory/weak_ptr.h"
#include "chrome/browser/importer/importer_progress_observer.h"
#include "components/user_data_importer/common/importer_data_types.h"
#include "content/public/browser/web_ui_message_handler.h"

class ExternalProcessImporterHost;
class Profile;

class BlueliumHeliumImportHandler : public content::WebUIMessageHandler,
                                   public importer::ImporterProgressObserver {
 public:
  explicit BlueliumHeliumImportHandler(Profile* profile);
  ~BlueliumHeliumImportHandler() override;
  void RegisterMessages() override;
  void OnJavascriptDisallowed() override;
  void ImportStarted() override {}
  void ImportItemStarted(user_data_importer::ImportItem item) override {}
  void ImportItemEnded(user_data_importer::ImportItem item) override;
  void ImportEnded() override;

 private:
  void GetState(const base::ListValue& args);
  void Import(const base::ListValue& args);
  void OnDetected(std::string callback_id, base::DictValue result);
  void OnReady(std::string callback_id, std::string id, base::DictValue result);
  void StopImport();
  raw_ptr<Profile> profile_;
  raw_ptr<ExternalProcessImporterHost> host_ = nullptr;
  std::string callback_id_;
  uint16_t requested_ = 0;
  uint16_t finished_ = 0;
  bool checking_ = false;
  base::WeakPtrFactory<BlueliumHeliumImportHandler> weak_factory_{this};
};
#endif  // CHROME_BROWSER_UI_WEBUI_ONBOARDING_BLUELIUM_HELIUM_IMPORT_HANDLER_H_
''',
'chrome/browser/ui/webui/onboarding/bluelium_helium_import_handler.cc': r'''// Bluelium : source Helium fixe et lecture disque hors du thread UI.
#include "chrome/browser/ui/webui/onboarding/bluelium_helium_import_handler.h"

#include <set>
#include <utility>
#include "base/environment.h"
#include "base/files/file_enumerator.h"
#include "base/files/file_util.h"
#include "base/functional/bind.h"
#include "base/no_destructor.h"
#include "base/path_service.h"
#include "base/strings/string_util.h"
#include "base/strings/utf_string_conversions.h"
#include "base/task/thread_pool.h"
#include "build/build_config.h"
#include "chrome/browser/importer/brave_external_process_importer_host.h"
#include "chrome/browser/importer/profile_writer.h"
#include "chrome/browser/profiles/profile.h"
#include "chrome/common/importer/chrome_importer_utils.h"
#include "chrome/common/pref_names.h"
#include "components/prefs/pref_service.h"
#include "content/public/browser/web_contents.h"
#if BUILDFLAG(IS_LINUX)
#include "base/nix/xdg_util.h"
#endif

namespace {
constexpr uint16_t kItems = user_data_importer::HISTORY |
    user_data_importer::FAVORITES | user_data_importer::EXTENSIONS;

// Bluelium : empêcher un deuxième import dans une autre fenêtre du même profil.
std::set<Profile*>& BusyProfiles() {
  static base::NoDestructor<std::set<Profile*>> profiles;
  return *profiles;
}

base::DictValue Detect(const base::FilePath& target) {
  base::DictValue result;
  base::ListValue profiles;
  base::FilePath root;
#if BUILDFLAG(IS_MAC)
  base::FilePath home;
  if (base::PathService::Get(base::DIR_HOME, &home)) {
    root = home.Append("Library/Application Support/net.imput.helium");
  }
#elif BUILDFLAG(IS_LINUX)
  auto env = base::Environment::Create();
  root = base::nix::GetXDGDirectory(env.get(), base::nix::kXdgConfigHomeEnvVar,
                                    ".config").Append("net.imput.helium");
#endif
  result.Set("status", "not_found");
  result.Set("profiles", base::ListValue());
  if (root.empty() || !base::DirectoryExists(root)) {
    return result;
  }
  base::FilePath canonical_root, canonical_target;
  if (!base::NormalizeFilePath(root, &canonical_root) ||
      !base::NormalizeFilePath(target.DirName(), &canonical_target) ||
      canonical_root == canonical_target || canonical_root.IsParent(canonical_target) ||
      canonical_target.IsParent(canonical_root)) {
    result.Set("status", "same_profile");
    return result;
  }
  // Bluelium : profil déjà recopié en entier depuis Helium (lanceur AppImage
  // ou tools/migrate-helium-macos.sh) : ne pas proposer un second import.
  if (base::PathExists(target.DirName().Append(".copie-depuis-helium"))) {
    result.Set("status", "same_profile");
    return result;
  }
  result.Set("status", "available");
  // Bluelium : verrou présent, même périmé => ne jamais essayer de l'effacer.
  const auto lock = root.Append("SingletonLock");
  result.Set("sourceBusy", base::PathExists(lock) || base::IsLink(lock));
  base::FileEnumerator directories(root, false, base::FileEnumerator::DIRECTORIES);
  for (auto dir = directories.Next(); !dir.empty(); dir = directories.Next()) {
    const std::string id = dir.BaseName().AsUTF8Unsafe();
    if (id != "Default" && !base::StartsWith(id, "Profile ")) {
      continue;
    }
    // Bluelium : pas de profil symbolique ni de chemin fourni par JavaScript.
    if (base::IsLink(dir) || !base::PathExists(dir.Append("Preferences"))) {
      continue;
    }
    uint16_t supported = 0;
    if (!ChromeImporterCanImport(dir, user_data_importer::TYPE_CHROME, &supported)) {
      continue;
    }
    supported &= kItems;
    if (!supported) {
      continue;
    }
    profiles.Append(base::DictValue().Set("id", id).Set("name", id)
        .Set("items", supported));
  }
  if (profiles.empty()) {
    result.Set("status", "not_found");
  }
  // Bluelium : chemin privé utilisé côté C++ seulement, retiré avant réponse.
  result.Set("root", root.AsUTF8Unsafe());
  result.Set("profiles", std::move(profiles));
  return result;
}
}  // namespace

BlueliumHeliumImportHandler::BlueliumHeliumImportHandler(Profile* profile)
    : profile_(profile) {}
BlueliumHeliumImportHandler::~BlueliumHeliumImportHandler() {
  StopImport();
}

void BlueliumHeliumImportHandler::RegisterMessages() {
  web_ui()->RegisterMessageCallback("getHeliumImportState", base::BindRepeating(
      &BlueliumHeliumImportHandler::GetState, base::Unretained(this)));
  web_ui()->RegisterMessageCallback("importHeliumProfile", base::BindRepeating(
      &BlueliumHeliumImportHandler::Import, base::Unretained(this)));
}

void BlueliumHeliumImportHandler::GetState(const base::ListValue& args) {
  if (args.size() != 1 || !args[0].is_string()) {
    return;
  }
  AllowJavascript();
  base::ThreadPool::PostTaskAndReplyWithResult(FROM_HERE, {base::MayBlock()},
      base::BindOnce(&Detect, profile_->GetPath()),
      base::BindOnce(&BlueliumHeliumImportHandler::OnDetected,
                    weak_factory_.GetWeakPtr(), args[0].GetString()));
}

void BlueliumHeliumImportHandler::OnDetected(std::string callback_id,
                                            base::DictValue result) {
  result.Remove("root");
  result.Set("completed", profile_->GetPrefs()->GetBoolean(prefs::kGlypheHeliumImportCompleted));
  result.Set("busy", BusyProfiles().contains(profile_.get()));
  ResolveJavascriptCallback(base::Value(callback_id), result);
}

void BlueliumHeliumImportHandler::Import(const base::ListValue& args) {
  if (args.size() != 2 || !args[0].is_string() || !args[1].is_string()) {
    return;
  }
  AllowJavascript();
  const auto& callback_id = args[0].GetString();
  if (!profile_->IsRegularProfile() ||
      profile_->GetPrefs()->GetBoolean(prefs::kGlypheHeliumImportCompleted)) {
    ResolveJavascriptCallback(base::Value(callback_id),
        base::DictValue().Set("status", "unavailable"));
    return;
  }
  if (checking_ || BusyProfiles().contains(profile_.get())) {
    ResolveJavascriptCallback(base::Value(callback_id),
        base::DictValue().Set("status", "busy"));
    return;
  }
  checking_ = true;
  BusyProfiles().insert(profile_.get());
  base::ThreadPool::PostTaskAndReplyWithResult(FROM_HERE, {base::MayBlock()},
      base::BindOnce(&Detect, profile_->GetPath()),
      base::BindOnce(&BlueliumHeliumImportHandler::OnReady,
          weak_factory_.GetWeakPtr(), callback_id, args[1].GetString()));
}

void BlueliumHeliumImportHandler::OnReady(std::string callback_id,
    std::string id, base::DictValue result) {
  checking_ = false;
  const std::string status = result.FindString("status") ?
      *result.FindString("status") : "not_found";
  const auto* root = result.FindString("root");
  const auto* profiles = result.FindList("profiles");
  const base::DictValue* selected = nullptr;
  if (profiles) {
    for (const auto& value : *profiles) {
      if (value.GetDict().FindString("id") && *value.GetDict().FindString("id") == id) {
        selected = &value.GetDict();
        break;
      }
    }
  }
  const bool source_busy = result.FindBool("sourceBusy").value_or(false);
  if (status != "available" || !root || !selected || source_busy) {
    BusyProfiles().erase(profile_.get());
    ResolveJavascriptCallback(base::Value(callback_id), base::DictValue().Set(
        "status", source_busy ? "source_busy" : status == "available" ? "invalid_profile" : status));
    return;
  }
  user_data_importer::SourceProfile source;
  source.importer_name = u"Helium";
  source.importer_type = user_data_importer::TYPE_CHROME;
  source.source_path = base::FilePath::FromUTF8Unsafe(*root).Append(id);
  source.profile = base::UTF8ToUTF16(id);
  source.services_supported = selected->FindInt("items").value_or(0);
  requested_ = source.services_supported;
  finished_ = 0;
  callback_id_ = callback_id;
  auto* host = new BraveExternalProcessImporterHost();
  host_ = host;
  host->set_observer(this);
  host->set_parent_window(web_ui()->GetWebContents()->GetTopLevelNativeWindow());
  host->set_parent_view(web_ui()->GetWebContents()->GetNativeView());
  host->StartImportSettings(source, profile_, requested_, new ProfileWriter(profile_));
}

void BlueliumHeliumImportHandler::ImportItemEnded(user_data_importer::ImportItem item) {
  finished_ |= item;
}

void BlueliumHeliumImportHandler::ImportEnded() {
  // Bluelium : le host s'auto-détruit après cette notification.
  host_ = nullptr;
  BusyProfiles().erase(profile_.get());
  const bool complete = requested_ != 0 && (finished_ & requested_) == requested_;
  if (complete) {
    profile_->GetPrefs()->SetBoolean(prefs::kGlypheHeliumImportCompleted, true);
  }
  ResolveJavascriptCallback(base::Value(callback_id_), base::DictValue()
      .Set("status", complete ? "finished" : finished_ ? "partial" : "failed")
      .Set("requestedItems", requested_).Set("finishedItems", finished_));
  callback_id_.clear();
}

void BlueliumHeliumImportHandler::StopImport() {
  weak_factory_.InvalidateWeakPtrs();
  if (host_) {
    auto* host = host_.get();
    host_ = nullptr;
    host->set_observer(nullptr);
    host->Cancel();
  }
  if (checking_ || !callback_id_.empty()) {
    BusyProfiles().erase(profile_.get());
  }
  checking_ = false;
  callback_id_.clear();
}

void BlueliumHeliumImportHandler::OnJavascriptDisallowed() {
  StopImport();  // Bluelium : fermer la page annule la suite, sans rollback.
}
''',
}
EDITS = [
 ('chrome/common/pref_names.h',
  'inline constexpr char kGlypheRedNightAutoEnd[] = "glyphe.red_night.auto.end";\n',
  'inline constexpr char kGlypheRedNightAutoEnd[] = "glyphe.red_night.auto.end";\n'
  'inline constexpr char kGlypheHeliumImportCompleted[] = "glyphe.helium_import.completed";\n'),
 ('chrome/browser/ui/prefs/prefs_tab_helper.cc',
  '  registry->RegisterIntegerPref(prefs::kGlypheRedNightAutoEnd, 420);\n',
  '  registry->RegisterIntegerPref(prefs::kGlypheRedNightAutoEnd, 420);\n'
  '  registry->RegisterBooleanPref(prefs::kGlypheHeliumImportCompleted, false);\n'),
 ('chrome/browser/ui/webui/BUILD.gn',
  '    "onboarding/onboarding_handler.cc",\n',
  '    "onboarding/onboarding_handler.cc",\n'
  '    "onboarding/bluelium_helium_import_handler.cc",\n'
  '    "onboarding/bluelium_helium_import_handler.h",\n'),
 ('chrome/browser/ui/webui/BUILD.gn',
  '    "//components/helium_onboarding:generated_resources",\n'
  '    "//components/helium_onboarding:localized_strings",\n',
  '    "//components/helium_onboarding:generated_resources",\n'
  '    "//components/helium_onboarding:localized_strings",\n'
  '    "//chrome/browser/importer",\n'
  '    "//chrome/common/importer",\n'
  '    "//components/user_data_importer/common",\n'),
 ('chrome/browser/ui/webui/onboarding/onboarding_page_ui.cc',
  '#include "chrome/browser/ui/webui/onboarding/onboarding_handler.h"\n',
  '#include "chrome/browser/ui/webui/onboarding/onboarding_handler.h"\n'
  '#include "chrome/browser/ui/webui/onboarding/bluelium_helium_import_handler.h"\n'),
 ('chrome/browser/ui/webui/onboarding/onboarding_page_ui.cc',
  '  web_ui->AddMessageHandler(\n'
  '      std::make_unique<OnboardingMessageHandler>(browser_context));\n',
  '  web_ui->AddMessageHandler(\n'
  '      std::make_unique<OnboardingMessageHandler>(browser_context));\n'
  '  // Bluelium : l’offre reste dans la page existante, sans consentement implicite.\n'
  '  web_ui->AddMessageHandler(std::make_unique<BlueliumHeliumImportHandler>(profile));\n'),
]
