"""Bluelium : geste retour/suivant « pastille seule et fondu » (macOS).

Choisi le 15 nov. sur le banc d'essai (variante B) :
- pendant le geste, la page ne bouge plus ; seule la pastille sort du bord,
  se remplit et donne le « tic » haptique au seuil ;
- au relâchement, la pastille s'efface d'une impulsion et une image figée de
  la page (copie du compositeur prise au début du geste) la recouvre ; dès que
  la destination a soumis une image, cette copie s'efface en fondu (200 ms).
  Sans copie disponible (contenu protégé, échec), la page change sans fondu.

Spec macOS appliquée après motion_tuning_spec.py ; les ancres visent son
résultat uniquement.
"""
NEW_FILES = {}
_MM = 'chrome/browser/ui/cocoa/history_overlay_controller.mm'
EDITS = [
 # Copie du compositeur : CopyFromSurfaceResult a besoin du type viz complet.
 ('chrome/browser/ui/cocoa/BUILD.gn',
  '    "//components/tabs:impl",\n',
  '    "//components/tabs:impl",\n'
  '    "//components/viz/common",  # Bluelium : copie de page du geste\n'),

 (_MM,
  '#include "content/public/browser/web_contents_observer.h"\n',
  '#include "content/public/browser/web_contents_observer.h"\n'
  '// Bluelium (pastille seule) : copie figée de la page pour le fondu.\n'
  '#include "base/task/bind_post_task.h"\n'
  '#include "base/time/time.h"\n'
  '#include "components/viz/common/frame_sinks/copy_output_result.h"\n'
  '#include "content/public/browser/render_widget_host_view.h"\n'
  '#include "skia/ext/skia_utils_mac.h"\n'
  '#include "ui/gfx/geometry/rect.h"\n'
  '#include "ui/gfx/geometry/size.h"\n'),

 (_MM,
  '- (void)finishPresentation;\n'
  '@end\n',
  '- (void)finishPresentation;\n'
  '- (void)snapshotCaptured:(NSImage*)image;  // Bluelium : pastille seule\n'
  '@end\n'),

 (_MM,
  '  void BeginNavigation() { waiting_ = true; }\n',
  '  void BeginNavigation() { waiting_ = true; }\n'
  '  // Bluelium : copie de la page au début du geste, rendue sur ce thread.\n'
  '  void CaptureSnapshot() {\n'
  '    content::RenderWidgetHostView* view =\n'
  '        web_contents()->GetRenderWidgetHostView();\n'
  '    if (!view) {\n'
  '      return;\n'
  '    }\n'
  '    view->CopyFromSurface(\n'
  '        gfx::Rect(), gfx::Size(), base::Milliseconds(500),\n'
  '        base::BindPostTaskToCurrentDefault(base::BindOnce(\n'
  '            &BlueliumHistoryObserver::SnapshotCaptured,\n'
  '            weak_factory_.GetWeakPtr())));\n'
  '  }\n'),

 (_MM,
  ' private:\n'
  '  void VisualStateReady(bool success) {\n',
  ' private:\n'
  '  void SnapshotCaptured(const content::CopyFromSurfaceResult& result) {\n'
  '    if (!result.has_value() || result->bitmap.drawsNothing()) {\n'
  '      return;  // Bluelium : sans copie, la page change sans fondu.\n'
  '    }\n'
  '    [owner_ snapshotCaptured:skia::SkBitmapToNSImage(result->bitmap)];\n'
  '  }\n'
  '  void VisualStateReady(bool success) {\n'),

 (_MM,
  '  std::unique_ptr<BlueliumHistoryObserver> _observer;\n',
  '  std::unique_ptr<BlueliumHistoryObserver> _observer;\n'
  '  // Bluelium (pastille seule) : copie figée de la page, sous la pastille.\n'
  '  CALayer* __strong _snapshot;\n'
  '  NSImage* __strong _snapshotImage;\n'),

 (_MM,
  '    (id)[NSColor colorWithWhite:0 alpha:0.16].CGColor ];\n'
  '  [view.layer addSublayer:_edge];\n',
  '    (id)[NSColor colorWithWhite:0 alpha:0.16].CGColor ];\n'
  '  [view.layer addSublayer:_edge];\n'
  '  _snapshot = [CALayer layer];\n'
  '  _snapshot.opacity = 0;\n'
  '  _snapshot.contentsGravity = kCAGravityResize;\n'
  '  _snapshot.actions = @{ @"contents" : NSNull.null, @"bounds" : NSNull.null,\n'
  '                         @"position" : NSNull.null };\n'
  '  [view.layer addSublayer:_snapshot];  // Bluelium : sous la pastille\n'),

 (_MM,
  '    _observer = std::make_unique<BlueliumHistoryObserver>(contents, self);\n',
  '    _observer = std::make_unique<BlueliumHistoryObserver>(contents, self);\n'
  '    _observer->CaptureSnapshot();  // Bluelium : image du fondu de sortie\n'),

 (_MM,
  '- (void)setGestureVelocity:(CGFloat)velocity {\n'
  '  _velocity = std::isfinite(velocity) ? velocity : 0;\n'
  '}\n',
  '- (void)setGestureVelocity:(CGFloat)velocity {\n'
  '  _velocity = std::isfinite(velocity) ? velocity : 0;\n'
  '}\n'
  '\n'
  '// Bluelium (pastille seule) : copie prête, gardée jusqu\'au relâchement.\n'
  '- (void)snapshotCaptured:(NSImage*)image {\n'
  '  if (!_ended) {\n'
  '    _snapshotImage = image;\n'
  '  }\n'
  '}\n'
  '\n'
  '- (void)showSnapshot {\n'
  '  if (!_snapshotImage || !_snapshot) {\n'
  '    return;\n'
  '  }\n'
  '  [CATransaction begin];\n'
  '  [CATransaction setDisableActions:YES];\n'
  '  _snapshot.frame = self.view.bounds;\n'
  '  _snapshot.contents = _snapshotImage;\n'
  '  _snapshot.opacity = 1;\n'
  '  [CATransaction commit];\n'
  '}\n'
  '\n'
  '- (void)fadeSnapshotWithDuration:(CFTimeInterval)duration {\n'
  '  [CATransaction begin];\n'
  '  [CATransaction setDisableActions:duration == 0];\n'
  '  [CATransaction setAnimationDuration:duration];\n'
  '  [CATransaction setAnimationTimingFunction:\n'
  '      [CAMediaTimingFunction functionWithControlPoints:.4 :0 :.2 :1]];\n'
  '  _snapshot.opacity = 0;\n'
  '  [CATransaction commit];\n'
  '}\n'
  '\n'
  '// Bluelium : la pastille valide d\'une petite impulsion puis s\'efface.\n'
  '- (void)popPill {\n'
  '  CABasicAnimation* grow = [CABasicAnimation animationWithKeyPath:@"transform.scale"];\n'
  '  grow.fromValue = @1.05;\n'
  '  grow.toValue = @1.2;\n'
  '  CABasicAnimation* fade = [CABasicAnimation animationWithKeyPath:@"opacity"];\n'
  '  fade.fromValue = @(_pill.opacity);\n'
  '  fade.toValue = @0;\n'
  '  CAAnimationGroup* pop = [CAAnimationGroup animation];\n'
  '  pop.animations = @[ grow, fade ];\n'
  '  pop.duration = 0.2;\n'
  '  pop.timingFunction = [CAMediaTimingFunction functionWithControlPoints:.2 :.8 :.2 :1];\n'
  '  [CATransaction begin];\n'
  '  [CATransaction setDisableActions:YES];\n'
  '  _pill.opacity = 0;\n'
  '  _ring.opacity = 0;\n'
  '  [CATransaction commit];\n'
  '  [_pill addAnimation:pop forKey:@"bluelium.history.pop"];\n'
  '}\n'),

 # Pendant le geste : page immobile, ni bande découverte ni ombre.
 (_MM,
  '  _floor.backgroundColor = page_color;\n'
  '  const CGFloat edge = std::min<CGFloat>(16, offset);\n'
  '  _floor.frame = sign > 0 ? CGRectMake(0, 0, offset, NSHeight(bounds))\n'
  '                          : CGRectMake(NSWidth(bounds) - offset, 0, offset,\n'
  '                                       NSHeight(bounds));\n'
  '  _edge.frame = sign > 0\n'
  '      ? CGRectMake(offset - edge, 0, edge, NSHeight(bounds))\n'
  '      : CGRectMake(NSWidth(bounds) - offset, 0, edge, NSHeight(bounds));\n'
  '  _offset = offset;\n'
  '  if (_pageView.layer) {\n'
  '    _pageView.layer.transform = CATransform3DTranslate(\n'
  '        _originalTransform, sign * offset, 0, 0);\n'
  '  }\n'
  '  [CATransaction commit];\n',
  '  _floor.backgroundColor = page_color;\n'
  '  // Bluelium (pastille seule) : la page reste immobile ; seule la pastille\n'
  '  // suit le doigt (offset ne sert plus qu\'à sa position).\n'
  '  _floor.frame = CGRectZero;\n'
  '  _edge.frame = CGRectZero;\n'
  '  _offset = 0;\n'
  '  [CATransaction commit];\n'),

 # Relâchement validé : impulsion de la pastille, copie figée, navigation.
 (_MM,
  '  _dismissing = YES;\n'
  '  const CGFloat out = std::max(_offset, std::min<CGFloat>(\n'
  '      NSWidth(self.view.bounds) * 0.18, 160));\n'
  '  const CFTimeInterval duration = [self durationToOffset:out];\n'
  '  [self animateToOffset:out duration:duration];\n'
  '  dispatch_after(dispatch_time(DISPATCH_TIME_NOW, duration * NSEC_PER_SEC),\n'
  '                 dispatch_get_main_queue(), ^{\n'
  '    self->_carryFinished = YES;\n'
  '    [self finishIfReady];\n'
  '  });\n',
  '  _dismissing = YES;\n'
  '  // Bluelium (pastille seule) : la copie figée couvre la page pendant le\n'
  '  // chargement ; elle s\'efface en fondu quand la destination est rendue.\n'
  '  [self showSnapshot];\n'
  '  [self popPill];\n'
  '  _carryFinished = YES;\n'),

 # Destination rendue : fondu enchaîné au lieu du retour au centre.
 (_MM,
  '  // Bluelium : la nouvelle page rejoint le centre depuis le même décalage.\n'
  "  // Aucune seconde translation de BrowserView, ni fondu de l'ancienne page.\n"
  '  const CFTimeInterval duration = gfx::BlueliumMotionEnabled() ? 0.18 : 0;\n'
  '  _velocity = 0;\n'
  '  [self animateToOffset:0 duration:duration];\n',
  '  // Bluelium (pastille seule) : fondu enchaîné de la copie vers la page.\n'
  '  const CFTimeInterval duration =\n'
  '      gfx::BlueliumMotionEnabled() && _snapshot.contents ? 0.2 : 0;\n'
  '  _velocity = 0;\n'
  '  [self fadeSnapshotWithDuration:duration];\n'),

 # Test : la page n'est plus décalée après validation.
 ('chrome/browser/ui/cocoa/history_overlay_controller_unittest.mm',
  '  EXPECT_EQ(1, navigations);\n'
  '  EXPECT_LT(test_view().layer.transform.m41, 0);\n',
  '  EXPECT_EQ(1, navigations);\n'
  '  // Bluelium (pastille seule) : la page reste immobile.\n'
  '  EXPECT_TRUE(CATransform3DIsIdentity(test_view().layer.transform));\n'),
]
