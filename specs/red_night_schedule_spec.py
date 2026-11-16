"""Bluelium : horaires Nuit par profil, indépendants des fenêtres et des pages."""

NEW_FILES = {
'chrome/browser/profiles/bluelium_night_scheduler.h': r'''// Bluelium : un planificateur par profil normal, détruit avant ses prefs.
#ifndef CHROME_BROWSER_PROFILES_BLUELIUM_NIGHT_SCHEDULER_H_
#define CHROME_BROWSER_PROFILES_BLUELIUM_NIGHT_SCHEDULER_H_

#include <optional>
#include <stdint.h>
#include "base/memory/raw_ptr.h"
#include "base/power_monitor/power_observer.h"
#include "base/timer/timer.h"
#include "components/prefs/pref_change_registrar.h"

class PrefService;

class BlueliumNightScheduler : public base::PowerSuspendObserver {
 public:
  explicit BlueliumNightScheduler(PrefService* prefs);
  ~BlueliumNightScheduler() override;
  void OnResume() override;

 private:
  void QueueScheduleChanged();
  void OnScheduleChanged();
  void Evaluate();
  raw_ptr<PrefService> prefs_;
  PrefChangeRegistrar registrar_;
  base::RepeatingTimer timer_;
  base::OneShotTimer schedule_change_timer_;
  std::optional<int64_t> last_boundary_;
};
#endif  // CHROME_BROWSER_PROFILES_BLUELIUM_NIGHT_SCHEDULER_H_
''',
'chrome/browser/profiles/bluelium_night_scheduler.cc': r'''// Bluelium : horaires civils locaux, y compris après veille ou changement d'heure.
#include "chrome/browser/profiles/bluelium_night_scheduler.h"

#include "base/functional/bind.h"
#include "base/power_monitor/power_monitor.h"
#include "base/time/time.h"
#include "chrome/common/pref_names.h"
#include "components/prefs/pref_service.h"

BlueliumNightScheduler::BlueliumNightScheduler(PrefService* prefs)
    : prefs_(prefs) {
  registrar_.Init(prefs);
  for (const char* name : {prefs::kGlypheRedNightAutoEnabled,
                           prefs::kGlypheRedNightAutoStart,
                           prefs::kGlypheRedNightAutoEnd}) {
    registrar_.Add(name, base::BindRepeating(
        &BlueliumNightScheduler::QueueScheduleChanged, base::Unretained(this)));
  }
  base::PowerMonitor::GetInstance()->AddPowerSuspendObserver(this);
  OnScheduleChanged();
}

BlueliumNightScheduler::~BlueliumNightScheduler() {
  base::PowerMonitor::GetInstance()->RemovePowerSuspendObserver(this);
}

void BlueliumNightScheduler::QueueScheduleChanged() {
  // Bluelium : appliquer ensemble les trois prefs du même appel Mojo.
  schedule_change_timer_.Start(FROM_HERE, base::TimeDelta(), this,
                               &BlueliumNightScheduler::OnScheduleChanged);
}

void BlueliumNightScheduler::OnScheduleChanged() {
  timer_.Stop();
  last_boundary_.reset();
  if (!prefs_->GetBoolean(prefs::kGlypheRedNightAutoEnabled)) {
    return;  // Bluelium : désactiver l'automatisation ne change pas le mode.
  }
  Evaluate();
  // Bluelium : aucune API multiplateforme ne notifie toutes les corrections
  // d'horloge/fuseau. Ce contrôle léger garantit une réaction sous une seconde,
  // sans écriture de pref tant qu'aucune borne n'est franchie.
  timer_.Start(FROM_HERE, base::Seconds(1), this,
               &BlueliumNightScheduler::Evaluate);
}

void BlueliumNightScheduler::OnResume() {
  if (prefs_->GetBoolean(prefs::kGlypheRedNightAutoEnabled)) {
    Evaluate();
  }
}

void BlueliumNightScheduler::Evaluate() {
  const int start = prefs_->GetInteger(prefs::kGlypheRedNightAutoStart);
  const int end = prefs_->GetInteger(prefs::kGlypheRedNightAutoEnd);
  if (start < 0 || start >= 1440 || end < 0 || end >= 1440) {
    return;  // Bluelium : une pref corrompue ne déclenche jamais une bascule.
  }
  base::Time::Exploded local;
  base::Time::Now().LocalExplode(&local);
  const int minute = local.hour * 60 + local.minute;
  local.hour = local.minute = local.second = local.millisecond = 0;
  base::Time civil_midnight;
  // Bluelium : encoder la date civile en UTC évite les jours de 23/25 heures.
  if (!base::Time::FromUTCExploded(local, &civil_midnight)) {
    return;
  }
  const int64_t day = civil_midnight.ToDeltaSinceWindowsEpoch().InMinutes();
  const int64_t start_boundary = day + start - (minute < start ? 1440 : 0);
  const int64_t end_boundary = day + end - (minute < end ? 1440 : 0);
  const int64_t boundary = start == end ? 0 :
      (start_boundary > end_boundary ? start_boundary : end_boundary);
  if (last_boundary_ == boundary) {
    return;
  }
  last_boundary_ = boundary;
  const bool enabled = start < end ? minute >= start && minute < end :
      start > end && (minute >= start || minute < end);
  // Bluelium : on n'observe PAS la pref manuelle. Une touche ou un sélecteur
  // reste donc prioritaire jusqu'à la prochaine borne, même après une veille.
  prefs_->SetBoolean(prefs::kGlypheRedNightEnabled, enabled);
}
''',
}

