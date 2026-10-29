"""Build a CC BY 4.0-source review candidate, never production assets.

Requires the verified official cache and HRA male lung source documented in
MIGRATION_STATUS.md. Missing regions remain visible release blockers, not legacy
fallbacks. Successful build/check means reproducibility, not approval to ship.
"""

import argparse
import base64
import csv
import html
import io
import json
import shutil
import zipfile
from pathlib import Path

import numpy as np
import trimesh
from check_official_coverage import constants
from prepare_female_candidate import digest, extract, verify, verify_official_evidence
from prepare_official_anatomy import BASE, PARTS, SOURCES
from trimesh.visual.color import ColorVisuals

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / ".research/commercial-migration-candidate"
HRA = ROOT / ".research/hra-source-review/3d-vh-m-lung.glb"
HRA_PREFIX = "https://raw.githubusercontent.com/hubmapconsortium/hra-kg/29888dcc5f32dae28c7a07c41171c822275360c3/digital-objects/ref-organ/lung-male/v1.4/raw/"
HRA_HASHES = {
    "3d-vh-m-lung.glb": "bba95516fa993ac45c3b1c53f32b58d97232ffd78ae56397e5a2589c6ce4903d",
    "crosswalk.csv": "072b3741e7e60c16f8d6f577ff302978211e826d7b9e345eb725afe5bdd9b910",
    "metadata.yaml": "1ba505e21496b1fdfaa12b2289ff197e33b28e52697b4b59e35469fa00d97089",
}
LUNGS = {"lung_left": ["VH_M_lungs_L"], "lung_right": ["VH_M_lungs_R"]}
FILES = (
    "anatomy.glb",
    "anatomy-data.js",
    "anatomy-manifest.json",
    "migration-report.json",
    "CREDITS.txt",
    "BODY_PARTS_LICENSE.txt",
    "HRA_METADATA.yaml",
    "THREE_LICENSE.txt",
    "index.html",
    "viewer.js",
    "preview-controls.js",
)
CODE = (
    "tools/prepare_commercial_candidate.py",
    "tools/prepare_official_anatomy.py",
    "tools/prepare_female_candidate.py",
    "tools/check_official_coverage.py",
    "tools/prepare_anatomy.py",
    "assets/viewer/index.html",
    "assets/viewer/viewer.js",
)


def prepare_output():
    if OUTPUT.resolve() != ROOT / ".research/commercial-migration-candidate":
        raise ValueError("Refusing redirected commercial candidate output")
    OUTPUT.mkdir(parents=True, exist_ok=True)
    for path in OUTPUT.iterdir():
        if path.is_symlink() or (path.is_file() and path.stat().st_nlink > 1):
            raise ValueError(f"Refusing linked candidate output: {path}")
    (OUTPUT / "anatomy-provenance.json").unlink(missing_ok=True)


def inputs():
    cache = ROOT / ".research/bodyparts3d-4.0-official"
    for name, expected in SOURCES.items():
        verify(cache / name, expected)
    evidence = ROOT / "docs/licensing/hra-lung"
    records = json.loads((evidence / "sources.json").read_text())
    expected = [
        {"url": HRA_PREFIX + name, "file": name, "sha256": value}
        for name, value in HRA_HASHES.items()
    ]
    if records != expected:
        raise ValueError("HRA lung source evidence changed; source review required")
    for record in records:
        verify(
            HRA if record["file"].endswith(".glb") else evidence / record["file"],
            record["sha256"],
        )
    return {
        "official_sources": [
            {"url": BASE + name, "sha256": value} for name, value in SOURCES.items()
        ],
        "official_evidence_sha256": verify_official_evidence(),
        "hra_sources": records,
        "hra_evidence_index_sha256": digest(evidence / "sources.json"),
        "code_sha256": {name: digest(ROOT / name) for name in CODE},
    }


def region_plan(inventory, mappings, members):
    plan = {}
    for name, legacy_concepts in inventory.items():
        tree, concepts = PARTS.get(name, ("isa", legacy_concepts))
        missing = [concept for concept in concepts if concept not in mappings[tree]]
        parts = sorted(set().union(*(mappings[tree].get(c, set()) for c in concepts)))
        absent = sorted(set(parts) - members)
        available = bool(parts) and not missing and not absent
        plan[name] = {
            "source": "hra-male-lung" if name in LUNGS else "official-bodyparts3d-4.0",
            "status": "available" if available else "missing-source",
            "tree": tree,
            "concepts": concepts,
            "parts": parts,
            "missing_concepts": missing,
            "missing_elements": absent,
        }
    return plan


