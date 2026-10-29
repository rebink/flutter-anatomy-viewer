# Female anatomy source candidate - not integrated

Follow-up: [gap-filled generated candidate](GENERATED_CANDIDATE.md) retains all
existing selection IDs using sourced female meshes plus explicitly labeled legacy
adaptations. It is separate from this original-source review and is not approved
for app integration.

Requested scope: separate Male/Female anatomy views, including a distinct female
body and sex-specific organs, with shared anatomy only where appropriate. This
is anatomical model selection, not inference of a person's gender identity.

## Verified source metadata

The Human Reference Atlas provides a female reference organ set:

- Title: 3D Reference Organ Set for United, Female, v1.10.
- Authors: Kristen Browne and Heidi Schlehlein.
- DOI: https://doi.org/10.48539/HBM637.DWBM.744
- Library: https://humanatlas.io/3d-reference-library
- Repository revision: `29888dcc5f32dae28c7a07c41171c822275360c3`.
- Object directory: `digital-objects/ref-organ/united-female/v1.10/raw/`.
- Object-specific metadata declares CC BY 4.0 and lists
  `3d-vh-f-united.glb` plus `crosswalk.csv` as its data.
- The description identifies the National Library of Medicine Visible Human
  Dataset as the source. Preserve its bibliography and attribution context.

Original metadata and crosswalk are preserved alongside this review.
`sources.json` records their immutable URLs and SHA-256 hashes. These hashes
identify evidence bytes, not legal clearance or anatomical validation.

## Coverage evidence and limits

The crosswalk contains 875 data rows, including labels for:

- Body skin and left/right mammary glands.
- Uterus, cervix and vagina.
- Left/right ovaries and fallopian tubes.
- Bony pelvis and multiple shared internal organs.

The GLB has now been downloaded, checksum-verified, parsed and rendered in a
separate local preview. Actual mesh descendants exist for skin, uterus, cervix,
vagina, both ovaries, both fallopian tubes and mammary glands. Crosswalk rows
can still describe groups rather than separately selectable meshes. Visual
inspection confirms a distinct female body surface and reproductive structures,
not clinical accuracy or approval for integration.

This is NOT a complete female muscle/skeleton atlas:

- The muscular-system subtree contains eye muscles and bilateral rectus femoris
  with quadriceps tendons, not the app's 28 major-muscle selections.
- The skeletal-system subtree contains sternum/manubrium, pelvic structures and
  vertebrae/disks. Additional femur/tibia/fibula/patella nodes occur in the knee
  models outside that subtree; hierarchy location alone is not coverage proof.
- No node names matched skull, mandible, ribs, humerus, radius, ulna, clavicle or
  scapula. Full coverage of the app's 33 bone/group selections is unresolved.
- No stomach node or esophagus node was identified. The esophageal impression
  of the liver is not an esophagus. These current organ selections remain gaps.
- The source labels six lumbar vertebrae; do not assume a textbook five-level
  mapping without anatomical review.

Do not reshape existing male geometry and call it a validated female atlas.

The app currently includes neither male nor female reproductive-organ selections;
a balanced sex-specific feature will need an explicit male coverage decision too.
No pregnancy-specific anatomy is requested or implied.

## Next implementation gates

1. DONE: download/checksum, hierarchy inspection and separate candidate renders.
   User/anatomical approval remains pending.
2. Map every current organ/muscle/bone selection against available geometry.
   Resolve missing coverage and male reproductive assets without silently dropping
   existing modes or mislabeling shared male-derived meshes as female anatomy.
3. Review anatomical registration before combining different donors/sources.
   Bounding-box scaling is not evidence of correct registration.
4. After source/geometry approval, add an accessible Male/Female model selector;
   switch shell, geometry and available structure lists together. Clear unavailable
   selections and preserve camera/mode behavior where valid.
5. Extend picking, loading/error, switching and attribution tests; inspect both
   rendered models. Promote model data, manifests, provenance and notices together.

Keep the mandatory credits control available even if loading fails. Retain CC BY
attribution and modification notices for any incorporated HRA assets; do not
relicense the existing CC BY-SA legacy assets. Geometry remains illustrative and
not clinically validated. Existing migration/publication gates remain in force.

## Download and rendering evidence

The GitHub raw GLB URL returned HTTP 404 because this object uses DVC storage.
The pinned `3d-vh-f-united.glb.dvc` and repository DVC configuration identify
its content-addressed CDN location; both are preserved alongside this review.

- Source bytes: **374,505,632** (approximately 357 MiB).
- Source MD5: `5e4aca68ceea6aa9b21aa9c333c54fec`, matching the DVC pointer.
- Source SHA-256: `95f0c3d2f918582608692ca1139e8bdb18c147a16470e9ee9af8b276bd77c422`.
- GLB v2: **1,160 nodes, 956 meshes, 7,756,626 indexed triangles**.
- Body bounds: approximately `[-0.487, -0.793, -0.219]` to
  `[0.475, 0.865, 0.108]` in loaded scene coordinates. The different origin,
  width and pose preclude simply dropping this shell over the current app model.
- `geometry-inspection.json` records preview selections, bounds, render triangle
  counts and muscle/skeleton subtree mesh names. Render triangle counts can
  include extra transparent-material passes; they are not unique source counts.

Local research artifacts (ignored by Git):

- `.research/female-anatomy/3d-vh-f-united.glb`: original source, not modified.
- `.research/female-anatomy/female-body.png`: front body surface.
- `.research/female-anatomy/female-organs.png`: selected internal organs, not all
  available structures; breasts/other foreground structures can occlude organs.
- `.research/female-anatomy/female-pelvis.png`: reproductive anatomy with a
  translucent pelvic reference.
- `.research/female-anatomy/female-mobile.png`: narrow-screen preview check.

All four screenshots were inspected. The local preview retains source transforms
and changes only visibility/materials. Placenta geometry exists in the source but
is deliberately excluded from this non-pregnancy preview. No anatomy has been
mixed with the bundled male geometry, decimated or promoted.

Preview/check commands from this working copy (scripts and source are local
research artifacts, not shipped app tooling):

```sh
./node_modules/.bin/esbuild .research/female-anatomy/preview.js --bundle --outfile=.research/female-anatomy/preview.bundle.js
node .research/female-anatomy/preview.cjs
node .research/female-anatomy/preview.cjs --serve
```

The check passed: required mesh descendants, nonempty render counts, finite
bounds, all six pelvic selections, no page errors, and no horizontal overflow at
390px. Active JS/CJS diagnostics were clean. This checks rendering and labels,
not clinical anatomy or mobile-device performance. App tests were not rerun
because no application code or bundled assets changed.

The source is too heavy to ship unchanged. Selective extraction, simplification,
coverage resolution and approval must precede the Male/Female app switch.

## Retrieval limitations

General search was blocked by DuckDuckGo's anti-bot challenge. The library portal
returned no usable document text to the fetcher. The pinned GitHub repository tree,
object metadata and crosswalk supplied the evidence above. A broader parallel
metadata retrieval timed out after partial results; no claims rely on the missing
files. This review does not establish that HRA is the only suitable source.
