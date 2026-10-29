"""Small checks for the isolated, fail-closed commercial migration builder."""

import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import numpy as np
import prepare_commercial_candidate as candidate
import trimesh


class CommercialCandidateTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()
        self.output = self.root / ".research/commercial-migration-candidate"
        for name, value in (("ROOT", self.root), ("OUTPUT", self.output)):
            patch = mock.patch.object(candidate, name, value)
            patch.start()
            self.addCleanup(patch.stop)

    def test_complete_inventory_keeps_exact_four_missing_muscles(self):
        inventory = candidate.constants(
            Path(candidate.__file__).resolve().parent / "prepare_anatomy.py"
        )["PARTS"]
        missing = {
            "muscle_abs_left",
            "muscle_abs_right",
            "muscle_latissimus_left",
            "muscle_latissimus_right",
        }
        missing_concepts = set().union(*(inventory[name] for name in missing))
        mappings = {"isa": {}, "partof": {}}
        for name, concepts in inventory.items():
            tree, concepts = candidate.PARTS.get(name, ("isa", concepts))
            for concept in concepts:
                if concept not in missing_concepts:
                    mappings[tree][concept] = {"element"}
        plan = candidate.region_plan(inventory, mappings, {"element"})
        self.assertEqual(set(plan), set(inventory))
        self.assertEqual(
            {
                name
                for name, entry in plan.items()
                if entry["status"] == "missing-source"
            },
            missing,
        )
        self.assertEqual(plan["lung_left"]["source"], "hra-male-lung")
        self.assertEqual(plan["brain"]["source"], "official-bodyparts3d-4.0")

    def test_neighboring_muscle_does_not_replace_missing_concept(self):
        plan = candidate.region_plan(
            {"muscle_abs_left": ["FMA13378"]},
            {"isa": {"FMA9628": {"parent"}}, "partof": {}},
            {"parent"},
        )
        self.assertEqual(plan["muscle_abs_left"]["status"], "missing-source")
        self.assertEqual(plan["muscle_abs_left"]["missing_concepts"], ["FMA13378"])

    def test_partial_mapping_and_missing_archive_member_are_blocked(self):
        mappings = {"isa": {"one": {"element"}, "two": {"absent"}}, "partof": {}}
        plan = candidate.region_plan(
            {"partial": ["one", "missing"], "absent": ["two"]}, mappings, {"element"}
        )
        self.assertEqual(plan["partial"]["status"], "missing-source")
        self.assertEqual(plan["absent"]["missing_elements"], ["absent"])
        self.assertEqual(plan["absent"]["status"], "missing-source")

    def test_duplicate_elements_are_combined_once(self):
        plan = candidate.region_plan(
            {"example": ["one", "two"]},
            {"isa": {"one": {"element"}, "two": {"element"}}, "partof": {}},
            {"element"},
        )
        self.assertEqual(plan["example"]["parts"], ["element"])
        self.assertEqual(plan["example"]["status"], "available")

    def test_lungs_require_an_official_registration_reference(self):
        plan = candidate.region_plan(
            {"lung_left": ["missing"]}, {"isa": {}, "partof": {}}, set()
        )
        self.assertEqual(plan["lung_left"]["status"], "missing-source")

    def test_output_rejects_a_redirected_directory(self):
        protected = self.root / "assets/viewer"
        protected.mkdir(parents=True)
        self.output.parent.mkdir()
        self.output.symlink_to(protected, target_is_directory=True)
        with self.assertRaisesRegex(ValueError, "redirected"):
            candidate.prepare_output()

    def test_output_rejects_hardlinked_files(self):
        protected = self.root / "original.glb"
        protected.write_bytes(b"unchanged")
        self.output.mkdir(parents=True)
        os.link(protected, self.output / "anatomy.glb")
        with self.assertRaisesRegex(ValueError, "linked"):
            candidate.prepare_output()
        self.assertEqual(protected.read_bytes(), b"unchanged")

    def test_failed_build_removes_old_success_marker(self):
        self.output.mkdir(parents=True)
        marker = self.output / "anatomy-provenance.json"
        marker.write_text("old-success")
        with (
            mock.patch.object(
                candidate, "inputs", side_effect=ValueError("changed source")
            ),
            self.assertRaisesRegex(ValueError, "changed source"),
        ):
            candidate.build()
        self.assertFalse(marker.exists())

    def test_changed_source_hash_is_rejected(self):
        cache = self.root / ".research/bodyparts3d-4.0-official"
        cache.mkdir(parents=True)
        (cache / "source.zip").write_bytes(b"changed")
        with (
            mock.patch.object(candidate, "SOURCES", {"source.zip": "0" * 64}),
            self.assertRaises(ValueError),
        ):
            candidate.inputs()

    def test_changed_hra_license_evidence_is_not_reaccepted(self):
        evidence = self.root / "docs/licensing/hra-lung"
        evidence.mkdir(parents=True)
        records = [
            {"url": candidate.HRA_PREFIX + name, "file": name, "sha256": value}
            for name, value in candidate.HRA_HASHES.items()
        ]
        records[-1]["sha256"] = "0" * 64
        (evidence / "sources.json").write_text(json.dumps(records))
        with (
            mock.patch.object(candidate, "SOURCES", {}),
            self.assertRaisesRegex(ValueError, "evidence changed"),
        ):
            candidate.inputs()

    def test_mesh_check_rejects_empty_nonfinite_and_flat_geometry(self):
        candidate.check_mesh(trimesh.creation.box())
        empty = trimesh.Trimesh()
        flat = trimesh.Trimesh(
            vertices=[[0, 0, 0], [1, 0, 0], [0, 1, 0]], faces=[[0, 1, 2]], process=False
        )
        nonfinite = trimesh.creation.box()
        nonfinite.vertices[0, 0] = np.nan
        for mesh in (empty, flat, nonfinite):
            with (
                self.subTest(mesh=mesh),
                self.assertRaisesRegex(ValueError, "candidate mesh"),
            ):
                candidate.check_mesh(mesh)


if __name__ == "__main__":
    unittest.main()