def check_mesh(mesh):
    if (
        not len(mesh.faces)
        or not np.isfinite(mesh.vertices).all()
        or not np.isfinite(mesh.area)
        or mesh.area <= 0
        or not np.all(np.ptp(mesh.bounds, axis=0) > 0)
    ):
        raise ValueError("Empty, nonfinite or collapsed candidate mesh")


def check(provenance_file=None):
    provenance = json.loads(
        (provenance_file or OUTPUT / "anatomy-provenance.json").read_text()
    )
    if provenance["inputs"] != inputs():
        raise ValueError("Candidate inputs changed; rebuild/review required")
    assert provenance["status"] == "blocked-review-only"
    assert provenance["promotion_allowed"] is False
    assert provenance["anatomically_validated"] is False
    assert set(provenance["output_sha256"]) == set(FILES)
    for name in FILES:
        verify(OUTPUT / name, provenance["output_sha256"][name])
    inventory = constants(ROOT / "tools/prepare_anatomy.py")["PARTS"]
    report = json.loads((OUTPUT / "migration-report.json").read_text())
    manifest = json.loads((OUTPUT / "anatomy-manifest.json").read_text())
    missing = sorted(
        name
        for name, item in report["regions"].items()
        if item["status"] == "missing-source"
    )
    assert set(report["regions"]) == set(inventory)
    assert report["missing_regions"] == missing
    assert set(manifest) == set(inventory) - set(missing)
    assert report["promotion_allowed"] is False and report["blockers"]
    assert report["legacy_geometry_reused"] is False
    credits = (OUTPUT / "CREDITS.txt").read_text()
    assert "Reproduction script: tools/prepare_commercial_candidate.py." in credits
    assert "Reproduction script: tools/prepare_official_anatomy.py." not in credits
    assert provenance["missing_regions"] == missing
    blob = (OUTPUT / "anatomy.glb").read_bytes()
    embedded = (OUTPUT / "anatomy-data.js").read_text()
    assert embedded.startswith('window.ANATOMY_GLB = "') and embedded.endswith('";\n')
    assert base64.b64decode(embedded.split('"')[1], validate=True) == blob
    scene = trimesh.load_scene(io.BytesIO(blob), file_type="glb", process=False)
    assert set(scene.geometry) == set(manifest)
    for name, mesh in scene.geometry.items():
        check_mesh(mesh)
        region = manifest[name]
        assert (
            region["license"] == "CC BY 4.0"
            and region["anatomically_validated"] is False
        )
        assert region["source"] == report["regions"][name]["source"]
        assert len(mesh.faces) == region["triangles"]
        assert np.allclose(mesh.bounds, region["bounds"], atol=1e-6)
        assert 0.5 <= mesh.area / region["source_area"] <= 1.15
        if name.endswith("_left"):
            assert mesh.bounds[:, 0].mean() > 0, name
        elif name.endswith("_right"):
            assert mesh.bounds[:, 0].mean() < 0, name
    print(
        f"PASS: {len(manifest)}/{len(inventory)} regions, source/evidence hashes, notices and GLB round-trip. BLOCKED for release."
    )