EDITS = [
 ('chrome/common/pref_names.h',
  'inline constexpr char kGlypheRedNightEnabled[] = "glyphe.red_night.enabled";\n',
  'inline constexpr char kGlypheRedNightEnabled[] = "glyphe.red_night.enabled";\n'
  '// Bluelium : minutes civiles locales depuis minuit.\n'
  'inline constexpr char kGlypheRedNightAutoEnabled[] = "glyphe.red_night.auto.enabled";\n'
  'inline constexpr char kGlypheRedNightAutoStart[] = "glyphe.red_night.auto.start";\n'
  'inline constexpr char kGlypheRedNightAutoEnd[] = "glyphe.red_night.auto.end";\n'),
 ('chrome/browser/ui/prefs/prefs_tab_helper.cc',
  '  registry->RegisterBooleanPref(prefs::kGlypheRedNightEnabled, false);\n',
  '  registry->RegisterBooleanPref(prefs::kGlypheRedNightEnabled, false);\n'
  '  // Bluelium : 21:00 à 07:00, automatisation désactivée par défaut.\n'
  '  registry->RegisterBooleanPref(prefs::kGlypheRedNightAutoEnabled, false);\n'
  '  registry->RegisterIntegerPref(prefs::kGlypheRedNightAutoStart, 1260);\n'
  '  registry->RegisterIntegerPref(prefs::kGlypheRedNightAutoEnd, 420);\n'),
 ('chrome/browser/profiles/BUILD.gn',
  '    "profile_impl.cc",\n    "profile_impl.h",\n',
  '    "profile_impl.cc",\n    "profile_impl.h",\n'
  '    "bluelium_night_scheduler.cc",\n    "bluelium_night_scheduler.h",\n'),
 ('chrome/browser/profiles/profile_impl.h',
  'class PrefService;\n',
  'class PrefService;\nclass BlueliumNightScheduler;  // Bluelium : horaires Nuit\n'),
 ('chrome/browser/profiles/profile_impl.h',
  '  std::unique_ptr<sync_preferences::PrefServiceSyncable> prefs_;\n',
  '  std::unique_ptr<sync_preferences::PrefServiceSyncable> prefs_;\n'
  '  std::unique_ptr<BlueliumNightScheduler> bluelium_night_scheduler_;\n'),
 ('chrome/browser/profiles/profile_impl.cc',
  '#include "chrome/browser/profiles/profile_impl.h"\n',
  '#include "chrome/browser/profiles/profile_impl.h"\n'
  '#include "chrome/browser/profiles/bluelium_night_scheduler.h"\n'),
 ('chrome/browser/profiles/profile_impl.cc',
  '  ChromeVersionService::OnProfileLoaded(prefs_.get(), IsNewProfile());\n',
  '  // Bluelium : ProfileImpl appartient au profil original ; pas un timer par fenêtre.\n'
  '  if (IsRegularProfile()) {\n'
  '    bluelium_night_scheduler_ = std::make_unique<BlueliumNightScheduler>(GetPrefs());\n'
  '  }\n'
  '  ChromeVersionService::OnProfileLoaded(prefs_.get(), IsNewProfile());\n'),
 ('chrome/browser/profiles/profile_impl.cc',
  'ProfileImpl::~ProfileImpl() {\n',
  'ProfileImpl::~ProfileImpl() {\n'
  '  bluelium_night_scheduler_.reset();  // Bluelium : arrêter avant les services/prefs.\n'),
]

