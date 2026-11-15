"""Bluelium : changement de couleur de page en fondu flouté, sur toute la fenêtre.

Avant (page_color_fade_spec.py) : fondu de 180 ms fait de ~6 paliers, chacun
avec un ThemeChanged() complet de la fenêtre. Saccadé et perçu comme brutal.
Un balayage du haut vers le bas a été essayé puis écarté (15 nov.).

Après : on copie au compositeur l'image de toute la fenêtre, la fenêtre passe
d'un coup à la nouvelle couleur (un seul ThemeChanged()), puis l'image figée
s'efface en 160 ms en se floutant : les deux couleurs se mélangent au lieu de
se succéder. Couvre tout le navigateur (cadre, onglets, barre, panneaux) ; la
page web, identique dans l'image, ne change pas d'aspect.

Sans animation (« réduire les animations »), copie impossible ou en retard de
plus de 120 ms : passage direct. Un nouveau changement pendant un fondu repart
de l'état affiché.

S'applique après motion_spec.py (BlueliumMotionEnabled).
"""
NEW_FILES = {}
_H = 'chrome/browser/ui/views/frame/browser_widget.h'
_CC = 'chrome/browser/ui/views/frame/browser_widget.cc'
_GN = 'chrome/browser/ui/views/frame/BUILD.gn'
EDITS = [
 (_GN,
  '  sources = [ "browser_widget.cc" ]\n'
  '  public_deps = [\n'
  '    ":browser_widget",\n'
  '    "//chrome/browser:browser_public_dependencies",\n'
  '  ]\n'
  '  deps = [\n',
  '  sources = [ "browser_widget.cc" ]\n'
  '  public_deps = [\n'
  '    ":browser_widget",\n'
  '    "//chrome/browser:browser_public_dependencies",\n'
  '  ]\n'
  '  deps = [\n'
  '    # Bluelium : fondu de la couleur de page (copie du compositeur).\n'
  '    "//components/viz/common",\n'
  '    "//skia",\n'
  '    "//ui/compositor",\n'
  '    "//ui/gfx",\n'),

 (_H,
  'class BrowserWidget : public views::Widget,\n',
  'class BlueliumPageColorBlend;\n\n'
  'class BrowserWidget : public views::Widget,\n'),
 (_H,
  '  void FinishGlyphePageColorFade();\n',
  '  void FinishGlyphePageColorFade();\n'
  '  // Bluelium : fondu flouté de toute la fenêtre vers la nouvelle couleur.\n'
  '  void StartBlueliumPageColorBlend();\n'),
 (_H,
  '  base::RepeatingTimer glyphe_fade_timer_;\n',
  '  base::RepeatingTimer glyphe_fade_timer_;\n'
  '  std::unique_ptr<BlueliumPageColorBlend> bluelium_blend_;\n'),

 (_CC,
  '#include "ui/gfx/animation/tween.h"\n',
  '#include "ui/gfx/animation/tween.h"\n'
  '#include "base/memory/weak_ptr.h"\n'
  '#include "components/viz/common/frame_sinks/copy_output_request.h"\n'
  '#include "components/viz/common/frame_sinks/copy_output_result.h"\n'
  '#include "ui/compositor/layer.h"\n'
  '#include "ui/compositor/layer_delegate.h"\n'
  '#include "ui/compositor/paint_recorder.h"\n'
  '#include "ui/gfx/animation/bluelium_motion.h"\n'
  '#include "ui/gfx/canvas.h"\n'
  '#include "ui/gfx/geometry/rect_conversions.h"\n'
  '#include "ui/gfx/image/image_skia.h"\n'
  '\n'
  '// Bluelium : image figée de la fenêtre, effacée en se floutant.\n'
  'class BlueliumPageColorBlend : public ui::LayerDelegate {\n'
  ' public:\n'
  '  // `apply` passe la fenêtre à la nouvelle couleur ; appelé une seule fois.\n'
  '  BlueliumPageColorBlend(ui::Layer* root, const gfx::Rect& area,\n'
  '                         base::OnceClosure apply)\n'
  '      : root_(root), area_(area), apply_(std::move(apply)) {}\n'
  '  BlueliumPageColorBlend(const BlueliumPageColorBlend&) = delete;\n'
  '  BlueliumPageColorBlend& operator=(const BlueliumPageColorBlend&) = delete;\n'
  '  ~BlueliumPageColorBlend() override { DropLayer(); }\n'
  '\n'
  '  void Start() {\n'
  '    const float scale = root_->device_scale_factor();\n'
  '    auto request = std::make_unique<viz::CopyOutputRequest>(\n'
  '        viz::CopyOutputRequest::ResultFormat::RGBA,\n'
  '        viz::CopyOutputRequest::ResultDestination::kSystemMemory,\n'
  '        base::BindOnce(&BlueliumPageColorBlend::OnCopied,\n'
  '                       weak_factory_.GetWeakPtr()));\n'
  '    request->set_area(gfx::ScaleToEnclosingRect(area_, scale));\n'
  '    root_->RequestCopyOfOutput(std::move(request));\n'
  '    // Copie en retard (fenêtre cachée, GPU occupé) : pas d\'attente.\n'
  '    timeout_.Start(FROM_HERE, base::Milliseconds(120),\n'
  '                 base::BindOnce(&BlueliumPageColorBlend::Apply,\n'
  '                                weak_factory_.GetWeakPtr()));\n'
  '  }\n'
  '\n'
  '  void OnPaintLayer(const ui::PaintContext& context) override {\n'
  '    ui::PaintRecorder recorder(context, area_.size());\n'
  '    recorder.canvas()->DrawImageInt(image_, 0, 0);\n'
  '  }\n'
  '  void OnDeviceScaleFactorChanged(float, float) override {}\n'
  '\n'
  ' private:\n'
  '  static constexpr base::TimeDelta kDuration = base::Milliseconds(160);\n'
  '  static constexpr float kMaxBlur = 14.f;\n'
  '\n'
  '  void Apply() {\n'
  '    if (apply_) {\n'
  '      timeout_.Stop();\n'
  '      std::move(apply_).Run();\n'
  '    }\n'
  '  }\n'
  '\n'
  '  void OnCopied(std::unique_ptr<viz::CopyOutputResult> result) {\n'
  '    if (!apply_) {\n'
  '      return;  // Trop tard : couleur déjà appliquée sans fondu.\n'
  '    }\n'
  '    // Copie profonde : le bitmap du résultat n\'est valable que le temps\n'
  '    // de l\'accès.\n'
  '    SkBitmap bitmap;\n'
  '    if (result && !result->IsEmpty()) {\n'
  '      auto scoped = result->ScopedAccessSkBitmap();\n'
  '      const SkBitmap source = scoped.GetOutScopedBitmap();\n'
  '      if (!source.drawsNothing() && bitmap.tryAllocPixels(source.info()) &&\n'
  '          !source.readPixels(bitmap.pixmap())) {\n'
  '        bitmap.reset();\n'
  '      }\n'
  '    }\n'
  '    if (bitmap.drawsNothing()) {\n'
  '      Apply();\n'
  '      return;\n'
  '    }\n'
  '    image_ = gfx::ImageSkia::CreateFromBitmap(bitmap,\n'
  '                                              root_->device_scale_factor());\n'
  '    Apply();  // Nouvelle couleur, sous l\'image figée posée juste après.\n'
  '\n'
  '    picture_ = ui::Layer::Create(ui::LAYER_TEXTURED);\n'
  '    picture_->SetName("BlueliumPageColorBlend");\n'
  '    picture_->set_delegate(this);\n'
  '    picture_->SetFillsBoundsOpaquely(false);\n'
  '    picture_->SetBounds(area_);\n'
  '    root_->Add(picture_.get());\n'
  '    root_->StackAtTop(picture_.get());\n'
  '    picture_->SchedulePaint(gfx::Rect(area_.size()));\n'
  '    start_ = base::TimeTicks::Now();\n'
  '    timer_.Start(FROM_HERE, base::Milliseconds(16),\n'
  '                 base::BindRepeating(&BlueliumPageColorBlend::Step,\n'
  '                                     weak_factory_.GetWeakPtr()));\n'
  '  }\n'
  '\n'
  '  // Opacité et flou à chaque image : l\'ancienne couleur se dissout dans\n'
  '  // la nouvelle au lieu de s\'effacer net.\n'
  '  void Step() {\n'
  '    const double t = std::clamp(\n'
  '        (base::TimeTicks::Now() - start_) / kDuration, 0.0, 1.0);\n'
  '    if (!picture_ || t >= 1.0) {\n'
  '      DropLayer();\n'
  '      return;\n'
  '    }\n'
  '    const float fade = static_cast<float>(\n'
  '        gfx::Tween::CalculateValue(gfx::Tween::EASE_IN_OUT, t));\n'
  '    picture_->SetOpacity(1.f - fade);\n'
  '    picture_->SetLayerBlur(kMaxBlur * static_cast<float>(\n'
  '        gfx::Tween::CalculateValue(gfx::Tween::EASE_OUT, t)));\n'
  '  }\n'
  '\n'
  '  void DropLayer() {\n'
  '    timer_.Stop();\n'
  '    if (picture_) {\n'
  '      picture_->set_delegate(nullptr);\n'
  '    }\n'
  '    picture_.reset();\n'
  '    image_ = gfx::ImageSkia();\n'
  '  }\n'
  '\n'
  '  raw_ptr<ui::Layer> root_;\n'
  '  const gfx::Rect area_;\n'
  '  base::OnceClosure apply_;\n'
  '  gfx::ImageSkia image_;\n'
  '  std::unique_ptr<ui::Layer> picture_;\n'
  '  base::TimeTicks start_;\n'
  '  base::OneShotTimer timeout_;\n'
  '  base::RepeatingTimer timer_;\n'
  '  base::WeakPtrFactory<BlueliumPageColorBlend> weak_factory_{this};\n'
  '};\n'),

 # Le fondu par paliers laisse place au fondu flouté.
 (_CC,
  '  glyphe_fade_from_ = *glyphe_shown_page_color_;\n'
  '  glyphe_fade_start_ = base::TimeTicks::Now();\n'
  '  glyphe_fade_timer_.Start(\n'
  '      FROM_HERE, base::Milliseconds(33),\n'
  '      base::BindRepeating(&BrowserWidget::StepGlyphePageColorFade,\n'
  '                          base::Unretained(this)));\n'
  '  StepGlyphePageColorFade();\n'
  '}\n',
  '  // Bluelium : fondu flouté de toute la fenêtre au lieu des paliers.\n'
  '  glyphe_fade_timer_.Stop();\n'
  '  StartBlueliumPageColorBlend();\n'
  '}\n'
  '\n'
  'void BrowserWidget::StartBlueliumPageColorBlend() {\n'
  '  // Un fondu en cours s\'arrête : on repart de ce qui est affiché.\n'
  '  bluelium_blend_.reset();\n'
  '  ui::Layer* root = GetLayer();\n'
  '  if (!gfx::BlueliumMotionEnabled() || !root || !IsVisible() ||\n'
  '      !GetRootView() || GetRootView()->size().IsEmpty()) {\n'
  '    FinishGlyphePageColorFade();\n'
  '    return;\n'
  '  }\n'
  '  bluelium_blend_ = std::make_unique<BlueliumPageColorBlend>(\n'
  '      root, gfx::Rect(GetRootView()->size()),\n'
  '      base::BindOnce(&BrowserWidget::FinishGlyphePageColorFade,\n'
  '                     base::Unretained(this)));\n'
  '  bluelium_blend_->Start();\n'
  '}\n'),
]
