# Integration and release compliance checklist

This is an engineering checklist, not legal advice or a compliance certificate.
Have qualified counsel review the actual product, jurisdictions and distribution
channels. Passing tests or displaying an info button does not settle every license
obligation. Do not distribute until the relevant permissions and gates are met.

## 1. Confirm which rights you have

- [ ] Preserve the original application's [MIT notice](../LICENSE) when reusing or
  distributing its code, including in private commercial Cureocity builds.
  Confirm authority to license contributions; MIT does not cover third-party models.
  Keep `publish_to: none` until an explicit package-release decision.
- [ ] Record the exact version/commit and model artifact hashes shipped.
- [ ] Identify the bundled assets as **CC BY-SA 2.1 Japan**, not MIT/CC BY 4.0.
  Use [LICENSE.md](../LICENSE.md), the bundled credits and source license summary.
- [ ] Review the controlling [CC BY-SA 2.1 JP legal code](https://creativecommons.org/licenses/by-sa/2.1/jp/legalcode).
  Check attribution, adaptation/share-alike, notice and restriction requirements.
  Do not substitute assumptions based on a different CC license version.
- [ ] Assess the distinction between adapted models, collections and independent
  host code. Do not tell downstream developers either that all their code must
  be open-source or that closed-source distribution is automatically cleared.
- [ ] Review all dependencies' licenses, including the separately MIT-licensed
  Three.js renderer. Preserve applicable third-party notices.

## 2. Wire attribution into the host

- [ ] Keep an accessible production **Credits and licenses** control on the anatomy
  screen. Current implementation: `lib/main.dart`, opening bundled `CREDITS.txt`.
  Record the equivalent host screen/control in the host's integration notes.
- [ ] Ensure the notice is readable, scrollable and available at large text sizes.
  Test with model loading deliberately failed; attribution must still open.
- [ ] Display database/creator credit, source URLs, license URL and modification
  notice. Prefer loading the bundled notice rather than maintaining a stale copy.
- [ ] Retain `CREDITS.txt`, `BODY_PARTS_LICENSE.txt`, `THREE_LICENSE.txt` and the
  manifest in the app/package distribution. Preserve links to the legal code.
- [ ] Add host modifications to credits when changing geometry/material treatment.
  Maintain source IDs, pinned sources, reproduction instructions and hashes.
- [ ] Do not hide attribution for commercial or white-label builds. No banner
  over the model is required by this project policy, but silent asset files alone
  are not our accepted UX. If attribution is refused, stop using these models and
  obtain separate written permission or replace them with suitable alternatives.

Current credit identification (keep the full bundled notice, not just this line):

> BodyParts3D, (c) The Database Center for Life Science licensed under CC Attribution-Share Alike 2.1 Japan.

Source: https://github.com/Kevin-Mattheus-Moerman/BodyParts3D

License: https://creativecommons.org/licenses/by-sa/2.1/jp/deed.en

## 3. Review distribution restrictions

- [ ] Review the host EULA, app-store terms, DRM and additional restrictions with
  counsel for compatibility with the applicable model license. Generic "all
  content is proprietary" or "no copying any assets" clauses need review/carve-outs.
- [ ] Determine how recipients receive licensed model adaptations and notices
  under the applicable share-alike terms. Keep reproducible source/modification
  records; do not assume supplying a screenshot of credits is sufficient.
- [ ] Preserve clinical disclaimers: illustrative, reduced-detail, not clinically
  validated, not patient-specific, and no implied endorsement by DBCLS.
- [ ] Keep fictional findings labeled. Real medical data requires a separate
  clinical, privacy, security and regulatory review, not just a new data endpoint.

## 4. Keep legacy and official-candidate licensing separate

The official DBCLS update dated 27 February 2025 specifies CC BY 4.0. Evidence is
preserved in `docs/licensing/bodyparts3d/`, but the candidate lung geometry is not
approved and its scope does not cover the current muscle/bone additions.

- [ ] Do not relabel the current mirror-derived artifacts based on that update.
- [ ] Before migration, review/approve source and anatomy for the entire replacement.
- [ ] Replace model, embedded JS, manifest, provenance, notices and documentation
  together; retain official evidence and update attribution to the actual inputs.
- [ ] Run candidate provenance checks and app/browser checks, then inspect geometry.
  Interaction tests do not verify anatomy; hashes do not prove legal clearance.
- [ ] Even after an approved CC BY 4.0 migration, retain attribution and review
  conflicting EULA/store/DRM restrictions. It is not an attribution-free license.

See [INTEGRATION.md](../INTEGRATION.md) for the candidate status and future credit.

## 5. Technical and handoff gates

- [ ] Run `flutter analyze`, `flutter test`, `npm ci`, `npm run build:viewer` and
  `npm run test:viewer`; inspect front/back/focus screenshots in all modes.
- [ ] Validate Android/iOS builds, physical-device memory/performance and accessibility.
  Historic iOS build results do not establish the new modes' device readiness.
- [ ] Inspect packaged assets, not just the working tree, for required notices.
- [ ] Use release signing and non-prototype application identifiers. Never commit
  credentials, keystores, private patient data or local research caches.
- [ ] If extracting a package, fix package-relative loading, separate demo data
  from viewer API, and ship/link `AGENTS.md` and `INTEGRATION.md` from its README.
- [ ] Append a pointer in the host's existing agent instructions; do not overwrite
  them. Record the credits entry point and remind agents the asset migration is
  pending. Dependency installation does not notify or enforce agent compliance.

Suggested handoff record:

```text
Viewer commit:
Host version/platforms:
Application-code permission/license decision:
Bundled model source/license and artifact hashes:
Attribution screen/control and failed-load test:
Host model modifications and notice location:
Dependency/EULA/store/DRM reviewer and decision:
Anatomy/accessibility/device validation evidence:
Unresolved blockers and release owner:
```

Retain this record with the release, not just in a transient chat.