CSM = 'ui/webui/resources/cr_components/customize_color_scheme_mode/'
HANDLER = 'chrome/browser/ui/webui/cr_components/customize_color_scheme_mode/'
# Les deux interfaces contiennent SetFollowPageColor : des ancres distinctes.
EDITS += [
 (CSM + 'customize_color_scheme_mode.mojom',
  '  // Helium Glyphe : la barre du haut suit la couleur de la page.\n'
  '  SetFollowPageColor(bool enabled);\n',
  '  // Helium Glyphe : la barre du haut suit la couleur de la page.\n'
  '  SetFollowPageColor(bool enabled);\n'
  '  // Bluelium : commande atomique des horaires Nuit (minutes locales).\n'
  '  SetRedNightSchedule(bool enabled, int32 start_minutes, int32 end_minutes);\n'),
 (CSM + 'customize_color_scheme_mode.mojom',
  '  // Helium Glyphe : état de « Couleur de la page dans la barre ».\n'
  '  SetFollowPageColor(bool enabled);\n',
  '  // Helium Glyphe : état de « Couleur de la page dans la barre ».\n'
  '  SetFollowPageColor(bool enabled);\n'
  '  // Bluelium : envoyé à l’ouverture et à chaque changement de pref.\n'
  '  SetRedNightSchedule(bool enabled, int32 start_minutes, int32 end_minutes);\n'),
 (HANDLER + 'customize_color_scheme_mode_handler.h',
  '  void SetFollowPageColor(bool enabled) override;\n',
  '  void SetFollowPageColor(bool enabled) override;\n'
  '  void SetRedNightSchedule(bool enabled, int32_t start_minutes,\n'
  '                           int32_t end_minutes) override;\n'
  '  void UpdateRedNightSchedule();\n'),
 (HANDLER + 'customize_color_scheme_mode_handler.cc',
  'void CustomizeColorSchemeModeHandler::SetFollowPageColor(bool enabled) {\n',
  'void CustomizeColorSchemeModeHandler::SetRedNightSchedule(\n'
  '    bool enabled, int32_t start_minutes, int32_t end_minutes) {\n'
  '  if (start_minutes < 0 || start_minutes >= 1440 ||\n'
  '      end_minutes < 0 || end_minutes >= 1440) {\n'
  '    UpdateRedNightSchedule();  // Bluelium : renvoyer les valeurs retenues.\n'
  '    return;\n'
  '  }\n'
  '  PrefService* prefs = glyphe_prefs_.prefs();\n'
  '  // Bluelium : coalescer les trois notifications dans le planificateur.\n'
  '  prefs->SetInteger(prefs::kGlypheRedNightAutoStart, start_minutes);\n'
  '  prefs->SetInteger(prefs::kGlypheRedNightAutoEnd, end_minutes);\n'
  '  prefs->SetBoolean(prefs::kGlypheRedNightAutoEnabled, enabled);\n'
  '  UpdateRedNightSchedule();\n'
  '}\n\n'
  'void CustomizeColorSchemeModeHandler::UpdateRedNightSchedule() {\n'
  '  const PrefService* prefs = glyphe_prefs_.prefs();\n'
  '  remote_client_->SetRedNightSchedule(\n'
  '      prefs->GetBoolean(prefs::kGlypheRedNightAutoEnabled),\n'
  '      prefs->GetInteger(prefs::kGlypheRedNightAutoStart),\n'
  '      prefs->GetInteger(prefs::kGlypheRedNightAutoEnd));\n'
  '}\n\n'
  'void CustomizeColorSchemeModeHandler::SetFollowPageColor(bool enabled) {\n'),
 (HANDLER + 'customize_color_scheme_mode_handler.cc',
  '  glyphe_prefs_.Init(profile->GetPrefs());\n',
  '  glyphe_prefs_.Init(profile->GetPrefs());\n'
  '  for (const char* pref : {prefs::kGlypheRedNightAutoEnabled,\n'
  '                            prefs::kGlypheRedNightAutoStart,\n'
  '                            prefs::kGlypheRedNightAutoEnd}) {\n'
  '    glyphe_prefs_.Add(pref, base::BindRepeating(\n'
  '        &CustomizeColorSchemeModeHandler::UpdateRedNightSchedule,\n'
  '        base::Unretained(this)));\n'
  '  }\n'),
 (HANDLER + 'customize_color_scheme_mode_handler.cc',
  'void CustomizeColorSchemeModeHandler::UpdateColorSchemeMode() {\n',
  'void CustomizeColorSchemeModeHandler::UpdateColorSchemeMode() {\n'
  '  UpdateRedNightSchedule();  // Bluelium : état initial du panneau.\n'),
]