def preview(manifest, report, credits):
    shutil.copyfile(ROOT / "assets/viewer/viewer.js", OUTPUT / "viewer.js")
    page = (ROOT / "assets/viewer/index.html").read_text()
    options = "".join(
        f'<option value="{html.escape(name)}">{html.escape(name)}</option>'
        for name in manifest
        if name != "body_shell"
    )
    panel = f"""<aside style="position:absolute;z-index:2;top:8px;left:8px;right:8px;padding:12px;background:#fff;color:#16343b;font:14px sans-serif;max-height:40vh;overflow:auto;overflow-wrap:anywhere">
<strong>CC BY 4.0-source review candidate - NOT APPROVED FOR RELEASE</strong>
<p>{len(manifest)}/{len(report["regions"])} regions. Missing: {html.escape(", ".join(report["missing_regions"]))}.
Lung alignment is an unreviewed display translation. Not clinically validated.</p>
<label>Mode <select id="mode"><option value="body">Body Parts</option><option value="muscles">Muscles</option><option value="bones">Bones</option></select></label>
<label>Structure <select id="region">{options}</select></label>
<button id="focus">Focus</button><button id="reset">Reset</button><button id="rotate">Rotate</button>
<details><summary>Credits and licenses</summary><pre style="white-space:pre-wrap">{html.escape(credits)}</pre><a href="BODY_PARTS_LICENSE.txt">Model license</a> / <a href="THREE_LICENSE.txt">Three.js license</a></details>
<a href="migration-report.json">Blocking migration report</a></aside>"""
    controls = """const mode = document.querySelector('#mode');
function configure() { if (!window.anatomy?.ready) return false; window.anatomy.configure({mode:mode.value,loading:false,reducedMotion:true}); return true; }
window.AnatomyBridge = {postMessage(data) { if (JSON.parse(data).type === 'ready') configure(); }};
configure();
mode.addEventListener('change', () => { if (configure()) window.anatomy.reset(); });
document.querySelector('#focus').addEventListener('click', () => { const id=document.querySelector('#region').value; mode.value=id.startsWith('muscle_')?'muscles':id.startsWith('bone_')?'bones':'body'; if(configure()) window.anatomy.focus(id); });
document.querySelector('#reset').addEventListener('click', () => { if(configure()) window.anatomy.reset(); });
document.querySelector('#rotate').addEventListener('click', () => { if(configure()) window.anatomy.nudge('left'); });
"""
    (OUTPUT / "preview-controls.js").write_text(controls)
    (OUTPUT / "index.html").write_text(
        page.replace("<body>", "<body>" + panel).replace(
            "</body>", '<script src="preview-controls.js"></script></body>'
        )
    )


