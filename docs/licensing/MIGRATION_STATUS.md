# Public repository / Cureocity migration status

## Approved plan

The owner approved MIT for original application code and an official CC BY 4.0
model migration **before** changing `rebink/flutter-anatomy-viewer` to public.
The intended host is the private commercial Cureocity app. See [LICENSE](../../LICENSE)
and [LICENSE.md](../../LICENSE.md) for the code/asset boundary.

**Status: blocked on source coverage and geometry approval.** No model assets have
been promoted, repository visibility has not changed, and no legal certification
is claimed. The currently bundled legacy models remain CC BY-SA 2.1 Japan.

## Verified coverage gap

`tools/check_official_coverage.py` checks the current viewer's 77 region IDs against
the official candidate mappings plus the current muscle/bone concept IDs. It
verifies the source SHA-256 pins from `tools/prepare_official_anatomy.py` before
reading mappings or checking OBJ membership. It reads legacy *concept identifiers*,
not legacy geometry, and does not reuse meshes.

Result: 73 regions resolve to official elements; four current muscle IDs do not:

| Viewer ID | Missing official IS-A concept |
| --- | --- |
| `muscle_abs_right` | `FMA13377` |
| `muscle_abs_left` | `FMA13378` |
| `muscle_latissimus_right` | `FMA13358` |
| `muscle_latissimus_left` | `FMA13359` |

This establishes missing mappings in the checked release, not the absence of every
possible equivalent geometry from all official releases. A similarly located mesh
is not sufficient justification for assigning the missing anatomical name.

Reproduce after preparing the official cache as described in [SETUP.md](../SETUP.md):

```sh
python3 tools/check_official_coverage.py > /tmp/official-coverage.json
```

Exit 1 is the **expected blocking result** while mappings are unresolved. Missing
files/checksum errors also fail; do not change hashes merely to get a passing gate.
A future exit 0 proves concept/element availability only, not anatomical correctness,
license clearance, or approval to replace the assets. The current candidate builder
still emits 16 regions; it has not yet been expanded to the full viewer coverage.

## Lung geometry findings

Read-only inspection of the cached official Release 4.0 archives and mappings found:

- Right lung `FMA7309`: 156 elements; left lung `FMA7310`: 124 elements.
- Their elements are bronchial, arterial and venous structures, not lung envelopes.
- Whole-lung sets exactly equal the unions of the corresponding lobe sets:
  `FMA7333`, `FMA7337`, `FMA7383` (right); `FMA7370`, `FMA7371` (left).
- The IS-A archive has 2,234 OBJs; PART-OF has 1,258. All 1,258 shared elements
  have identical non-comment geometry content; swapping archives does not fix this.
- No mapped solid lung/lobe or pleural-envelope replacement was identified in these
  two cached archives. Other official releases/services have not been ruled out.
- The preserved official README explains that compound organs are sums of atomic
  elements, not separately supplied meshes. See [README_e.html](bodyparts3d/README_e.html).

The existing candidate further simplifies these branch structures. Its topology
also needs review before accepting that representation; watertight source vessels
are not evidence of a solid lung envelope. Do not synthesize a hull and represent
it as recovered official lung geometry.

## Remaining path to release

1. Obtain suitable official solid lung/lobe and missing muscle sources with
   verifiable licensing/provenance, or obtain separate written permission covering
   the exact desired legacy artifacts and adaptations. Record scope and hashes.
2. Alternatively, obtain explicit owner approval for different geometry/coverage.
   This would change the product; it is not an automatic licensing fix.
3. Build the complete candidate exclusively from approved sources. Review all
   organs, muscles and bones, not just the six flagged selections. Resolve mesh
   topology, labels, decimation and source-header/license discrepancies as needed.
4. Present rendered comparisons for owner approval. Replace GLB, embedded JS,
   manifest, provenance, credits and license notices together only after approval.
5. Run geometry/provenance, viewer, Flutter, packaged-notice and device/accessibility
   checks. MIT code and approved CC BY 4.0 models permit commercial use under their
   respective terms, not unconditional use without notices or restrictions review.
6. Review Cureocity's actual EULA, store distribution, DRM and model modifications
   with counsel. Record the host credits entry point. No Cureocity host files or
   store agreements have been inspected or modified in this repository task.
7. Make the personal repository public only after the migration/approval gate.
   A visibility change exposes Git history too: historical CC BY-SA models retain
   their historical license. Do not describe every Git revision as CC BY 4.0.
   History removal/rewrite, if desired, needs a separate explicit decision.

## Draft request to DBCLS / rights holder

Do not send confidential Cureocity material. The following is a draft, not a sent
request or evidence that permission was granted:

> We intend to distribute a public MIT-licensed viewer and use its anatomy assets
> in a private commercial application. We would like to use official CC BY 4.0
> BodyParts3D geometry with visible attribution and modification notices.
>
> In Release 4.0, FMA7309/FMA7310 and their lobes resolve to bronchovascular
> structures, and FMA13377/FMA13378/FMA13358/FMA13359 are not in the checked IS-A
> mapping. Can you identify official solid lung/lobe, rectus abdominis and
> latissimus dorsi surface datasets, their stable downloads and applicable licenses?
>
> Our current mirror-derived meshes come from revision
> f0eeb6e843380cfe6b83797cf8c3e1af74de5e61 of
> https://github.com/Kevin-Mattheus-Moerman/BodyParts3D and retain CC BY-SA 2.1 Japan
> notices. We have not assumed your newer grant relicenses those artifacts.
> If you can authorize those exact assets/adaptations under CC BY 4.0 or separate
> commercial terms, please confirm the scope, attribution and applicable conditions.
> Please also clarify the legacy wording in official OBJ headers relative to the
> 27 February 2025 license update.

Keep any response with the release provenance and obtain legal review where needed.
