# HRA male lung candidate - not promoted

## Source and rights evidence

- Source: HuBMAP Human Reference Atlas, **3D Reference Organ for Lung, Male v1.4**.
- Authors: Kristen Browne and Heidi Schlehlein (2024).
- DOI: https://doi.org/10.48539/HBM532.KLZD.394
- Library: https://humanatlas.io/3d-reference-library
- Pinned source tree: https://github.com/hubmapconsortium/hra-kg/tree/29888dcc5f32dae28c7a07c41171c822275360c3/digital-objects/ref-organ/lung-male/v1.4/raw
- The object-specific `metadata.yaml` explicitly states **CC BY 4.0** and lists
  `3d-vh-m-lung.glb` and `crosswalk.csv` as its data. This finding is based on the
  object's metadata, not the repository's MIT software license.
- Original metadata and crosswalk are preserved here without edits; `sources.json`
  records immutable URLs and SHA-256 digests for all three upstream files.
- License: https://creativecommons.org/licenses/by/4.0/
- Metadata says the model derives from the Visible Human Male supplied by the
  National Library of Medicine; retain its bibliography and attribution context.

Suggested future credit, only when these assets are actually integrated:

> Browne, Kristen, and Heidi Schlehlein. 2024. "3D Reference Organ for Lung, Male
> v1.4." HuBMAP Human Reference Atlas. https://doi.org/10.48539/HBM532.KLZD.394.
> Licensed under Creative Commons Attribution 4.0 International:
> https://creativecommons.org/licenses/by/4.0/.

Append an accurate modification notice when extracting, transforming, reducing or
recoloring the model. Do not imply endorsement. Preserve the source metadata's full
citation/bibliography with the provenance. No modifications are yet approved for
shipping, and this review is not legal or anatomical certification.

## Geometry investigation

The downloaded GLB is 10,942,332 bytes and contains 58 meshes. The hierarchy
contains `VH_M_lungs_L` and `VH_M_lungs_R`, left upper/lower lobes and right
upper/middle/lower lobes. The crosswalk identifies the lungs as
`UBERON:0002168` (left) and `UBERON:0002167` (right).

A browser preview rendered only the `VH_M_lungs` subtree with illustrative teal
materials. Visual inspection confirms lung-like outer surfaces and lobes, unlike
the branching-only BodyParts3D Release 4.0 selection. The standalone screenshot
is local research evidence at `.research/hra-source-review/lungs-preview.png`;
it is not included in the application or a clinical validation.

The complete source GLB also includes bronchi and other named structures. Select
only reviewed lung descendants during extraction; do not blindly combine every
mesh. Crosswalk labels should not be treated as infallible anatomical validation.

## Reproduce source retrieval

The source manifest includes a remote GLB, deliberately not duplicated in Git.
From the repository root, this standard-library command downloads into an ignored
research folder and rejects changed bytes before writing:

```sh
python3 - <<'PY'
import hashlib
import json
import urllib.request
from pathlib import Path

folder = Path('.research/hra-source-review')
folder.mkdir(parents=True, exist_ok=True)
records = json.loads(Path('docs/licensing/hra-lung/sources.json').read_text())
for record in records:
    data = urllib.request.urlopen(record['url'], timeout=60).read()
    if hashlib.sha256(data).hexdigest() != record['sha256']:
        raise ValueError('Source changed: ' + record['file'])
    (folder / record['file']).write_bytes(data)
print('Verified HRA source files; geometry approval still pending')
PY
```

## Integration gates still open

1. Check source rights/attribution and downstream distribution terms for the host.
2. Extract the correct left/right surfaces; preserve provenance for every component.
3. Register coordinates, orientation and scale against the official BodyParts3D
   skeleton/body. These datasets are different donors and poses: simple centering
   or bounding-box fitting is not proof of anatomical alignment.
4. Review interaction with heart, ribs, airway and body shell; label the resulting
   mixed-source model as illustrative. Obtain visual approval before promotion.
5. Add build/provenance/selection checks and promote all notices/artifacts together.

This is a candidate solution for **two lung selections only**. It does not supply
the four unresolved abdominal/latissimus muscle selections. The owner selected
preserve-coverage migration; no partial reduction of the app is authorized.
