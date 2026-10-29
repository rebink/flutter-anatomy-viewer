# No-purchase female illustration candidate

This supersedes the cosmetic candidate as the default browser preview, not as an
approved anatomical model. **The Flutter app is unchanged. Candidate promotion
and package publication remain gated; keep `publish_to: none`.** The owner has
separately approved public source release with the current bundled models.
The result is an illustrative composite, not the complete female-source atlas
requested in the source review. No fee, proprietary library or paid service is
required by this build.

## What changed

- Preserve HRA source coordinates/proportions. Remove abdomen flattening and the
  shared athletic/slimming warp; a narrow waist is not an accuracy criterion.
- Extract 44 missing regions afresh from the checksum-pinned official BodyParts3D
  Release 4.0 archive, with its separately preserved current CC BY 4.0 evidence.
  No legacy geometry is reused for those 44 regions.
- Retain four explicitly labeled legacy exceptions: left/right rectus abdominis
  and latissimus dorsi. Their concept IDs are absent from both Release 4.0
  mapping trees; the archive headers also contain no corresponding names. Do not
  substitute obliques or other neighboring muscles to make coverage appear full.
- Preserve all 85 existing candidate IDs: shell, 23 organ selections, 28 muscle
  selections and 33 bone/group selections. Cervix remains grouped with uterus.
- Mark adapted structures in the selectable list and show the source/license on
  selection. Credits remain available independently of the 3D loading outcome.
- Use open-source Chromium headless shell for both browser check suites instead
  of requiring Google Chrome. Pin the geometry-building Python dependencies.

## Build and inspect

Validated toolchain target: Python 3.13, Node 20+, existing npm lockfile. Downloads
need network access; the built preview needs only a loopback server. On Linux,
Playwright may additionally require system browser dependencies. The HRA download
is about 375 MB and the official archive is about 130 MB. Leave adequate disk space
for source data, the Python environment, browser and generated artifacts.

```sh
npm ci
npm run setup:browsers
python3 -m venv .venv
. .venv/bin/activate
python -m pip install -r tools/requirements-anatomy.txt
npm run test:geometry
npm run build:female
npm run test:female
npm run test:viewer
npm run preview:female
```

Open the printed localhost URL; stop the preview with Ctrl-C. The preview binds
only to `127.0.0.1`. It is not a hosted service or a native Flutter model selector.
The builder downloads only known official URLs with fixed hashes; changed cache
or download bytes fail closed, rather than being silently repinned. It does not
import/execute the legacy builder or change the bundled app models.

Outputs are in `.research/female-open-candidate/`:

- `anatomy.glb`, embedded `anatomy-data.js`, `anatomy-manifest.json`.
- `anatomy-provenance.json`: source URLs/hashes, generator/inventory hashes,
  official license-evidence hashes and hashes for every candidate file. This
  record is finalized only after validation passes; failed builds cannot preview.
- `CREDITS.txt`, `HRA_METADATA.yaml`, `BODY_PARTS_LICENSE.txt`,
  `LEGACY_BODY_PARTS_LICENSE.txt`, `THREE_LICENSE.txt`.
- Browser screenshots with the `same-ui-` prefix after `npm run test:female`.

The earlier `.research/female-generated-candidate/` is preserved as historical
research. [GENERATED_CANDIDATE.md](GENERATED_CANDIDATE.md) describes that older,
cosmetically warped 37-HRA/48-legacy model, not the new build.

## Exact source and license boundaries

| Source | Regions | Treatment |
| --- | ---: | --- |
| HRA female v1.10 reference set | 37 | CC BY 4.0; source world transforms, mesh selection/combination and reduction; no shape warp |
| Fresh official BodyParts3D Release 4.0 | 44 | CC BY 4.0; male-derived illustrative registration, not new female anatomy |
| Existing mirror-derived BodyParts3D | 4 | CC BY-SA 2.1 Japan; same attribution/share-alike duties as before |

Original application code remains MIT. These counts do not grant a blanket MIT
or CC BY-only license to the combined GLB. Mixed-source distribution review is
still unresolved. Do not remove the four legacy notices or rename their license.
The old BodyParts3D OBJ headers differ from the updated official database grant;
retain that discrepancy and the evidence in `docs/licensing/bodyparts3d/`.

