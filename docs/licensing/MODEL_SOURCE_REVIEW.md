# Free anatomy model replacement review

Reviewed 2026-10-07 for a public MIT-code repository and the private commercial
Cureocity app. No runtime assets or licenses were changed. This is source and
engineering due diligence, not legal clearance or clinical validation.

Follow-up: [commercial migration candidate](COMMERCIAL_MIGRATION_CANDIDATE.md)
implements the available regions in a separate blocked preview after the owner
reported no rights-holder response. The source gaps below remain unresolved;
this does not relicense old meshes or authorize a reduced-coverage app.

## What is actually going wrong

1. **The source releases are not equivalent.** The legacy mirror and official
   Release 4.0 archive do not offer identical anatomy. The official mappings lack
   FMA13377/FMA13378 (right/left rectus abdominis) and FMA13358/FMA13359
   (right/left latissimus dorsi). Independent name/alias searches in both official
   IS-A and PART-OF metadata and OBJ headers found no defensible substitutes.
2. **This is not an observed parser bug.** Metadata columns match the checker.
   A tempting parent, FMA20278/FMA78435, resolves to FJ1452/FJ1452M (external
   obliques), not rectus abdominis. Substituting it would falsely label anatomy.
3. **The lung mismatch precedes simplification.** Correct whole-lung IDs resolve
   to 156 right and 124 left bronchial/arterial/venous elements. Switching to lobe
   IDs produces the same element sets, not solid outer lung surfaces.
4. **Coverage checking is not a complete build.** The checker considers 77 regions
   and 73 resolve to elements, including the unsuitable lung representation.
   `tools/prepare_official_anatomy.py` still exports only 16 regions. The muscle
   and skeleton export work remains to be implemented, even where mappings exist.
5. **Licenses apply to particular assets.** The official archive's CC BY 4.0
   notice cannot simply be pasted onto the old mirror-derived models. A source's
   software license or a free web viewer does not license every model/texture.

The earlier researcher failure was a run that returned no final response, not an
app failure. It was resumed and its findings recovered. This pass independently
rechecked the mappings and broadened the source search. Search-engine CAPTCHA
limited general discovery; primary project sites and actual downloads were checked.

## Shortlist

