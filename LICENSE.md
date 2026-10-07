# Licensing notice - separate components, separate terms

## Application code

The original application code, tools and documentation are licensed under
[MIT](LICENSE), allowing reuse in private commercial products such as Cureocity.
Include the MIT copyright and permission notice with copies or substantial portions
of that software. This grant does **not** relicense third-party assets or evidence.

The repository remains private until the approved model-migration/public-release
plan is complete; MIT does not itself change repository visibility. This is not
yet a published Flutter package. Keep `publish_to: none` in `pubspec.yaml`.
Do not apply a blanket MIT label to the model assets.

## Bundled anatomy

The mirror-derived BodyParts3D assets in `assets/viewer/anatomy.glb` and
`assets/viewer/anatomy-data.js` retain **Creative Commons Attribution-Share Alike
2.1 Japan (CC BY-SA 2.1 JP)**. Their modifications remain under those terms.
The application's MIT license does not replace or remove the model license.

- Attribution and modifications: [CREDITS.txt](assets/viewer/CREDITS.txt)
- Preserved source license summary: [BODY_PARTS_LICENSE.txt](assets/viewer/BODY_PARTS_LICENSE.txt)
- License deed: https://creativecommons.org/licenses/by-sa/2.1/jp/deed.en
- Controlling legal code: https://creativecommons.org/licenses/by-sa/2.1/jp/legalcode
- Mirror source: https://github.com/Kevin-Mattheus-Moerman/BodyParts3D
- Pinned revision: `f0eeb6e843380cfe6b83797cf8c3e1af74de5e61`
- Mesh identifiers: [anatomy-manifest.json](assets/viewer/anatomy-manifest.json)
- Reproduction script: [prepare_anatomy.py](tools/prepare_anatomy.py)

Attribution is not the only obligation: adaptations of the licensed models are
subject to the applicable share-alike requirements. Do not assume either that
this automatically licenses all independent host code or that it permits every
proprietary combination. Have counsel assess adaptations, collections, distribution,
and any EULA/store/DRM restrictions for the actual product.

The database's official 2025 CC BY 4.0 update is documented separately. It has
**not** been applied to the bundled artifacts. The official candidate is not
approved for use here; its lung geometry differs. See [INTEGRATION.md](INTEGRATION.md).

## Renderer and other dependencies

Three.js is separately MIT licensed; preserve [THREE_LICENSE.txt](assets/viewer/THREE_LICENSE.txt)
when distributing the bundled renderer. Flutter, WebView plugins and other
dependencies retain their own licenses. Review the resolved dependency notices
for each distribution; this file is not an exhaustive dependency-license inventory.

## Before distribution

Follow [the release checklist](docs/RELEASE_CHECKLIST.md) and
[the integration policy](INTEGRATION.md). Keep the production credits control
and notices. These guides are engineering safeguards, not legal advice or a
certification of compliance. Clinical validation is also outside this prototype.
