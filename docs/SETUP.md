# Installation and use

## What you are installing

This repository is an Android/iOS Flutter **application prototype**, not an
installable pub.dev package. It runs its bundled Three.js viewer inside a WebView.
There is no backend, real patient data, or runtime CDN requirement. Dependency
installation does require network access on a fresh machine.

Access remains private pending the agreed official-model migration and approval.
Original application code is MIT licensed for reuse, including private commercial
apps; the models are separately licensed. Read [LICENSE.md](../LICENSE.md) and
[INTEGRATION.md](../INTEGRATION.md) before distributing a host app.

## Prerequisites

- Git and access to `rebink/flutter-anatomy-viewer`.
- Tested baseline: Flutter 3.27.2 / Dart 3.6.1. The Dart constraint is `^3.6.1`;
  other compatible versions still need validation. Do not blindly upgrade lockfiles.
- Android: Android Studio/SDK, compatible Java/Gradle setup and emulator or device.
- iOS: macOS, Xcode, CocoaPods, simulator or a signing-configured device.
- Node.js 20+ and npm for renderer development/checks, not for simply running the app.
- Google Chrome for `npm run test:viewer` (the test selects the `chrome` channel).
- Python 3 and a virtual environment only if rebuilding geometry/candidate assets.

Run `flutter doctor -v` and resolve the issues for your target platform.

## Clone and run

```sh
git clone https://github.com/rebink/flutter-anatomy-viewer.git
cd flutter-anatomy-viewer
flutter doctor -v
flutter pub get
flutter devices
flutter run -d <device-id>
```

Use your normal Git credential manager or `gh auth login` for private access;
never put tokens in repository URLs or commit `.env`/signing files.

The renderer and model data are already checked in. You do not need Node or
Python just to launch the app. Android/iOS are the supported app targets;
`flutter run -d chrome` is not a supported substitute for this WebView app.

If a fresh Android checkout reports a missing Gradle wrapper, regenerate platform
tooling using the tested Flutter version (`flutter create --platforms=android .`)
and review the resulting diff before keeping it. The standard Flutter template
ignores local Gradle wrapper artifacts; never overwrite customized platform files
without reviewing/backing them up.

## Controls and modes

- **Body Parts**: 15 organ regions; two fictional lung findings appear after a
  two-second simulated fetch. Select a lung, then View details for the demo.
- **Muscles**: 28 major muscles, 14 left/right pairs. This is not a complete atlas.
- **Bones**: 33 selectable bones/groups. Skull, spine sections, ribs, hands and
  feet are grouped; this is not an individually selectable 206-bone atlas.
- Tap a mesh or its named button to highlight and focus it. Other structures in
  that mode fade; structures in other modes are hidden and cannot be picked.
- Drag to rotate; pinch to zoom. Named rotation/zoom buttons provide alternatives.
  Reset body view restores the overview; mode switching resets selection.
- Opacity adjusts the active structures from 35% to 100%. Reduce motion and system
  reduced-motion settings disable automatic rotation/animated camera moves.
- **Credits and licenses** opens the required readable, scrollable attribution.
  It must work even when the model fails to load.

The parameter browser is a disconnected catalog by default. See
[medical-support.md](../medical-support.md) before supplying database records.
Neutral coloring means unassessed, not healthy; geometry is not clinically validated.

## Development and checks

Run from the repository root:

```sh
npm ci
npm run build:viewer
flutter analyze
flutter test
npm run test:viewer
```

Edit `tools/viewer.js`, then rebuild `assets/viewer/viewer.js`; do not hand-edit the
minified bundle. Commit both source and generated output. Browser checks exercise
the actual offline GLB, all muscle/bone selections and cross-mode isolation;
screenshots are written to ignored `.research/`. Inspect those screenshots too.
Flutter tests use a fake WebView: they do not establish real device performance.

Optional platform checks:

```sh
flutter build ios --simulator --debug
flutter build apk --debug
flutter run --profile -d <physical-device-id>
```

Device signing, production identifiers, privacy declarations and store submission
are host responsibilities. Current platform project IDs are prototype IDs; the
Android release build configuration uses debug signing and is not store-ready.
Do not commit signing keys or passwords.

## Rebuild the current legacy geometry

Only do this when changing models; it downloads source meshes and needs disk space.

```sh
python3 -m venv .venv
. .venv/bin/activate
python -m pip install trimesh==5.1.1 fast-simplification==0.2.0
python tools/prepare_anatomy.py
npm run test:viewer
```

The builder uses the pinned mirror revision and reuses unchanged reduced meshes.
Review anatomy, source IDs and notices; update GLB, embedded JS, manifest and
modification credits together. Keep the raw GLB in the repository for authoring and
tests, but not in Flutter's runtime assets: `anatomy-data.js` already embeds it.
The combined model is about 10.98 MB binary / 607,068 triangles; its base64 form is
larger. All three modes share this file and are loaded together.

## Optional official candidate research - not the shipped assets

A fresh clone does not contain `.research/bodyparts3d-4.0-candidate/`. Therefore
`python3 tools/check_asset_licenses.py` is **not** a fresh-clone test. After creating
the Python environment above, explicitly rebuild the candidate before using it:

```sh
python tools/prepare_official_anatomy.py
python tools/check_asset_licenses.py
```

These commands download checksum-pinned official inputs and write a separate
candidate under `.research/`. The check verifies that candidate's provenance,
not approval of the shipped models or permission to relabel them. The candidate
has 16 regions and does not include the newer muscle/bone modes. Do not copy it
into app assets: lung geometry and a complete migration need separate approval.

## Embedding into another app

There is no supported `flutter pub add` / Git-dependency installation yet.
Preserve the MIT code notice and separately satisfy the model terms. Use the in-repository
`AnatomyScreen`/`AnatomyApp` constructors as the prototype starting point. Keep
its support Dart files, complete listed viewer assets and WebView dependencies;
use [the integration guide](../INTEGRATION.md) for attribution and host-agent rules.
A proper package extraction must fix package-relative asset loading and separate
the demo findings/navigation from the reusable viewer. Do not claim that merely
copying this screen provides a production medical API.

## Troubleshooting

- Private clone denied: verify `gh auth status` and access to the personal account's
  repository, not the Cureocity organization.
- 3D unavailable: check WebView platform support and that every `flutter.assets`
  entry exists; do a full app restart after changing bundled JavaScript/model data.
- Chrome missing: install Google Chrome; the test does not use Flutter Web.
- Python reports missing `trimesh`: activate `.venv` and point your editor at that
  interpreter, not the system Python.
- Candidate checker reports missing files: it requires the optional candidate
  build described above; do not substitute the shipped legacy models.
- Mobile jank or memory pressure: see [THEMING.md](THEMING.md#performance).
