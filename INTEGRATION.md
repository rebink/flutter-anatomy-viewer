# Commercial Integration and Attribution

Start with [installation and usage](docs/SETUP.md),
[theme/performance guidance](docs/THEMING.md), and
[the release checklist](docs/RELEASE_CHECKLIST.md).
This repository contains a Flutter demo, not an installable pub.dev package.

Original application code is [MIT licensed](LICENSE), including for private
commercial use. Preserve the MIT notice. [Model rights remain separate](LICENSE.md).
The owner has approved publishing this repository with its current CC BY-SA 2.1
Japan models. Replacement candidates remain unapproved.

## Current status - not yet migrated

The app still bundles its original mirror-derived anatomy with CC BY-SA 2.1
Japan notices. A fresh official Release 4.0 candidate was built but NOT accepted:
its lung mappings render branching bronchial/vessel structures rather than the
previous solid lung surfaces. The original assets and notices were restored.
Do not describe the current package as CC BY 4.0 or attribution-free.

The official DBCLS / LSDB Archive license page specifies **CC BY 4.0**, dated
**27 February 2025**. The history confirms the license update. Commercial use,
redistribution and adaptation are permitted subject to those terms, without
share-alike; attribution remains required. This is favorable for a commercial
package once the asset migration is accepted. It does not require opening host
application code solely because it includes the CC BY 4.0 assets.

- License: https://dbarchive.biosciencedbc.jp/en/bodyparts3d/lic.html
- History: https://dbarchive.biosciencedbc.jp/en/bodyparts3d/update.html
- Download: https://dbarchive.biosciencedbc.jp/en/bodyparts3d/download.html
- Legal code: https://creativecommons.org/licenses/by/4.0/legalcode.en
- Preserved pages and hashes: `docs/licensing/bodyparts3d/`

The downloaded archive's OBJ comments still contain the old CC BY-SA wording.
The current official database license page and dated README explicitly specify
CC BY 4.0; both are preserved as evidence of the updated grant. Record this
metadata discrepancy; obtain DBCLS/legal confirmation if your release review
requires it. Never pretend the archive headers were updated too.

## Quality-first model acceptance

CC BY-SA 2.1 Japan permits commercial use subject to its conditions. Retaining
the current models is therefore a possible licensing route; migration to
CC BY 4.0 is not a prerequisite solely because an app is paid. Prefer correct,
reviewed geometry over a less restrictive license with missing or mismatched
structures. Replacement geometry still requires source/anatomy approval; public
source release does not approve candidates or enable pub.dev publication.

The current models are a starting point, not a complete or perfect atlas:

| Bundled layer | Current coverage | Important limit |
| --- | --- | --- |
| Body surface | One shell | Not a matched male/female model pair |
| Organs | 15 selectable regions | Selected organs and combined structures; the heart is heart wall |
| Muscles | 28 selections, 14 bilateral pairs | Major-muscle illustration, not every muscle or muscle head |
| Skeleton | 33 selectable bones/groups | Skull, spine, ribs, hands and feet include grouped constituent bones |

The separate female preview is not an approved full female atlas. Its 85 regions
combine HRA references with 48 male-derived adaptations, and its cross-source
registration is not anatomically reviewed. Do not promote it as a complete female
replacement or cosmetically reshape male meshes and claim female-source anatomy.
List-only systems in the medical-parameter browser do not add 3D coverage.

Before calling any replacement complete for a product, record and pass:

1. **Agreed scope:** name every required structure, laterality, sex-specific
   representation and selectable grouping. Completing the current 77 regions is
   different from supplying a full atlas with individual bones and muscles.
   Record missing structures explicitly; never substitute a nearby mesh.
2. **Anatomical review:** a qualified reviewer checks labels, laterality,
   proportions, organ placement, joint fit and muscle attachments against the
   source. Check front, back, both sides and focused views. A matched source
   frame is preferable to an unreviewed warp across different donors/poses.
3. **Fidelity:** compare the original and reduced meshes at intended zoom levels;
   retain important boundaries and landmarks before optimizing. The
   [legacy builder](tools/prepare_anatomy.py) targets 8,000 triangles per selection,
   even for a whole hand or rib group; shell, brain and skull target 24,000. It
   may reuse already reduced meshes when source IDs match, so simply increasing
   the budget does not restore detail. Rebuild demonstrated problem regions from
   verified source geometry, not the previously reduced output. Higher polygon
   counts alone do not establish anatomical correctness. Rendering tests, finite
   bounds and matching hashes are engineering checks, not anatomical validation.
4. **Integration:** verify all agreed structures render, highlight and select
   without cross-mode picking or silently missing IDs. Check accessible lists,
   small screens, loading/failure behavior and actual Android/iOS device budgets.
5. **Coordinated approval:** review source/license evidence, then promote GLB,
   embedded data, manifest, provenance and notices together. Preserve the
   illustrative/not-clinically-validated disclosure unless a separate validation
   process supports a stronger claim.

Neither the legacy set nor a candidate currently has this full approval. This
checklist defines acceptance; it is not a statement that model completion has
already happened.

## Mandatory info button

Our package policy is to retain an accessible information/credits button in
production, opening the bundled `assets/viewer/CREDITS.txt`. Keep it visible,
clearly labeled and available even if the 3D viewer fails to load. The dialog
must remain readable and scrollable at large text sizes. Do not add a public
option to disable attribution in the eventual package.

An info button is generally a reasonable attribution mechanism when it reveals
the creator/database name, license and source URLs, and modification notice.
CC BY 4.0 allows a reasonable attribution manner based on context; it does not
mandate a persistent banner on the 3D view. This is engineering guidance, not a
guarantee of legal compliance in every app/distribution channel.