def build():
    prepare_output()
    evidence = inputs()
    inventory = constants(ROOT / "tools/prepare_anatomy.py")["PARTS"]
    cache = ROOT / ".research/bodyparts3d-4.0-official"
    mappings = {}
    for tree in ("isa", "partof"):
        mapping = {}
        with (cache / f"{tree}_element_parts.txt").open() as stream:
            rows = csv.reader(stream, delimiter="\t")
            next(rows)
            for concept, _label, element in rows:
                mapping.setdefault(concept, set()).add(element)
        mappings[tree] = mapping
    hra_scene = trimesh.load_scene(HRA, process=False)
    scene, manifest = trimesh.Scene(), {}
    with zipfile.ZipFile(cache / "isa_BP3D_4.0_obj_99.zip") as archive:
        members = {
            Path(name).stem: name
            for name in archive.namelist()
            if name.endswith(".obj")
        }
        plan = region_plan(inventory, mappings, set(members))
        for name, region in plan.items():
            if region["status"] == "missing-source":
                continue
            # Official lung branches provide a display location, not a lung envelope.
            elements = [
                trimesh.load_mesh(
                    io.BytesIO(archive.read(members[part])), file_type="obj"
                )
                for part in region["parts"]
            ]
            if not elements:
                raise ValueError(f"No official registration reference for {name}")
            official = trimesh.util.concatenate(elements)
            assert isinstance(official, trimesh.Trimesh)
            official.vertices = official.vertices[:, [0, 2, 1]] / 1000
            official.vertices[:, 2] *= -1
            mesh = official
            translation = [0.0, 0.0, 0.0]
            if name in LUNGS:
                mesh = extract(hra_scene, LUNGS[name])
                translation = (
                    official.bounds.mean(axis=0) - mesh.bounds.mean(axis=0)
                ).tolist()
                mesh.apply_translation(translation)
            check_mesh(mesh)
            source_area = float(mesh.area)
            mesh.merge_vertices(merge_tex=True, merge_norm=True)
            target = 24000 if name in {"body_shell", "brain", "bone_skull"} else 8000
            if len(mesh.faces) > target:
                mesh = mesh.simplify_quadric_decimation(face_count=target)
            mesh.update_faces(mesh.nondegenerate_faces())
            mesh.remove_unreferenced_vertices()
            mesh.visual = ColorVisuals(mesh=mesh)
            check_mesh(mesh)
            scene.add_geometry(mesh, node_name=name, geom_name=name)
            manifest[name] = {
                **region,
                "license": "CC BY 4.0",
                "anatomically_validated": False,
                "source_nodes": LUNGS.get(name, []),
                "translation": translation,
                "registration": "unreviewed bounds-center translation; no shape scaling"
                if name in LUNGS
                else "official shared coordinates; axis/unit conversion only",
                "source_area": source_area,
                "triangles": len(mesh.faces),
                "bounds": mesh.bounds.tolist(),
            }
            print(name, len(mesh.faces), flush=True)
    missing = sorted(set(inventory) - set(manifest))
    report = {
        "status": "blocked-review-only",
        "promotion_allowed": False,
        "legacy_geometry_reused": False,
        "regions": plan,
        "missing_regions": missing,
        "blockers": (
            ["Missing licensed muscle sources: " + ", ".join(missing)]
            if missing
            else []
        )
        + [
            "HRA/BodyParts3D cross-donor lung registration is not anatomically reviewed; bounds-center translation does not align the lung apices.",
            "All regions, decimation and source/license scope need owner and qualified review.",
            "Host EULA/store/DRM compatibility and publication approval remain open.",
        ],
    }
    blob = scene.export(file_type="glb")
    assert isinstance(blob, bytes)
    (OUTPUT / "anatomy.glb").write_bytes(blob)
    (OUTPUT / "anatomy-data.js").write_text(
        'window.ANATOMY_GLB = "' + base64.b64encode(blob).decode() + '";\n'
    )
    for name, data in (
        ("anatomy-manifest.json", manifest),
        ("migration-report.json", report),
    ):
        (OUTPUT / name).write_text(json.dumps(data, indent=2) + "\n")
    notices = ROOT / "docs/licensing/bodyparts3d"
    credits = (
        "CC BY 4.0-SOURCE REVIEW CANDIDATE - NOT APPROVED FOR RELEASE\n"
        "No legacy geometry reused. Missing selections remain release blockers.\n"
        "Illustrative only; not clinically validated. No endorsement implied.\n\n"
        + (notices / "CANDIDATE_CREDITS.txt")
        .read_text()
        .replace(
            "Reproduction script: tools/prepare_official_anatomy.py.",
            "Reproduction script: tools/prepare_commercial_candidate.py.",
        )
        + "\nLUNG REPLACEMENTS\n"
        "Browne, Kristen, and Heidi Schlehlein. 2024. 3D Reference Organ for Lung, Male v1.4.\n"
        "HuBMAP Human Reference Atlas. https://doi.org/10.48539/HBM532.KLZD.394\n"
        "CC BY 4.0: https://creativecommons.org/licenses/by/4.0/\n"
        "Courtesy of the U.S. National Library of Medicine. Bibliography: HRA_METADATA.yaml.\n"
        "Modifications: extracted lung descendants with source world transforms, welded seams,\n"
        "simplified, applied unreviewed bounds-center display translation and exported GLB/base64.\n"
        "Translation is not verified anatomical registration; no source shape scaling.\n"
        "Per-region source/parts/nodes: anatomy-manifest.json. Gaps: migration-report.json.\n"
        "Three.js MIT notice: THREE_LICENSE.txt. Attribution remains mandatory.\n"
    )
    (OUTPUT / "CREDITS.txt").write_text(credits)
    shutil.copyfile(
        notices / "CANDIDATE_LICENSE.txt", OUTPUT / "BODY_PARTS_LICENSE.txt"
    )
    shutil.copyfile(
        ROOT / "docs/licensing/hra-lung/metadata.yaml", OUTPUT / "HRA_METADATA.yaml"
    )
    shutil.copyfile(
        ROOT / "assets/viewer/THREE_LICENSE.txt", OUTPUT / "THREE_LICENSE.txt"
    )
    preview(manifest, report, credits)
    provenance = {
        "status": "blocked-review-only",
        "promotion_allowed": False,
        "anatomically_validated": False,
        "inputs": evidence,
        "missing_regions": missing,
        "output_sha256": {name: digest(OUTPUT / name) for name in FILES},
    }
    pending = OUTPUT / "anatomy-provenance.pending.json"
    try:
        pending.write_text(json.dumps(provenance, indent=2) + "\n")
        check(pending)
        pending.replace(OUTPUT / "anatomy-provenance.json")
    finally:
        pending.unlink(missing_ok=True)
    print(f"Review only: {OUTPUT}. App unchanged; {len(missing)} missing regions.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check",
        action="store_true",
        help="Verify review artifacts; NOT release approval",
    )
    args = parser.parse_args()
    try:
        check() if args.check else build()
    except (OSError, ValueError, AssertionError) as error:
        parser.exit(1, f"Candidate verification failed: {error}\n")
