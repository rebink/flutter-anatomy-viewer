# Historical gap-filled female candidate

**Superseded build:** [OPEN_CANDIDATE.md](OPEN_CANDIDATE.md) documents the current
source-preserving preview. The old output is retained for comparison, but the
builder/preview commands below now target the new candidate. This page records
the earlier cosmetic experiment; it is not the current implementation guide.

**Current gate:** the user now requires genuine female muscles and bones and chose
to assess a complete source before replacement. This mixed-source, cosmetically
warped candidate does not meet that requirement. See
[complete-source review and acceptance gate](COMPLETE_SOURCE_REVIEW.md). Further
cosmetic refinement is not a substitute for source and anatomical review.

User approved filling the missing parts, keeping sourced female geometry and
creating or adapting missing anatomy. This candidate does that by adapting
existing meshes rather than inventing less reliable procedural organ shapes.
It is not an original, license-free or clinically validated female atlas.

## Result

- Builder: `tools/prepare_female_candidate.py`.
- Output: `.research/female-generated-candidate/anatomy.glb` (local, ignored).
- 85 selectable regions: body shell, 23 organ regions, 28 major muscles and 33
  bones/bone groups. All 77 previous IDs remain, with eight female-specific IDs.
- Added IDs: `breast_left`, `breast_right`, `uterus`, `vagina`, `ovary_left`,
  `ovary_right`, `fallopian_tube_left`, `fallopian_tube_right`.
  Cervix is included in the uterus group, not a separate selectable region.
- 37 regions extracted from HRA female geometry; 48 adapted from the existing
  legacy geometry. Stomach and esophagus use adapted real meshes, not new shapes.
- 638,937 triangles; 11,577,076-byte GLB (approximately 11.0 MiB), down from the
  374,505,632-byte HRA source by selecting and reducing relevant structures.

These are selection counts, not proof of anatomically complete systems. There
are still only the curated major muscles and grouped bones of the original app,
not all human muscles or all 206 bones.

## Modifications and limits

HRA mesh descendants are combined under the app's region IDs while preserving
source world transforms. Coincident vertices are welded before reduction to
avoid deleting disconnected seam triangles. Existing male-derived regions use
an explicitly illustrative piecewise height/width/depth warp and arm-pose shift.
No patient data, learned reconstruction or anatomical expert registration is used.

The outer shell now has a flatter anterior abdomen, smoothly blended into the
surrounding skin. This is an explicit aesthetic adaptation, not measured anatomy.
The initial abdomen-only refinement changed depth in 221 shell vertices, at most
31.14 mm inward, without altering the 84 internal meshes. The subsequent athletic
proportion pass described below now also adjusts internal geometry. Source hashes/licenses are unchanged;
regenerated manifest, credits and output hashes record the modification. Synthetic
boundary/symmetry checks and a generated-shell profile check guard the refinement.
Front and side screenshots were inspected; `same-ui-female-side.png` shows the
updated profile. These checks do not establish collision-free or clinical anatomy.

The current candidate additionally uses a smooth, shared athletic-proportion warp:
central waist width tapers by 14% at its peak, with separate 9% hip, 10% thigh and
4% calf bands. Depth tapers by 10%, 8%, 8% and 4% respectively. Bands overlap and
blend continuously; the adjustment fades out toward the arms. Shoulder width,
head, feet and overall height are preserved. The same coordinate transform is
applied to all 85 regions rather than shrinking the shell around unchanged organs.
This is stylization, not measured athlete anatomy or a fix for pre-existing
registration differences. All region topology and heights were checked against
the previous candidate; transformed vertices match the shared warp. Shell surface
area is 96.71% of the previous candidate. Boundary, symmetry, proportions, build
and browser checks pass; updated front and side screenshots were inspected.

Separate body/organs/muscles/bones/reproductive previews render successfully.
Visual review still shows registration differences at joints and extremities,
including hand/shell alignment; hip-to-femur fit also needs refinement. This
candidate is NOT ready for promotion merely because its selections and meshes
exist. Reduction changes surface detail, particularly on the body/face. Bounds,
area checks and successful rendering do not validate organ placement, muscle
attachments, collision-free geometry or female skeletal morphology.

## Rights and attribution

