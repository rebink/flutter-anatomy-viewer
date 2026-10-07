# Anatomy / Findings

Android/iOS Flutter prototype: a translucent 3D body with Body Parts, Muscles and Bones modes, individually selectable organs, 28 major muscles and 33 bones/bone groups, fictional lung highlights, focus/zoom, and native preview/detail screens.

**Demonstration only. Not a diagnostic tool.** No medical documents, patient data, server requests, diagnoses or urgency assessment are included. Neutral organs mean unassessed, not healthy. Geometry has not been clinically validated.

## Documentation and permissions

Private repository: **rebink/flutter-anatomy-viewer** (personal account, not Cureocity).
This is an application prototype, **not a published Flutter package**. Original
application code has no reuse license yet; the models and dependencies have
separate licenses. See [LICENSE.md](LICENSE.md) before redistribution.

- [Install, run, use controls and troubleshoot](docs/SETUP.md)
- [Theme customization and performance tuning](docs/THEMING.md)
- [Integration and mandatory attribution](INTEGRATION.md)
- [Legal/release checklist and host handoff](docs/RELEASE_CHECKLIST.md)
- [Agent rules](AGENTS.md) and [medical parameter contract](medical-support.md)

## Run

Tested with Flutter 3.27.2 / Dart 3.6.1. Bundled assets require no runtime network access.

```sh
git clone https://github.com/rebink/flutter-anatomy-viewer.git
cd flutter-anatomy-viewer
flutter doctor -v
flutter pub get
flutter devices
flutter run -d <android-or-ios-device-id>
```

The app shows two fictional findings after a two-second simulated fetch. Tap a lung or its list entry to open the preview, then View details. Drag the model to rotate, pinch to zoom, and use Reset body view to return. Replay demo reruns loading. Reduce motion disables automatic rotation and animated camera moves; system reduced-motion preferences are respected. Scrolling is available outside the interactive model area.

Use **Muscles** to explore 14 left/right muscle pairs: deltoid, pectoralis major, biceps brachii, triceps brachii, rectus abdominis, external oblique, trapezius, latissimus dorsi, gluteus maximus, rectus femoris, vastus lateralis, biceps femoris, gastrocnemius and tibialis anterior. Tap a mesh or its named button to highlight it and focus the camera; posterior muscles focus from behind. Other muscles fade, and organs are hidden and excluded from picking. Switching modes resets selection; Body Parts retains the organ demo. This is a curated major-muscle view, not a complete atlas or clinical assessment.

Use **Bones** to explore the skull, mandible, spine sections, sacrum, sternum, ribs, and paired shoulder/arm/hip/leg bones, hands and feet. Tap a bone/group or its named button to highlight and focus it; other modes are hidden and excluded from picking. Skull, vertebral sections, ribs, hands and feet are grouped rather than individually selectable constituent bones. This curated skeleton is not a complete 206-bone atlas and is not clinically validated.

## Implementation

- `lib/main.dart`: mock data, Flutter UI, validated viewer messages, bottom sheet and detail navigation.
- `tools/viewer.js`: Three.js scene, rim-lit shell, organ materials, camera controls and raycast picking.
- `assets/viewer/anatomy.glb`: approximately 607,000 triangles / 10.98 MB. Separate shell, 28 selectable major muscles, 33 selectable bones/bone groups, and 15 organ regions: left/right lungs, heart wall, liver, stomach, brain, airway, esophagus, small intestine, large intestine/rectum, left/right kidneys, bladder, pancreas and gallbladder.
- `assets/viewer/anatomy-data.js`: the GLB embedded for local-file WebView loading without cross-origin requests. Only this copy is bundled in the app; the raw GLB remains an authoring/test artifact to avoid shipping duplicate geometry.
- `tools/prepare_anatomy.py`: legacy asset reduction/conversion from a pinned mirror revision.
- `tools/prepare_official_anatomy.py`: separate checksum-pinned official Release 4.0 candidate builder. It does not overwrite app assets; geometry approval is pending.

The renderer is a bundled Three.js WebView rather than Thermion: current Thermion requires a newer Flutter SDK than the default installed version. No CDN or local HTTP server is used. Assets are intentionally curated, not reconstructed from the reference JPG. No exhaustive bone inventory, vasculature or skeletal animation is included. The brain representation combines cortex, cerebellum and brainstem structures rather than every internal brain region. Baseline organ colors distinguish anatomy, not assessed health. The opacity slider adjusts the current mode's structures from 35% to 100%; selecting a structure fades its neighbors to reveal deeper structures. Explore anatomy provides a button for every region, including otherwise occluded organs.

## Medical parameter navigation

The **Body systems and parameters** browser covers 12 system groups, including list-only systems without matching 3D meshes. Organ previews link to related groups. Pass database-derived `medicalParameters` to `AnatomyApp` or `AnatomyScreen`; the default explicitly shows a disconnected catalog, not a hard-coded enabled inventory. Enabled records retain their source/evidence labels and can belong to multiple systems. Unknown mappings remain accessible. This metadata does not change the fictional lung findings or infer patient/device availability.

See `medical-support.md` for the requested inventory, evidence caveats, mapping keys, geometry limits and host integration contract. Database access and medical calculations are not implemented in this offline prototype.

## Licensing

**The bundled app still uses the original BodyParts3D mirror-derived assets with CC BY-SA 2.1 Japan notices.** Keep attribution and share-alike obligations for those assets. They have not been relabeled.