Retain license files with redistributed models/packages as well. Attribution is
not the entire license: current CC BY-SA assets also retain share-alike terms;
CC BY 4.0 assets still require preserving applicable notices and avoiding
conflicting legal/technological restrictions. Review host EULA/store/DRM terms.
Three.js has a separate MIT notice. Original application code is MIT licensed;
that grant does not cover third-party geometry.

If your app refuses attribution anywhere, do not integrate these bundled models.
Obtain separate permission or replace them with appropriate original/CC0 assets.

## Host app license procedure for the current models

Follow these steps in the actual commercial host, not just this demo:

1. **Identify the assets correctly.** The currently bundled geometry and its
   embedded copy remain CC BY-SA 2.1 Japan, including the prototype's earlier
   reductions and combinations. Reusing these files unchanged does not erase
   their existing modifications or license. Keep the pinned source revision and
   record the hashes of the artifacts that the host actually ships.
2. **Keep the production credits entry point.** Preserve the accessible
   information button described above, including after model-load failure and
   at enlarged text sizes. Load the full bundled `CREDITS.txt`; a short creator
   line or a link to the host's website is not a replacement for that notice.
   It already supplies creator/database, source/license URLs and modifications.
3. **Distribute the notices.** Keep `CREDITS.txt`, `BODY_PARTS_LICENSE.txt`,
   `THREE_LICENSE.txt` and `anatomy-manifest.json` with the shipped viewer assets.
   Include the root `LICENSE` text in the host's third-party notices when reusing
   this application's MIT code. Preserve other dependency notices separately.
   The current app embeds `anatomy-data.js`; there is no need to ship a duplicate
   raw GLB just to retain its notice. Verify the built package, not only source.
4. **Describe host changes accurately.** Retain all existing modification
   notices. If accurate for the host, append: "Runtime materials used for
   interactive color highlighting; tap interaction added. Underlying bundled
   mesh geometry unchanged by this host app." Update the description if meshes
   are subsequently edited. Do not label the model unmodified from upstream.
5. **Preserve model-license rights.** Keep the covered model adaptations under
   the applicable share-alike terms and do not claim exclusive ownership of
   them. Separate host code does not automatically become share-alike merely
   because it includes separately licensed art, but the collection/adaptation
   distinction needs review for the actual integration. An info button alone
   does not settle this question.
6. **Review contracts and technical restrictions.** Have counsel check the host
   EULA, app-store terms and DRM against the exact
   [CC BY-SA 2.1 JP legal code](https://creativecommons.org/licenses/by-sa/2.1/jp/legalcode).
   Blanket "all assets are proprietary" or "no copying any content" terms must
   not override recipients' licensed model rights. Adding a notice does not
   automatically cure conflicting DRM or store conditions.
7. **Keep a release record.** Use the handoff record in
   [the release checklist](docs/RELEASE_CHECKLIST.md). Record the real host
   credits screen, tested failed-load behavior, artifact hashes, dependency
   notices and distribution review. Include this guide and `AGENTS.md` with the
   eventual SDK and add the pointer below to the host's existing agent rules.

Suggested starting text for counsel to adapt in the host's third-party/EULA
notices (not an approved legal clause):

> The third-party BodyParts3D anatomy assets are licensed under Creative Commons
> Attribution-ShareAlike 2.1 Japan. See "Credits and licenses" for attribution,
> source, modification and license details. Restrictions in these application
> terms do not limit rights granted under the applicable third-party licenses.

If CC BY 4.0 assets are later approved and included, credit their actual sources
and authors, retain their license notices and indicate changes. Do not relabel
remaining legacy meshes or a mixed-source GLB as entirely CC BY 4.0. CC BY 4.0
removes share-alike for its covered material; it does not remove attribution or
permit conflicting restrictions. Use the source-specific metadata and notices.

These are engineering integration instructions, not legal certification. No
model promotion or package-publication approval is implied by following them.

## After official-source migration is approved

Promote the new geometry, credits, license notice, manifest and provenance as one
change. Bundle anatomy-provenance.json and run the provenance/browser checks.
Show this credit together with source/license URLs and modification details:

> BodyParts3D, © The Database Center for Life Science licensed under CC Attribution 4.0 International.
>
> Source: https://dbarchive.biosciencedbc.jp/en/bodyparts3d/download.html
>
> License: https://creativecommons.org/licenses/by/4.0/
>
> Modified: combined official OBJ elements, reduced polygons, converted
> coordinates/units, exported GLB/base64, and applied illustrative materials.
> Not clinically validated; no endorsement by DBCLS is implied.

Prefer loading the actual bundled notice instead of duplicating it in host code.
Append further model modifications if the host changes the geometry.

## Agent handoff

Read `AGENTS.md` before embedding or modifying this viewer. Explain attribution
obligations to the developer and verify that the mandatory button works in the
host app. Installing a dependency does not automatically notify agents. Include
these guides in the eventual package; add a pointer to the host's existing
AGENTS.md or equivalent instructions (substitute the actual package location):

```text
Anatomy integration: read <package-path>/INTEGRATION.md and <package-path>/AGENTS.md.
Preserve the mandatory info button and bundled attribution/license notices.
Check the actual bundled asset license: official-source migration is pending.
Do not describe models as attribution-free or remove credits for commercial use.
Host attribution entry point: <actual screen/control, verified before release>.
```

Do not overwrite other host rules. This is an explicit handoff, not an automatic
notification or enforcement hook. The public repository remains a demo;
package-relative assets and reusable API extraction are separate work.
