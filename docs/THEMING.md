# Themes, colors and performance

## Flutter theme and viewer style

Use standard Material `ThemeData` for UI and `AnatomyStyle` for model colors and
lighting. This example belongs inside this application's Dart sources (it is not
a published-package import):

```dart
import 'package:flutter/material.dart';
import 'package:anatomy_viewer/main.dart' show AnatomyApp;
import 'package:anatomy_viewer/anatomy_style.dart';

void main() {
  runApp(AnatomyApp(
    theme: ThemeData(
      colorScheme: ColorScheme.fromSeed(seedColor: const Color(0xFF24746B)),
      scaffoldBackgroundColor: const Color(0xFFF4F1EA),
    ),
    darkTheme: ThemeData.dark(),
    themeMode: ThemeMode.system,
    style: const AnatomyStyle(
      bodyShell: Color(0xFF487C91),
      warning: Color(0xFFAA6600),
      danger: Color(0xFFB42318),
      backgroundHighlight: Color(0xFFFFFFFF),
      organColors: {
        ...AnatomyStyle.defaultOrganColors,
        'brain': Color(0xFFA8C6EA),
        'muscle_deltoid_left': Color(0xFFC77665),
        'bone_femur_left': Color(0xFFE4D8B8),
      },
    ),
  ));
}
```

`AnatomyScreen(style: ...)` also inherits an existing host Material theme.
Changing theme/style on rebuild synchronizes the existing viewer rather than
reloading model geometry. A fixed `AnatomyStyle` does not automatically choose a
separate dark/light palette; pass the appropriate style from the host if needed.

## Supported settings

| Setting | Effect |
| --- | --- |
| `theme`, `darkTheme`, `themeMode` | Flutter controls, text, cards and surfaces |
| `scaffoldBackgroundColor` | Main viewer background |
| Theme `onSurface` | Viewer status foreground |
| `backgroundHighlight` | Viewer background gradient highlight; defaults to theme `surfaceContainerHighest` |
| `bodyShell` | Translucent body outline |
| `neutralOrgan` | Fallback for organ IDs without a baseline color |
| `organColors` | Per-structure RGB overrides keyed by exact mesh ID; despite its name it also accepts muscle/bone IDs |
| `warning`, `danger` | Shared fictional-finding colors in 3D and Flutter |
| `keyLight`, `rimLight` | Directional lighting colors |
| `ambientSky`, `ambientGround` | Hemisphere lighting colors |

`organColors` replaces the default map: spread `AnatomyStyle.defaultOrganColors`
to change only selected entries. `{}` makes organs use `neutralOrgan`; muscle
and bone defaults are separate renderer colors, not `neutralOrgan`.
Find IDs in `assets/viewer/anatomy-manifest.json` and display labels in
`lib/main.dart`. Do not invent IDs or infer medical findings from the palette.

The current selected-muscle/bone highlight is fixed gold (`0xffd58a`) in
`tools/viewer.js` and takes priority over per-structure colors. It has no public
style option yet. Findings override baseline organ colors. Changes to renderer
constants require `npm run build:viewer` and regression checks.

Colors are converted to sRGB; alpha in a Dart color does not control 3D
transparency. Use the existing opacity slider. Lighting/transparency affect the
rendered appearance, so inspect screenshots and devices instead of assuming
hex values will look identical on a shaded mesh.

## Accessibility

Keep readable contrast in both themes and test at large system text sizes.
Never rely on red/green alone: preserve labels, finding icons, named selection
buttons, rotate/zoom controls and the reduce-motion setting. Preserve the
**Credits and licenses** tooltip and readable scrollable dialog. Test these
controls with the viewer unavailable as well as while it is working.

## Performance

Existing optimizations:

- One bundled offline model; hidden modes are excluded from picking/rendering.
- Reduced geometry, approximately 607k triangles across all modes.
- Pixel ratio capped at 2 in `tools/viewer.js`.
- Rendering stops when the scene/camera is idle; lifecycle/detail-route handling
  pauses rendering when the viewer should be inactive.
- Raw GLB is excluded from Flutter runtime assets to avoid shipping it alongside
  the same base64-embedded geometry.

Hidden modes still occupy memory: all meshes are loaded together. Base64 also
adds transfer/storage and decode overhead. Do not promise low-memory support
from desktop browser tests or claim hidden geometry has been unloaded.

Measure first on representative Android/iOS devices:

```sh
flutter run --profile -d <physical-device-id>
```

Check startup/decode time, WebView memory, rotation/zoom frame rate, temperature,
background/resume and repeated mode switching. Flutter frame charts alone do
not fully measure WebGL work inside the WebView; use platform WebView/Safari
inspection or native profiling too. Compare the same camera/mode/device before
and after any change.

If measurement shows a bottleneck, first try a lower pixel-ratio cap (for example
1.5) in the renderer, then rebuild and inspect sharpness. Further decimation
requires anatomy review and updated modification notices. Per-mode lazy loading
is a future optimization, not currently implemented. Do not solve performance
issues by removing attribution, accessibility controls or legal notices.
