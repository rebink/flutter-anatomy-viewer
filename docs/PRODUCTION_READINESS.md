# Public repository licensing and engineering readiness

Audit date: 29 October 2026. Scope clarified by the owner: making the repository
public so other developers can reuse it, not launching a live service or making
an app-store release. Those distribution paths have different acceptance gates.

## Public repository licensing

The licenses of the reviewed original code, bundled anatomy and renderer permit
public redistribution when their respective conditions are met. **CC BY-SA does
not prohibit a public repository or commercial use.** A CC BY 4.0 migration is not
legally required solely to make the repository public.

| Component | Applicable license | Public redistribution conditions |
| --- | --- | --- |
| Original application code, tools and documentation | MIT | Preserve the copyright and permission notice; do not extend this grant to third-party material |
| Current anatomy GLB and embedded model | CC BY-SA 2.1 Japan | Preserve attribution, source/license links and notices; identify modifications; keep covered model adaptations under the applicable share-alike terms |
| Bundled Three.js r170 | MIT | Preserve `THREE_LICENSE.txt` with the renderer |

The review confirms that `LICENSE` and `LICENSE.md` distinguish original code
from models; `CREDITS.txt` identifies the database, pinned mirror revision,
modifications and model license; and the runtime credits control remains
available. The model notice and Three.js notice each match their pinned upstream
source byte-for-byte. The source-requested paper and archive DOI references have
also been added to `CREDITS.txt`.

Do not describe the whole repository or model data as MIT, CC BY 4.0 or
attribution-free. Public-source consumers must retain the applicable notices and
the required attribution control. Do not impose conflicting restrictions on
licensed model rights. Independently written host code does not automatically
become share-alike solely by being distributed as a collection with these assets;
the collection/adaptation distinction still depends on the actual integration.

The owner has explicitly approved public source release with the current
share-alike assets. This supersedes the earlier migration-first repository
visibility hold in `AGENTS.md` and
[the migration status](licensing/MIGRATION_STATUS.md). No replacement geometry
is approved, no model is relicensed, and pub.dev publication remains disabled.

Review the actual public commit and exposed Git history before changing
visibility. The path-level history check found no added JPG, PDF, font, OBJ,
BLEND or ZIP files; it is not a complete content, secrets or rights audit of every
revision. Archived third-party website evidence is excluded from our MIT grant
and has not received a separate exhaustive redistribution review. Downloaded
candidate models and dependencies are not covered by the component table merely
because build scripts reference them. Downstream products remain responsible
for their actual dependency notices and license compatibility.

Sources checked:

