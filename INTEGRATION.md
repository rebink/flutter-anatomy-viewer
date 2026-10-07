# Commercial Integration and Attribution

Start with [installation and usage](docs/SETUP.md),
[theme/performance guidance](docs/THEMING.md), and
[the release checklist](docs/RELEASE_CHECKLIST.md).
The repository is a private app prototype, not an installable package.
Original application code is [MIT licensed](LICENSE), including for private
commercial use. Preserve the MIT notice. [Model rights remain separate](LICENSE.md).
The repository stays private until the official-model migration is approved.

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
notification or enforcement hook. The project remains a private prototype;
package-relative assets and reusable API extraction are separate work.
