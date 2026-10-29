# Female muscle and skeleton authenticity gate

## Decision

The user requested genuine, correct female muscle/bone anatomy and chose to find
and assess a complete source before replacing geometry. The existing candidate
remains unapproved. No new geometry has been purchased, downloaded or promoted in
this investigation; no vendor has been contacted. A product listing is not
anatomical validation, and verified source hashes establish identity, not accuracy.

## Audit of the current generated candidate

The original HRA input SHA-256 and all output hashes in candidate provenance were
checked successfully. Per-region manifest counts are:

| Current selections | HRA female-derived | Adapted legacy male-derived | Anatomically validated |
| --- | ---: | ---: | ---: |
| Muscles | 2 | 26 | 0 |
| Bones / bone groups | 13 | 20 | 0 |

The only female-source muscles used are left/right rectus femoris. Female-source
bone selections are cervical/thoracic/lumbar spine groups, sacrum, sternum, and
bilateral femur, patella, tibia and fibula. The current hip bones, skull, mandible,
ribs, clavicles, scapulae, arm bones, hand groups and foot groups are adapted legacy
meshes. These are current mapping counts, not all potentially usable HRA coverage.

All 28 muscle and 33 bone selections subsequently received the athletic-proportion
warp. Even the female-derived subset therefore no longer preserves its reference
proportions. This cosmetic deformation must not be described as verified female
anatomy. Prior rendering, picking, area and symmetry tests do not validate skeletal
shape, muscle attachments or anatomical registration.

## Shortlist and exclusions

### 1. Zygote female anatomy collection: full-body evaluation candidate

Primary vendor pages:

- https://www.zygote.com/poly-models/3d-human-collections/3d-female-anatomy-collection
- https://www.zygote.com/poly-models/3d-female-systems/3d-female-skeleton
- https://www.zygote.com/index.php/poly-models/3d-female-systems/3d-female-muscular-system
- https://www.zygote.com/terms

The collection page describes a CT-based skeleton, individually named/grouped
bones, and systems correlated in scale and proportion. It lists female skeletal,
muscular, integumentary and organ systems. The muscular-system page describes
superficial/deep axial and appendicular muscles, individual grouping and origins
and insertions; the skeleton is sold separately when buying that muscle product.
The skeletal product lists female pelvic/brow features and CT-derived geometry.

These are vendor assertions, not independently verified mesh findings. The pages
do not establish the specific female scan/donor provenance, expert sign-off,
complete correspondence to our selection IDs, or the quality of exported files.
Obtain an evaluation asset and the supporting information before acceptance.

The complete collection requires a sales quote. Individual pages display $6,560
for muscles and $4,260 for skeleton; these are unconfirmed page prices, not an
app license quote or a budget commitment. Do not infer that a standard purchase
permits bundled GLB/JavaScript redistribution. The public terms defer product
rights to the accompanying license and prohibit redistribution outside it.
Obtain written permission for this exact use: offline Flutter/WebView embedding,
GLB conversion and decimation, interactive picking, commercial app distribution,
asset extraction risk, and any future package redistribution. A reusable package
may require rights beyond those for a single app. No license has been accepted.

Verdict: strongest complete candidate found in this bounded search; request a
matched female evaluation set and app/package licensing terms. NOT approved yet.

### 2. Visible Human female musculoskeletal geometries: credible but partial

- Project: https://simtk.org/projects/3d-vh-geometry/
- Paper: https://www.nature.com/articles/s41597-022-01905-2
- Dataset DOI referenced by paper: https://doi.org/10.56902/COB.vh.2022.0

Andreassen et al., Scientific Data 10, 34 (2023), describe segmentation from the
Visible Human female and male cryosections, with 76 muscles and 28 bones per
subject plus cartilage/ligament/fat geometry. Coverage is lower extremity, not a
full-body muscle/skeleton atlas. The authors describe anatomical review, separate
left/right segmentations and overlap removal, but also acknowledge uncertain
boundaries, reconstructed damaged areas and missing tendon structures.

The paper identifies the female donor as 59 years old, 62 inches, 88 kg, BMI 36.
It is therefore not evidence for an athletic donor physique. Genuine donor anatomy
and an aesthetically slim silhouette are different acceptance criteria.

The article is CC BY 4.0; that alone does NOT verify the separate downloadable
mesh dataset license. Dataset terms and artifact hashes still require review.
No mesh files were downloaded in this investigation.

