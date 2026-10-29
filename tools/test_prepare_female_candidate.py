"""Small offline checks for the candidate pipeline; no anatomical claims."""

import io
import shutil
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import numpy as np
import prepare_female_candidate as candidate
import trimesh


class CandidateTests(unittest.TestCase):
    def test_existing_selection_inventory_is_preserved(self):
        parts = candidate.selection_parts()
        self.assertEqual(len(set(parts) | set(candidate.HRA_NODES)), 85)
        self.assertEqual(len(candidate.HRA_NODES), 37)
        self.assertEqual(len(candidate.LEGACY_REGIONS), 4)
        self.assertFalse(candidate.LEGACY_REGIONS & set(candidate.HRA_NODES))
        self.assertEqual(
            len(set(parts) - set(candidate.HRA_NODES) - candidate.LEGACY_REGIONS), 44
        )

    def test_extraction_preserves_transform_and_deduplicates_descendants(self):
        scene = trimesh.Scene()
        matrix = np.eye(4)
        matrix[:3, 3] = [1, 2, 3]
        scene.graph.update(frame_to="group", frame_from="world", matrix=matrix)
        original = trimesh.creation.box()
        scene.add_geometry(original, node_name="child", parent_node_name="group")
        extracted = candidate.extract(scene, ["group", "child"])
        np.testing.assert_allclose(extracted.bounds, original.bounds + [1, 2, 3])
        self.assertEqual(len(extracted.faces), len(original.faces))
        np.testing.assert_allclose(original.centroid, [0, 0, 0], atol=1e-8)
        with self.assertRaisesRegex(ValueError, "Missing source node"):
            candidate.extract(scene, ["absent"])

    def test_adaptation_is_finite_and_laterality_preserving(self):
        for name in ["muscle_deltoid", "muscle_gluteus", "muscle_biceps_femoris"]:
            left = trimesh.creation.box(extents=[0.05, 0.1, 0.05])
            left.apply_translation([0.2, 0.8, 0.12])
            right = left.copy()
            right.vertices[:, 0] *= -1
            a = candidate.adapt(left, name + "_left")
            b = candidate.adapt(right, name + "_right")
            self.assertTrue(np.isfinite(a.vertices).all())
            np.testing.assert_allclose(a.vertices[:, 0], -b.vertices[:, 0])
            np.testing.assert_allclose(a.vertices[:, 1:], b.vertices[:, 1:])
            self.assertGreater(a.centroid[0], 0)

    def test_changed_cache_fails_without_redownload(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "model.glb"
            path.write_bytes(b"changed")
            with patch.object(candidate.urllib.request, "urlopen") as request:
                with self.assertRaisesRegex(ValueError, "Source changed"):
                    candidate.fetch(candidate.HRA_URL, path, "0" * 64)
                request.assert_not_called()
            self.assertEqual(path.read_bytes(), b"changed")

    def test_bad_download_never_becomes_a_cached_source(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "model.glb"
            with (
                patch.object(
                    candidate.urllib.request,
                    "urlopen",
                    return_value=io.BytesIO(b"wrong model"),
                ),
                self.assertRaisesRegex(ValueError, "Source changed"),
            ):
                candidate.fetch(candidate.HRA_URL, path, "0" * 64)
            self.assertFalse(path.exists())
            self.assertFalse(path.with_suffix(".glb.download").exists())

    def test_output_cannot_replace_current_or_previous_assets(self):
        self.assertEqual(
            candidate.OUTPUT, candidate.ROOT / ".research/female-open-candidate"
        )
        self.assertNotEqual(candidate.OUTPUT, candidate.LEGACY)
        self.assertNotEqual(
            candidate.OUTPUT, candidate.ROOT / ".research/female-generated-candidate"
        )

    def test_non_official_download_url_is_rejected(self):
        with (
            tempfile.TemporaryDirectory() as directory,
            self.assertRaisesRegex(ValueError, "Only pinned official HTTPS"),
        ):
            candidate.fetch("file:///etc/passwd", Path(directory) / "model", "0" * 64)

    def test_official_license_evidence_cannot_be_missing_or_changed(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            evidence = root / "docs/licensing/bodyparts3d"
            shutil.copytree(candidate.ROOT / "docs/licensing/bodyparts3d", evidence)
            with patch.object(candidate, "ROOT", root):
                self.assertEqual(len(candidate.verify_official_evidence()), 6)
                license_file = evidence / "license.html"
                license_file.write_text("changed license")
                with self.assertRaisesRegex(ValueError, "Source changed"):
                    candidate.verify_official_evidence()
                license_file.unlink()
                with self.assertRaises(FileNotFoundError):
                    candidate.verify_official_evidence()

    def test_symlinks_and_hardlinks_cannot_overwrite_bundled_assets(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            protected = root / "assets/viewer/anatomy.glb"
            protected.parent.mkdir(parents=True)
            protected.write_bytes(b"protected model")
            output = root / ".research/female-open-candidate"
            output.parent.mkdir()
            with (
                patch.object(candidate, "ROOT", root),
                patch.object(candidate, "OUTPUT", output),
            ):
                output.symlink_to(protected.parent, target_is_directory=True)
                with self.assertRaisesRegex(ValueError, "redirected"):
                    candidate.prepare_output_directory()
                output.unlink()
                output.mkdir()
                linked = output / "anatomy.glb"
                linked.symlink_to(protected)
                with self.assertRaisesRegex(ValueError, "linked candidate"):
                    candidate.prepare_output_directory()
                linked.unlink()
                linked.hardlink_to(protected)
                with self.assertRaisesRegex(ValueError, "linked candidate"):
                    candidate.prepare_output_directory()
                self.assertEqual(protected.read_bytes(), b"protected model")

    def test_failed_validation_cannot_leave_previewable_provenance(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            output = root / ".research/female-open-candidate"
            output.mkdir(parents=True)
            final = output / "anatomy-provenance.json"
            final.write_text("previous successful build")
            with (
                patch.object(candidate, "ROOT", root),
                patch.object(candidate, "OUTPUT", output),
            ):
                candidate.prepare_output_directory()
                self.assertFalse(final.exists())
                with (
                    patch.object(
                        candidate, "check", side_effect=ValueError("invalid geometry")
                    ),
                    self.assertRaisesRegex(ValueError, "invalid geometry"),
                ):
                    candidate.write_validated_provenance({"rejected": True})
                self.assertFalse(final.exists())
                self.assertFalse((output / "anatomy-provenance.pending.json").exists())
                with patch.object(candidate, "check") as check:
                    candidate.write_validated_provenance({"passed": True})
                    check.assert_called_once()
                self.assertIn('"passed": true', final.read_text())


if __name__ == "__main__":
    unittest.main()