HRA DOI: https://doi.org/10.48539/HBM637.DWBM.744. Pinned source records, object
metadata, DVC pointer and bibliography are retained alongside this guide. Preserve
"Courtesy of the U.S. National Library of Medicine" and no-endorsement notices.
The united female reference set includes reference components such as Allen
brain; membership does not prove that every component came from a female donor.

## Available-data workarounds and their limits

Denver's CC BY 4.0 female lower-body dataset remains the preferred source upgrade:
https://digitalcommons.du.edu/visiblehuman/1/. Its 87.8 MB final STL archive and
301.9 MB aligned CT download both returned Cloudflare HTTP 403 in direct requests
and a fresh, headed browser. SimTK/DOI/author code point back to the same host; no
authorized mesh mirror was located. No challenge bypass or unverified reupload
was used. A verified archive hash cannot be invented before obtaining the bytes.

The original female CT **is** accessible at the official NLM host:
https://data.lhncbc.nlm.nih.gov/public/Visible-Human/Female-Images/radiological/normalCT/index.html.
A 253,201-byte `.Z` sample returned HTTP 200, decompressed to a 512x512 GE image,
and its official header identifies female sex. This is not the aligned Denver
DICOM archive or a segmented muscle atlas. Full-volume reconstruction, individual
muscle segmentation and review remain work, not an automatic fallback that has
already been completed. NLM's separate attribution/terms apply; do not label its
raw data MIT or CC0. ITK-SNAP GPLv3 is an available free manual-segmentation route.

## Remaining acceptance gates

The 48 adapted structures are still male-derived. Their existing coarse landmark
registration is explicitly illustrative. The new build is not proof of correct
joint fit, organ containment, female skeletal morphology or muscle attachments.
No qualified anatomical review, patient validation or physical-device performance
check has occurred. Keeping source proportions avoids an unsupported aesthetic
change but does not resolve cross-source alignment.

Pipeline checks cover expected IDs, source labels/licenses, source and official
evidence hashes, finite meshes/laterality, GLB/manifest parity, reduction
bounds/area and embedded bytes. Unit checks cover transform preservation,
deduplication, failed-download cleanup, cache rejection, allowed source URLs,
missing/changed license evidence, symlink/hardlink output isolation and failure
invalidation. A failed rebuild must be corrected/rebuilt before previewing it. Browser checks cover all selection buttons,
source disclosure, model/mode isolation, controls, mobile layout, failed-load
credits and retry. These are engineering checks, **not anatomical acceptance**.

## Engineering verification (2026-10-08)

- 10 offline Python unit tests passed, including all three review fixes:
  rejected-build invalidation, evidence verification and link-safe outputs.
- The rebuilt GLB has 85 regions, 541,015 triangles and 9,810,816 bytes;
  standalone candidate provenance/geometry checks passed.
- Candidate browser suite and bundled viewer regression passed on open-source
  Chromium headless 140.0.7339.186 / Playwright 1.55.1.
- `flutter analyze --no-pub` found no issues; all 7 Flutter tests passed.
- Active LSP checks on the six changed code/config paths reported no findings.
  The separate official 16-region candidate license checker also passed; it is
  not an anatomical or combined-model license approval.
- Inspected female front/side, muscles, bones and mobile screenshots. Layout and
  controls render, but hand/shell and cross-source joint registration differences
  remain visible. These screenshots do not satisfy anatomical acceptance.
- Confirmed no changes to `assets/`, `lib/`, `pubspec.yaml` or `pubspec.lock`.
  Python package metadata identifies trimesh/fast-simplification as MIT and
  NumPy under its open-source BSD/MIT/0BSD/Zlib/CC0 expressions.

Environment note: Playwright's installer stalled after the official Chromium
headless ZIP finished downloading on this machine. The ZIP passed `unzip -tq`;
its official contents were extracted to Playwright's normal browser cache for
these tests. The unmodified browser then passed both suites. This is not a
project dependency workaround or proof that fresh installation works on every OS.

Before release: obtain source/anatomical approval, resolve the remaining geometry
and mixed-license gaps, promote model/embedded data/manifest/provenance/notices
as one reviewed change, implement and test native switching, and complete the
native/transitive license and device audits. Do not claim the entire project is
done because this research preview runs.