- [CC BY-SA 2.1 Japan deed](https://creativecommons.org/licenses/by-sa/2.1/jp/deed.en)
  and [controlling legal code](https://creativecommons.org/licenses/by-sa/2.1/jp/legalcode),
  especially Article 5 on notices, attribution, adaptations and collections.
- [Pinned model-source README](https://github.com/Kevin-Mattheus-Moerman/BodyParts3D/blob/f0eeb6e843380cfe6b83797cf8c3e1af74de5e61/README.md)
  and [content license](https://github.com/Kevin-Mattheus-Moerman/BodyParts3D/blob/f0eeb6e843380cfe6b83797cf8c3e1af74de5e61/LICENSE_content).
- [Three.js r170 license](https://github.com/mrdoob/three.js/blob/r170/LICENSE).

This is a component-level engineering licensing review, not legal certification.

## Previously verified engineering checks

| Check | Result |
| --- | --- |
| `flutter analyze` | Pass, no issues |
| `flutter test --reporter expanded` | Pass, 12 tests |
| `flutter build apk --debug --no-pub` | Pass |
| `flutter build ios --simulator --debug --no-pub` | Pass |
| Rebuilt Android APK viewer/notices | Pass; all six bundled files match source, including updated credits; no duplicate raw GLB |
| Simulator app viewer/notices | Passed at the earlier engineering checkpoint; rebuild with updated citation references before distributing that binary |
| `npm ci` and `npm audit --json` | Pass, zero reported vulnerabilities |
| `tools/check_viewer.cjs` through Playwright with installed Chrome | Pass |
| Optional candidate geometry helper unit tests | Pass, 21 tests; not anatomy approval |
| Optional `python3 tools/check_asset_licenses.py` | Pass for the staged candidate; not approval to ship it |

The local Chromium headless-shell installer timed out twice while extracting its
archive. Browser verification therefore used Playwright's `chrome` channel with
the same checker, not the default headless-shell executable. Re-run the normal
`npm run setup:browsers` / `npm run test:viewer` path on a clean runner. The new
GitHub Actions workflow has not been executed remotely during this audit.
Candidate checks require local research data and are deliberately not fresh-clone
or shipped-app gates.

Browser checks compare the committed renderer with a deterministic rebuild and
compare the embedded model with the raw GLB. They exercise all 28 muscle and 33
bone/group selections, organ picking, mode isolation, opacity, theming, idle
rendering, off-canvas drag recovery and WebGL context-loss fallback/reload. They
also reject runtime HTTP(S) requests and JavaScript errors. Rendered screenshots
are useful visual checks, not clinical or source/license approval.

## Engineering fixes applied

- Restrict bridge-enabled navigation to the bundled local viewer entry document,
  retaining its exact URL once loading starts; reject other documents and frames.
- Keep credits readable after viewer failure and show a redistribution warning
  rather than an unhandled exception if the required notice cannot be loaded.
  This warning does not replace the obligation to ship the full notice.
- Bound viewer text, omit the redundant gesture hint at enlarged text sizes and
  wrap the report header. Regression coverage uses a 320-pixel viewport at 300%
  text scaling; the native rotate/zoom controls remain available.
- Make browser verification fail for stale renderer bytes or mismatched embedded
  geometry and cover gesture/context-loss recovery.
- Update Android Gradle Plugin from 8.1.0 to 8.1.1, the minimum required by the
  resolved AndroidX WebKit dependency. The previous Android debug build failed.
- Add `.github/workflows/verify.yml` for Flutter analysis/tests, browser checks and
  Android debug compilation. It does not publish or approve model assets.

## Separate project and distribution gates

These are not all conditions for lawful public-source redistribution. Package
extraction is an API/usability concern; device acceptance concerns runtime quality;
and signing/store checks apply only when distributing the app. The owner-approved
public source release does not depend on completing the model migration.

1. **Replacement-model approval.** The bundled legacy assets remain
   **CC BY-SA 2.1 Japan**, not MIT or CC BY 4.0. Public source release with those
   assets is approved. Replacement candidates still have unresolved geometry
   and source-coverage issues. Review and approve a replacement before changing
   models, embedded data, manifest, provenance and notices together. See
   [migration status](licensing/MIGRATION_STATUS.md).
2. **Package extraction.** The current project starts in `lib/main.dart` and
   includes fictional findings and application navigation. Extract a public
   viewer library with caller-supplied highlights/callbacks, an example app,
   package-relative asset loading, documented exports and package metadata.
   Include `AGENTS.md`, `INTEGRATION.md` and the required notices. Validate a
   separate host integration and package contents before a publish dry run.
   Keep `publish_to: none` until the release is explicitly approved.
3. **App-store identity, signing and compliance (if distributing the app).**
   These are app-store gates, not pub.dev library requirements. Android still
   uses `com.example.anatomy_viewer` and debug signing for release builds; iOS uses
   `com.example.anatomyViewer` and the existing development team configuration.
   The owner must supply final identifiers and production signing. Check current
   store SDK/toolchain, native-library and privacy requirements for the chosen
   Flutter/plugin versions. Debug APK and simulator builds do not establish
   App Store or Google Play readiness.
4. **Physical-device acceptance.** Validate actual Android WebView and iOS
   WKWebView entry URLs, first load/retry, offline operation, accessible credits,
   TalkBack/VoiceOver, text scaling, reduced motion, background/foreground,
   multi-touch, GPU loss and memory/performance on representative devices.
   Mock WebView tests and desktop Chrome cannot certify these native paths.
5. **Product and legal acceptance.** Preserve the mandatory production credits
   control, full source/license URLs and modification notices. Review the
   current assets' share-alike terms and any host EULA/store/DRM conflict.
   Keep the fictional-data and non-clinically-validated disclosures; there is no
   patient-data pipeline, diagnosis or clinical validation in this prototype.

Use the existing [release checklist](RELEASE_CHECKLIST.md) and
[integration requirements](../INTEGRATION.md) for the approval and host handoff.
Public repository release is owner-approved with the current split licenses.
Model promotion, license relabeling, pub.dev publication and signing-credential
changes are not part of this release.
