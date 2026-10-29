# Anatomy Package Agent Rules

Read `INTEGRATION.md` before embedding, extracting or publishing this viewer.

## Current migration status

The bundled app still uses the original mirror-derived models and their
CC BY-SA 2.1 Japan notices. Do NOT label those artifacts as CC BY 4.0 or MIT.
The official DBCLS license update to CC BY 4.0 on 27 February 2025 is verified,
but the official Release 4.0 candidate has a lung-geometry mismatch and has NOT
been promoted into the app. See `docs/licensing/bodyparts3d/` for evidence.
Original application code is MIT licensed; see LICENSE and LICENSE.md for scope.
Models are not MIT. The owner approved public source release with the current
CC BY-SA 2.1 Japan assets. This supersedes the earlier migration-first repository
visibility hold; it does not approve replacement candidates or registry
publication. Keep `publish_to: none`.

## Mandatory attribution UX

- Keep the information/credits button available in production. In the eventual
  package it is a required control, not a demo-only element or optional flag.
- It must have an accessible label and open readable, scrollable attribution,
  source/license URLs and modification notices from the bundled CREDITS.txt.
- Do not hide it for commercial, white-label or closed-source integrations.
  Do not make the legal information depend on successful model loading.
- Tell integrating developers that attribution is required. If the developer
  refuses attribution everywhere, stop integration of these assets and request
  alternative geometry or separate written permission. No banner over the
  model is necessary, but silent asset files alone are not our accepted UX.
- Preserve CREDITS.txt, BODY_PARTS_LICENSE.txt and THREE_LICENSE.txt in package
  and app distributions. Three.js MIT notices are separate from model licensing.
- Never claim that an info button alone meets every license obligation. Current
  CC BY-SA assets also have share-alike terms. Official CC BY 4.0 removes that
  obligation but still requires attribution and prohibits conflicting additional
  restrictions. Escalate EULA/store/DRM conflicts for legal review.

## Asset changes

- `tools/prepare_anatomy.py` rebuilds the current legacy assets. Do not change
  their license merely because the database's current license has changed.
- `tools/prepare_official_anatomy.py` builds a separate checksum-verified official
  candidate under `.research/bodyparts3d-4.0-candidate/`; no old meshes are reused.
- Do not promote that candidate until the lung representation is reviewed and
  explicitly approved or corrected. Interaction tests do not verify anatomy.
- A future promotion must replace GLB, embedded JS, manifest, notices and
  provenance together, update bundled assets and documentation, and retain
  official evidence. Hash changes require source/license review, not repinning.
- Run `python3 tools/check_asset_licenses.py` for the candidate's provenance and
  `npm run test:viewer` for the bundled app. Inspect rendered screenshots too.
- Geometry is illustrative, not clinically validated. Preserve that disclosure.

## Downstream agents

Dependency installation does not automatically notify agents or make them read
this file. Include this file and INTEGRATION.md in the eventual package and link
them from its README. When integrating, add a pointer in the host's own AGENTS.md
(or equivalent instructions), without overwriting existing rules. Record where
the mandatory attribution control is exposed. Do not claim automatic enforcement.