Verdict: worthwhile lower-body reference/possible partial source, not a complete
replacement. Combining it with another source would require registration review,
even if both refer to the Visible Human female.

### 3. AnatomyTOOL / Open3Dmodel: not a female-specific replacement

https://anatomytool.org/open3dmodel-about documents the male MRI-derived
BodyParts3D -> Z-Anatomy lineage and retention of many original muscle outlines.
Anatomist review and additional female organs do not turn that skeleton and
musculature into a female-specific source. Its historical license descriptions
also do not override object-specific/current licenses or our existing notices.

Verdict: not a solution to this request's female-provenance gap.

### 4. MakeHuman / MPFB: alternative outer body only

Primary documentation checked on 28 October 2026:

- https://static.makehumancommunity.org/about/license.html
- https://static.makehumancommunity.org/mpfb/faq/can_i_sell_models.html

The project license page states that core graphical assets are CC0. Its sales
FAQ explicitly includes the base mesh, targets and skins, while warning that
third-party assets can have different licenses. Tool source code is separately
GPL (MPFB) or AGPL (MakeHuman); do not confuse this with the core asset license.
The FAQ fetch returned its relevant answer but an incomplete-extraction warning;
the independently retrieved project license page supplies the core CC0 evidence.

This is an option for creating and reviewing a different female exterior, not a
source of matched internal organs, female muscles or a female skeleton. A more
attractive surface does not establish internal anatomical correctness. Do not
put unregistered male-derived internals inside a new shell and describe the
result as a validated female atlas. No MakeHuman geometry or third-party asset
has been downloaded, generated, licensed individually or approved for this app.

Verdict: useful no-cost exterior-only evaluation path. Not a complete replacement
for the requested female anatomy; anatomical registration remains a separate gate.

The current HRA female reference remains useful for available female structures,
but its missing full-body muscle/bone coverage is documented in REVIEW.md.
Generic marketplace titles and generated anatomy were not accepted as evidence.
This search does not prove that no complete open female atlas exists; none was
verified here.

## Acceptance gate before replacing the candidate

1. Obtain a single matched female skeleton/muscle set, preferably with its shell
   and organs in the same reference frame, plus version and scan/model provenance.
2. Verify every required muscle and bone/group against a delivered inventory and
   actual nonempty meshes. Record missing structures rather than substituting
   unlabelled male meshes or inferring completeness from a product title.
3. Verify female-specific skeletal features, laterality, units, joint alignment,
   and each muscle's origin/insertion with a qualified anatomical reviewer.
   Investigate the current HRA six-lumbar-level labeling before mapping spine IDs.
4. Remove cosmetic proportion warping from the reference anatomy pipeline. Use a
   documented female athletic reference if that physique is required; do not claim
   that slimming a reference mesh preserves its anatomical validation.
5. Approve embedding/distribution permissions, attribution and modification
   notices. Keep source hashes and untouched originals; assess simplification
   against anatomical landmarks rather than only mesh counts or area ratios.
6. Only then replace geometry, manifest, provenance and notices together and rerun
   selection, switching, loading/credits and front/side/back visual checks.

The user has not approved a purchase. Next external dependency is a suitable
licensed evaluation asset with provenance, not another cosmetic mesh adjustment.
All existing publication and production-promotion gates remain unchanged.

## Retrieved evidence

Fetched primary-source text is cached under `.research/sources/<SHA-256>.md`.
Hashes below identify the fetched text, not model files or legal approval.

| Source | SHA-256 |
| --- | --- |
| Zygote collection | `3c6eda7abe3454f2939e8c1340561b132a67d25a164c6382d38fdb0e3608df93` |
| Zygote muscles | `60418cb95ae22ca25db253535429b92197ac02618dfc8186a27cd6adc0c3539e` |
| Zygote skeleton | `1030dfe8659cfcd34108e26af8bae4e51f80b6603b058111909ff0d49f85771e` |
| Zygote terms | `44a56cb3e3a60b165a5fe8a29a91dc60a775f85955b9c6198d8adf9fb83b74dd` |
| SimTK project | `78cf5453d41a4553d79a96e3d09be205ad3f68e7074fb54dd294fd995309e190` |
| Scientific Data paper | `0b0a2baf116c641953ffeff847096f14d902fc7a71d3a574d26820e578026c29` |
| AnatomyTOOL provenance | `0a29a32666b879235f7cc36cce35f153ae7a22f74b7929b9285767e14a4c7af0` |
