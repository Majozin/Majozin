"""Offline contract regression tests for project-owned status in private repositories."""
import base64
import json
from pathlib import Path
import sys
import unittest
from unittest.mock import patch
from urllib.error import HTTPError

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import update_private_projects as project


def example(percent=0, estimated=False):
    return {
        "schema_version": "project-status/v1",
        "repository": "Majozin/mod-control-center",
        "progress": {
            "percent": percent,
            "estimated": estimated,
            "basis": "homologated_deliverables",
        },
        "profile": {
            "visible": True,
            "public_name": "Mod Control Center",
            "public_status": "Aguardando testes reais",
        },
        "sensitive_private_value": "NEVER-PUBLISH",
    }


def encoded(data):
    return {
        "type": "file",
        "encoding": "base64",
        "content": base64.b64encode(json.dumps(data).encode("utf-8")).decode("ascii"),
    }


class ProjectStatusTests(unittest.TestCase):
    def test_renamed_project_status_is_source_of_truth(self):
        with patch.object(project, "request", return_value=encoded(example())) as fetch:
            s = project.project_status("mod-control-center")
        self.assertEqual(s, {
            "name": "Mod Control Center",
            "percent": 0,
            "status": "Aguardando testes reais",
            "visible": True,
        })
        self.assertNotIn("sensitive_private_value", str(s))
        self.assertIn("/repos/Majozin/mod-control-center/contents/PROJECT_STATUS.json",
                      fetch.call_args.args[0])

    def test_positive_without_estimate_is_rejected(self):
        with patch.object(project, "request", return_value=encoded(example(69, False))):
            with self.assertRaisesRegex(RuntimeError, "Progresso"):
                project.project_status("mod-control-center")

    def test_positive_audited_status_with_estimate_valid(self):
        with patch.object(project, "request", return_value=encoded(example(42, True))):
            s = project.project_status("mod-control-center")
            self.assertEqual(s["percent"], 42)

    def test_wrong_repo_identity_rejected_after_rename(self):
        data = example()
        data["repository"] = "Majozin/valheim-mod-control-center"
        with patch.object(project, "request", return_value=encoded(data)):
            with self.assertRaisesRegex(RuntimeError, "Schema/identidade"):
                project.project_status("mod-control-center")

    def test_404_only_is_legacy_fallback(self):
        exc = HTTPError("https://api.github.com", 404, "Not Found", {}, None)
        with patch.object(project, "request", side_effect=exc):
            self.assertIsNone(project.project_status("legacy-project"))

    def test_permission_error_aborts_without_erasing_cards(self):
        exc = HTTPError("https://api.github.com", 403, "Forbidden", {}, None)
        with patch.object(project, "request", side_effect=exc):
            with self.assertRaisesRegex(RuntimeError, "Falha ao ler"):
                project.project_status("mod-control-center")

    def test_invalid_binary_payload_and_private_field_protection(self):
        with patch.object(project, "request", return_value={
            "type":"file", "encoding":"base64", "content":"not valid data"
        }):
            with self.assertRaises(RuntimeError):
                project.project_status("mod-control-center")

    def test_boolean_progress_rejected(self):
        with patch.object(project, "request", return_value=encoded(example(True, True))):
            with self.assertRaisesRegex(RuntimeError, "Progresso"):
                project.project_status("mod-control-center")

    def test_public_label_validation(self):
        data = example()
        data["profile"]["public_status"] = "status\ninjection"
        with patch.object(project, "request", return_value=encoded(data)):
            with self.assertRaisesRegex(RuntimeError, "Metadados"):
                project.project_status("mod-control-center")


if __name__ == "__main__":
    unittest.main()