**Verified official-source update:** DBCLS / LSDB Archive specifies **CC BY 4.0**, with a license update dated **27 February 2025**. It permits commercial use/redistribution subject to attribution, without share-alike. However, the fresh Release 4.0 candidate's lung mappings render branching internal structures instead of our previous solid surfaces. The visual migration is blocked; original app assets and notices were restored. The candidate remains in `.research/bodyparts3d-4.0-candidate/` for review. This is not an attribution-free asset option.

**Integrators and agents: read [INTEGRATION.md](INTEGRATION.md) and [AGENTS.md](AGENTS.md).** The information/credits button is mandatory for the planned package; preserve attribution and readable notices in production. Dependency installation does not automatically notify agents: add the documented pointer to host agent instructions.

Current notices are `assets/viewer/CREDITS.txt` and `BODY_PARTS_LICENSE.txt`. Official license/download/history snapshots and legal code are preserved in `docs/licensing/bodyparts3d/`. Three.js is MIT; its license is bundled. The reference JPG is not distributed.

## Checks and rebuilding

```sh
flutter analyze
flutter test
npm ci
npm run build:viewer
npm run test:viewer  # uses installed Google Chrome through Playwright
flutter build ios --simulator --debug
flutter build apk --debug
```

The separate `python3 tools/check_asset_licenses.py` command requires the optional
candidate build; `.research/` is deliberately excluded from Git. It is not a
fresh-clone gate and does not approve the bundled legacy models. See
[setup instructions](docs/SETUP.md#optional-official-candidate-research---not-the-shipped-assets).

Browser checks load the actual GLB offline, verify organ/muscle/bone labels, select all 28 muscles and 33 bones/bone groups, reject cross-mode focus/picking, pick real lung/brain/intestine/kidney meshes, verify transparency shader state, reject loading taps and out-and-back drags, exercise accessible rotate/zoom controls, and verify idle scenes stop GPU draw calls. Screenshots go to `.research/anatomy-full.png` and `.research/anatomy-focus.png`. Flutter tests exercise detail navigation, demo disclosure and lifecycle/route pause synchronization using a test WebView platform.

To rebuild geometry, use a Python virtual environment with `trimesh==5.1.1` and `fast-simplification==0.2.0`, then run `python tools/prepare_anatomy.py`. Legacy downloads are cached in `.research/anatomy_raw/`. To rebuild the separate official candidate, run `python tools/prepare_official_anatomy.py` in the same venv. Its official downloads are cached in `.research/bodyparts3d-4.0-official/`; hashes are checked even though upstream uses a LATEST URL. Changed inputs fail closed. Candidate outputs never reuse old geometry or overwrite the app. `python3 tools/check_asset_licenses.py` checks the staged candidate's provenance, not approval for app release.

## Custom themes and colors

`AnatomyApp` accepts standard Flutter `theme`, `darkTheme`, and `themeMode` parameters. `AnatomyScreen` can also be placed under a host app's existing Material theme. UI backgrounds, cards, text, typography, controls and the viewer background follow that theme.

Use `AnatomyStyle` from `lib/anatomy_style.dart` for the body shell, default/per-organ colors, warning/danger colors, background highlight and lighting. The same severity colors are used in 3D, preview cards and detail screens.

```dart
AnatomyApp(
  theme: ThemeData.light(),
  darkTheme: ThemeData.dark(),
  themeMode: ThemeMode.system,
  style: const AnatomyStyle(
    bodyShell: Color(0xFF487C91),
    warning: Color(0xFFAA6600),
    danger: Color(0xFFB42318),
    organColors: {
      ...AnatomyStyle.defaultOrganColors,
      'brain': Color(0xFFA8C6EA),
      'heart': Color(0xFFBC94D8),
    },
  ),
)
```

Rebuilding with a different style or theme updates the existing viewer without reloading geometry. `organColors` replaces the baseline palette: spread the defaults to override selected organs, or use `{}` for a uniform `neutralOrgan` color. Clinical highlights take precedence over baseline organ colors. 3D colors use sRGB channels; transparency is controlled by the opacity slider, not color alpha. Severity labels and icons remain visible regardless of palette; choose colors with adequate contrast. Runtime/patient input is never interpreted as arbitrary CSS.

## Package readiness

This remains a private prototype, not a published package. The next extraction should be a small viewer widget with caller-provided highlights and an organ-tap callback; keep medical data, interpretation and navigation in the host app. Retain an example app rather than embedding its demo findings in the library. Choose an explicit application-code license before distribution; the bundled model's current CC BY-SA license is separate and must not be relabeled as MIT. Complete or explicitly approve the official CC BY 4.0 geometry migration before advertising that license. Include `AGENTS.md`, `INTEGRATION.md`, notices and licensing evidence in the eventual package; keep its attribution button mandatory. Support package-relative asset loading during extraction. Android/physical-device validation and accessibility testing remain release gates.

## Validation status and remaining work

Flutter analysis, widget test, browser interaction check and iOS simulator compilation pass. Android build did not finish within the 240-second budget (Gradle assembleDebug); no Android success is claimed. The initial iOS 26 simulator boot stalled, but the app subsequently launched on the iOS 18.5 iPhone 16 Pro simulator and its body rendering was confirmed by screenshot. Physical-device behavior and mobile frame rate still need validation. Browser screenshots are not mobile runtime evidence.

Before real medical use: connect an authenticated server contract with stable finding IDs, organ/laterality identifiers, reviewed priority and evidence references; handle multiple/contradictory findings, failures and unmapped organs; conduct clinical, privacy and accessibility reviews. Unknown organs must remain accessible in a list rather than be guessed onto a mesh. Do not derive medical urgency from visual color or AI confidence.