HRA-derived regions retain CC BY 4.0 attribution and source metadata. Adapted
legacy regions retain CC BY-SA 2.1 Japan; adaptation does not remove share-alike.
There is no blanket MIT or CC BY-only license for the combined file. Mixed-source
adaptation/distribution compatibility needs review before release.

The output includes per-region `anatomy-manifest.json`, input/output hashes in
`anatomy-provenance.json`, `CREDITS.txt`, `HRA_METADATA.yaml`,
`BODY_PARTS_LICENSE.txt` and `THREE_LICENSE.txt`. The preview exposes credits
independently of successful model loading. No bundled app assets, production
credits, package settings or publication gates were changed.

## Reproduce and check

Use the existing asset-build environment (trimesh 5.1.1 and
fast-simplification 0.2.0). Obtain the pinned HRA GLB as described in REVIEW.md;
the builder refuses changed HRA or legacy GLB bytes. It never downloads or writes
to the app's asset directory.

```sh
/tmp/anatomy-tools/bin/python tools/prepare_female_candidate.py
/tmp/anatomy-tools/bin/python tools/prepare_female_candidate.py --check
```

The build/check passes all 85 IDs, GLB/manifest parity, finite nonzero bounds,
laterality, per-region face counts, source-to-reduced area limits, output hashes
and retention of the legacy notice. The area regression requires at least 90%
of the original shell area (50% for other reduced regions), with at most 15%
area growth. These limits catch catastrophic reduction, not anatomical errors.

Local research preview (scripts are ignored research artifacts):

```sh
node .research/female-generated-candidate/preview.cjs
node .research/female-generated-candidate/preview.cjs --serve
```

Browser checks pass all five views, mesh counts, readable credits, no page errors
and 390px layout without horizontal overflow. Screenshots are in the same folder:
`female-body.png`, `female-organs.png`, `female-muscles.png`, `female-bones.png`,
`female-pelvis.png`, posterior muscle/bone views and `female-mobile.png`.

JS/CJS diagnostics are clean. Python LSP uses an interpreter without numpy and
trimesh and reports those two missing imports; the pinned asset-build environment
imports them and runs the builder successfully. No app/native test or mobile GPU
performance claim is made because production integration has not occurred.

## Same-UI male/female comparison

A tracked local preview now reuses `assets/viewer/viewer.js` and the app's viewer
HTML directly rather than the earlier beige research renderer. Its surrounding
browser UI follows the current Flutter screen: dark teal palette, translucent
rim-lit shell, Body Parts / Muscles / Bones, opacity slider, structure chips,
focus/reset, accessible rotate/zoom controls, fictional lung report cards and
reduced motion. A Male/Female selector switches both model and structure lists.
Existing structure labels are read from the literal maps in `lib/main.dart`.

```sh
node tools/preview_anatomy_candidate.cjs
# Open the localhost URL printed by the command; Ctrl-C stops the server.
node tools/preview_anatomy_candidate.cjs --check
```

The wrapper is `tools/candidate-preview.html`. The server binds only to loopback
and uses the existing installed Playwright/Chrome for checks. It verifies the
candidate GLB hash and adds a presentation-only translation of `[0, 0.785, 0.155]`
in memory to match the renderer's existing camera coordinates. It does not scale
or rewrite candidate geometry, edit the shared renderer or modify app assets.

The credits dialog stays available even when model loading fails, shows the
currently selected model's bundled notices, scrolls, and supports Escape/Close.
The female candidate warning stays visible. The medical report cards are explicitly
fictional and do not imply generated diagnoses or assessed anatomy.

Browser checks cover male/female list isolation (15/23 organ regions), all eight
female additions, 28 muscles, 33 bones/groups, mode switching, focus/reset,
selection retention while changing opacity, camera buttons, 390px layout and
credits after a deliberately failed model load. Screenshots use the `same-ui-`
prefix in `.research/female-generated-candidate/`, including `same-ui-female.png`,
`same-ui-mobile.png`, `same-ui-male.png`, `same-ui-muscles.png` and
`same-ui-bones.png`. This is a browser preview with the same renderer and matching
layout, not an implemented native Flutter Male/Female selector. App production
code/assets and the anatomical/rights approval gates remain unchanged.

Next gate: refine and approve the mixed-source fit and licensing treatment, then
integrate native Male/Female switching with the matching region lists and notices.
