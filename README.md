# Flutter anatomy viewer

An offline 3D anatomy viewer for Android and iOS, built with Flutter and Three.js.
Select organs, muscles or bones to highlight them and focus the camera.

The demo includes 15 organ regions, 28 major muscles and 33 bones or bone groups.
You can rotate, zoom, adjust opacity and change the theme and model colors.
It is a curated view, not a complete anatomy atlas.

This repository contains a runnable demo, not a standalone pub.dev package yet.
The findings are fictional, and the geometry is not clinically validated.
Do not use it for diagnosis.

## Run the demo

Tested with Flutter 3.27.2 and Dart 3.6.1. Set up an Android or iOS device first.

```sh
git clone https://github.com/rebink/flutter-anatomy-viewer.git
cd flutter-anatomy-viewer
flutter pub get
flutter run -d <device-id>
```

Tap a structure or its named button to select it. Drag to rotate and pinch to
zoom. The model and renderer are bundled, so the viewer needs no runtime network
connection. You do not need Node.js or Python to run the demo.

## Configure or embed

Use `AnatomyApp` and `AnatomyStyle` to configure Flutter themes, body colors and
per-organ colors. See the [theme examples](docs/THEMING.md).

For another app, follow the [integration guide](INTEGRATION.md). The reusable
package API and package-relative asset loading still need extraction; there is
no supported `flutter pub add` or Git-dependency installation yet. Keep patient
data and medical interpretation in the host app.

## Licenses and attribution

- Original application code: [MIT](LICENSE).
- Bundled BodyParts3D models: [CC BY-SA 2.1 Japan](LICENSE.md), including the
  existing combinations, simplification and conversion.
- Three.js: [MIT](assets/viewer/THREE_LICENSE.txt).

Keep the **Credits and licenses** control visible and distribute the bundled
notices. Preserve attribution and the applicable share-alike terms for model
adaptations. The anatomy is not MIT, CC BY 4.0 or attribution-free.
Read [INTEGRATION.md](INTEGRATION.md) before redistribution. Agents should also
read [AGENTS.md](AGENTS.md).

## Development checks

```sh
flutter analyze
flutter test
npm ci
npm run setup:browsers
npm run test:viewer
```

After editing `tools/viewer.js`, run `npm run build:viewer` and commit the rebuilt
bundle. The browser checker catches stale bundles and saves screenshots to the
ignored `.research/` directory.

## More details

- [Setup, controls and troubleshooting](docs/SETUP.md)
- [Medical parameter mapping and its limits](medical-support.md)
- [License review and engineering checks](docs/PRODUCTION_READINESS.md)
- [Host integration checklist](docs/RELEASE_CHECKLIST.md)
- [Replacement-model research](docs/licensing/MIGRATION_STATUS.md) and
  [female preview](docs/licensing/hra-female/OPEN_CANDIDATE.md), neither approved
  as a replacement for the bundled models.
