# Commercial migration candidate - blocked, not integrated

The owner approved continuing the source migration after reporting that the
rights holder is unreachable and has not answered emails. Silence is not
permission. This work does not depend on obtaining a reply, relabeling existing
meshes, or generating 1:1 copies to evade their licenses.

## What this build does


tools/prepare_commercial_candidate.py builds a separate research artifact in
.research/commercial-migration-candidate/. It reads the existing 77-region
selection inventory without importing or reading the legacy geometry:

- 71 regions use freshly sourced official BodyParts3D Release 4.0 elements.
- Two lung selections use the checksum-pinned HRA male lung reference surfaces,
  rather than treating Release 4.0 bronchial branches as lung envelopes.
- Four muscle selections have no accepted replacement. They remain explicit
  missing-source entries in migration-report.json, not silent deletions or
  CC BY-SA fallbacks.

The missing IDs are muscle_abs_left, muscle_abs_right, muscle_latissimus_left
and muscle_latissimus_right. This is a 73/77 review candidate, NOT a complete
replacement app. It is separate from the existing female composite, which
continues to contain legacy geometry and must not be labeled CC BY-only.

Each built region records source concepts/elements or HRA node names, license,
transformation, triangle count and bounds in anatomy-manifest.json. Provenance
pins the input meshes, official license evidence, HRA metadata/crosswalk,
builder dependencies, original selection inventory, output model/base64,
notices and standalone preview. Changed source/evidence bytes fail verification;
do not fix such failures by merely repinning hashes.

All outputs remain blocked-review-only with promotion_allowed: false and
anatomically_validated: false. A passing check means byte/geometry consistency,
not legal clearance, clinical validation or permission to publish. Production
assets, the existing credits UI, package publication settings and app selection
lists are unchanged.

## Lung alignment limit

The HRA and BodyParts3D sources are different donors in different coordinate
frames. This preview preserves the HRA surfaces' size and orientation, then
translates each lung's bounds center to the corresponding official lung-tree
bounds center. This is explicitly an unreviewed DISPLAY translation, not a
validated registration. No shape scaling is used. Review actual lung surfaces,
heart, ribs, airway and body shell together before approving alignment. Do not
infer anatomical fidelity from finite bounds or a successful render. The inspected
front/back previews show different lung apex heights after this coarse
translation; landmark registration is still unresolved, not cosmetically fixed.

## Reproduce and inspect

Use the Python environment described in [the setup guide](../SETUP.md). The official cache must
already pass the existing source hashes. HRA male lung retrieval and its pinned
source/evidence files are documented in hra-lung/REVIEW.md; downloads are not
silently performed or accepted by this builder.

Run from the repository root with the environment activated:

    npm run build:migration
    npm run test:migration
    python3 -m http.server 8765 --bind 127.0.0.1 --directory .research/commercial-migration-candidate

Open http://127.0.0.1:8765 and inspect all three modes, front/back views, both
lungs, desktop/mobile layout and the always-readable credits. The preview uses
the existing renderer and production CSP with separate external control JS.
It labels all four gaps and is intentionally NOT the app's launch path.

The builder refuses redirected/hardlinked outputs and invalidates any previous
success marker before generating. A validated pending provenance file is only
published after all model/notices/preview artifacts exist and pass checks.

## Validation in this working copy

- Eleven unit tests pass: exact gap preservation, concept/element failures, no
  parent substitutions, output-link protection, stale-marker invalidation,
  evidence/hash changes and empty/nonfinite/collapsed mesh rejection.
- The real builder passes all 73 regions through source/evidence checks,
  source-area retention, laterality, GLB reload, embedded-base64 equality and
  complete output/notices/preview hashes. Passing is not release approval.
- Browser checks exercise all three modes, focus all 72 selectable structures,
  tap-pick both lungs plus representative muscle/bone, check 390px layout,
  and confirm readable credits even with the model request aborted. No page or
  console errors occurred on the normal-load page.
- Front/rotated organ, muscle and bone screenshots plus mobile/credits screenshots
  in the candidate directory were inspected. Lung apex alignment remains flagged.
- Playwright's managed Chromium download stalled and was killed after 300 seconds.
  These checks used the already-installed Chrome headless channel instead; the
  default managed Chromium path and Android/iOS WebViews are not validated here.

No legacy app assets are replaced. Legal source-scope/host-distribution review and
qualified anatomical approval are still outstanding.

## Source gaps: next acceptable routes

The official 20080812 archive does not contain any of the four target FMA IDs.
The official 20110915 Release 3.0 metadata lists all four, but its README
explicitly states CC BY-SA 2.1 Japan. No evidence in this investigation expressly
binds the newer general CC BY 4.0 grant to those exact old archive bytes. The
archive was not downloaded or verified; do not promote it by inference.

- Parts: https://dbarchive.biosciencedbc.jp/data/bodyparts3d/20110915/parts_list_e.txt
- Old terms: https://dbarchive.biosciencedbc.jp/data/bodyparts3d/20110915/README_e.html
- Current grant: https://dbarchive.biosciencedbc.jp/en/bodyparts3d/lic.html
- Expected objects: FMA13378.obj / FMA13377.obj (left/right rectus abdominis),
  FMA13359.obj / FMA13358.obj (left/right latissimus dorsi).

Without relying on an author response, the remaining options are independently
authored geometry with documented references/rights, or full-extent licensed
scan segmentation with documented weights/data terms and anatomical review.
Do not substitute a parent concept, clip a T4-L4 scan, mirror an unreviewed mesh,
or silently remove coverage. Modeling software or code being open source does
not establish the rights or completeness of a generated anatomical surface.
See MODEL_SOURCE_REVIEW.md for previously rejected/incomplete leads.

## Release gate

Resolve all four muscle sources, verify their complete laterality and anatomy,
review the mixed-source registration and all simplified meshes, review the exact
source/license scope and host EULA/store/DRM terms, and obtain explicit owner
approval. Only then replace GLB, embedded JS, manifest, provenance and notices
together and extend app interaction/attribution tests. Keep the mandatory
accessible credits control available even if model loading fails. Keep
publish_to: none; there is no automatic publication or production promotion.