| Source | Relevant coverage/formats | Model terms verified | Suitability here |
| --- | --- | --- | --- |
| [Official BodyParts3D](https://dbarchive.biosciencedbc.jp/en/bodyparts3d/download.html) | Organs, muscles, skeleton; OBJ archives | [CC BY 4.0](https://dbarchive.biosciencedbc.jp/en/bodyparts3d/lic.html) for archive database | Keep as the main candidate. Most current IDs resolve, but four muscles and solid lungs remain gaps; full builder/visual validation still needed. |
| [Human Reference Atlas](https://humanatlas.io/3d-reference-library) | Organ models, including solid lungs; GLB plus anatomy crosswalk | Object-specific CC BY 4.0 verified for male lung v1.4 | Best verified lung candidate. Not a verified complete muscle/skeleton replacement. Check each additional object's metadata. |
| [Open Anatomy Project](https://www.openanatomy.org/atlas-pages/atlas-spl-abdomen.html) | Regional organs, muscles and skeletal anatomy; downloaded abdomen archive includes VTK meshes | Dataset page says 3D Slicer License section B; archive LICENSE links Slicer terms | Permissive proprietary-use candidate, with notice/modification and other conditions. Actual rectus mesh found; no latissimus match in this abdomen archive. Not a complete atlas replacement. |
| [AnatomyTOOL Open3DModel](https://anatomytool.org/open3dmodel-create) | Skeleton, upper/lower limb and hand source downloads; OBJ, GLB, Blender | Download rows link CC BY-SA 4.0; separate viewer is GPLv3; certain muscle textures cite BY-NC-SA 4.0 | Untextured OBJ is worth auditing if share-alike is acceptable. Do not import textured bundles as commercially cleared. Full desired muscle/organ coverage not yet verified. |
| [Z-Anatomy](https://github.com/Z-Anatomy/Models-of-human-anatomy) | Whole-body Blender template ZIP: organs, muscles, skeleton | Headline CC BY-SA 4.0, but asset notice lists legacy BY-SA and NC source components | Broadest whole-body lead, not a commercially cleared drop-in. Audit exact components; do not rely on the headline license alone. |

All listed projects offer data/downloads rather than only a free viewer. Availability
and license findings do not prove anatomical accuracy, complete coverage or that
our adaptation is approved. No complete CC0/CC BY-only replacement covering every
current selection was verified in this pass; this is not proof that none exists.

## Concrete new lead: abdominal rectus mesh

Downloaded and inspected the ZIP directory and atlas metadata:

- URL: https://www.openanatomy.org/atlases/nac/abdomen-2016-09.zip
- Size: 34,861,066 bytes; 172 archive entries.
- SHA-256: `1cf85dbc820767b7c3095790ff38ae150a085af713061a2f0e950e355e4dc7c8`
- Mesh: `abdomen-2016-09/Data/Model_32_rectus_abdominis_muscle.vtk`
- Metadata ID: `#rectus_abdominis_muscle`, referencing that exact mesh.
- Format: binary VTK POLYDATA, 38,187 points, TRIANGLE_STRIPS connectivity;
  not a GLB ready for the app. Basic connectivity decoding yielded 75,564
  triangles with three distinct vertex indices; no anatomical suitability is implied.
- The archive contains one named rectus model, not separately labeled left/right
  rectus meshes. Completeness, laterality separation, scan truncation and body
  alignment have NOT been validated. It is not yet a replacement for both buttons.
- No latissimus entry was found in this archive's mesh names or atlas metadata.
- `abdomen-2016-09/LICENSE.md` explicitly releases the atlas under the 3D Slicer
  License; the dataset page identifies section B.

The [linked Slicer terms](https://www.openanatomy.org/atlas-pages/slicer-license.html)
include data and explicitly allow incorporation into proprietary programs. They
require applicable notices and Part B terms/preface, clear modification markings,
and preserve third-party permission caveats. They also include indemnification
and research/clinical warnings. This is a custom permissive license, not MIT/CC0.
Review those conditions rather than describing it as unrestricted.

The separately listed [Mauritanian thorax archive](https://www.openanatomy.org/atlas-pages/atlas-mauritania-thorax.html)
linked ZIP returned HTTP 404 during this review; do not count it as a successfully
retrieved replacement. No alternate thorax download was verified.

## Concrete pitfalls in whole-body alternatives

### Z-Anatomy

[Asset notice at pinned revision](https://github.com/Z-Anatomy/Models-of-human-anatomy/blob/b767bd814dd7db876dec5e7914d82d2d4ae1a316/License.txt)
lists models used as reference/included and adapted, including:

- Inner ear by University of Dundee School of Medicine: CC BY-NC-SA 4.0.
- Kidney by Lissie Cowley: CC BY-NC 4.0.
- BodyParts3D: CC BY-SA 2.1 Japan.

The wording does not establish which exact meshes incorporate each source versus
merely reference it. This is an unresolved component-provenance issue, not proof
that every Z-Anatomy muscle is noncommercial. Do not distribute the entire bundle
in Cureocity based solely on its blanket BY-SA statement. Seek clarification or
isolate independently verified components.

### AnatomyTOOL

The [source-file page](https://anatomytool.org/open3dmodel-create) lists muscle
textures derived from UBC/Claudia Krebs "Thoracic walls" under NonCommercial
ShareAlike terms. Its OBJ downloads explicitly omit textures/colors/normal maps;
those are preferable to investigate with our own procedural materials. Removing
textures does not automatically establish clean geometry provenance.

Source downloads responding HTTP 200 to HEAD checks (archives not inspected):

- [Skeleton OBJ ZIP](https://caskanatomy.info/open3dmodelfiles/overview-skeleton/overview-skeleton-obj.zip): 9,387,090 bytes.
- [Upper limb OBJ ZIP](https://caskanatomy.info/open3dmodelfiles/upper-limb/upper-limb-obj.zip): 21,336,550 bytes.
- [Lower limb OBJ ZIP](https://caskanatomy.info/open3dmodelfiles/lower-limb/lower-limb-obj.zip): 20,168,177 bytes.

The source page says bilaterally identical structures are usually supplied only
on the right, and the viewer mirrors them. Any import must implement correct
mirroring/normals and separate selection identities, not assume both sides exist.
The project's "Non-commercial, University based" description is not itself an
NC asset license; the explicit texture notices are the relevant warning.

## Commercial-use clarification

CC BY-SA is **not a ban on commercial use** and does not automatically require
publishing unrelated Cureocity application code. Shared model adaptations retain
applicable share-alike terms; attribution and compatible EULA/store/DRM treatment
still matter. A public repository is not itself prohibited by these licenses.
The owner has since approved public source release with the current CC BY-SA
models. Replacement geometry and registry publication remain separate approvals.

CC BY 4.0 removes share-alike, not attribution or other conditions. NC assets need
separate commercial permission or replacement. A credits button does not cure a
missing license grant, NC restriction or incompatible downstream restrictions.

## Recommended next implementation slice

1. Keep the verified official BodyParts3D source as the base; do not rewrite all
   anatomy merely because six current selections are problematic.
2. Implement a separate full-coverage candidate builder, with explicit per-region
   source provenance and unresolved regions remaining a hard promotion blocker.
3. Validate/extract HRA lungs and investigate the Open Anatomy rectus mesh for
   complete bilateral geometry. Review registration between different donors.
4. Obtain a permissively licensed full latissimus pair (and rectus alternatives if
   needed), or explicit permission covering the precise legacy meshes. No verified
   no-share-alike latissimus replacement was found in this pass.
5. If choosing the share-alike route instead, audit untextured AnatomyTOOL/Z-Anatomy
   components and decide on distribution obligations before importing them. These
   sources do not meet a CC BY-only goal simply by being free.
6. Promote only after full visual, provenance, attribution and interaction checks;
   leave Cureocity's legal/product review separate from anatomy engineering.

## Evidence trail

Fetched primary documents are cached locally under `.research/sources/` (not
published with the app). The hashes below identify fetched text, not model bytes:

| Document | SHA-256 of cached text |
| --- | --- |
| Z-Anatomy raw asset license | `f4b96aad005164f0ee445ebd11257bec45418d9259c3f1f856191cf7c005d69f` |
| AnatomyTOOL source downloads | `89df745694024be16ce9cf45095d80a19309f66b0858d4f896bf70e65af048e2` |
| Open Anatomy abdomen page | `8d977b503180bd6e105dcd9dfa241a3ef019642adb7f10f9ab94524cd296b70a` |
| Open Anatomy linked Slicer license | `d2a2cb1a78a2ce1a9d6f61cc343cd18a8ca34ff9c671d9a7d95d37cb72ac34f5` |

HRA's immutable asset URLs and byte hashes are already preserved in
[the lung source review](hra-lung/REVIEW.md). Existing official BodyParts3D source
pins and evidence remain unchanged. A content hash proves byte identity, not
source ownership, legal clearance or anatomical correctness.
