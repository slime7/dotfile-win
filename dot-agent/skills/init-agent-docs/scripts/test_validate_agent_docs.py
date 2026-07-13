#!/usr/bin/env python3
"""Regression tests for validate_agent_docs.py."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from validate_agent_docs import CORE_DOCUMENTS, validate_project


class ValidateAgentDocsTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.project_root = Path(self.temporary_directory.name)

    def tearDown(self) -> None:
        self.temporary_directory.cleanup()

    def write_document(self, relative_path: str | Path, text: str) -> Path:
        path = self.project_root / relative_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
        return path

    def write_valid_core(self) -> None:
        references = "\n".join(
            f"- [{path.as_posix()}]({path.as_posix()})"
            for path in CORE_DOCUMENTS
            if path.name != "AGENTS.md"
        )
        self.write_document("AGENTS.md", f"# Agent instructions\n\n{references}\n")
        self.write_document("docs/VISION.md", "# Vision\n\nCurrent product direction.\n")
        self.write_document(
            "docs/ARCHITECTURE.md", "# Architecture\n\nCurrent implementation.\n"
        )
        self.write_document(
            "docs/ABSTRACTIONS.md", "# Abstractions\n\nProject concepts.\n"
        )
        self.write_document(
            "docs/GETTING-STARTED.md", "# Getting Started\n\nRun the project.\n"
        )
        self.write_document(
            "docs/adr/README.md",
            "# ADR\n\nUse proposed, active, superseded, and retired statuses.\n",
        )

    def test_accepts_complete_documents_and_bilingual_adr(self) -> None:
        self.write_valid_core()
        self.write_document(
            "docs/adr/0001-storage-boundary.md",
            """# 0001 — Storage boundary

- 状态: active

## 背景

The project needs one source of truth.

## 决策

Use local files.

## 考虑的方案

Local files and a remote database.

## 影响

Callers must handle file errors.
""",
        )

        self.assertEqual(validate_project(self.project_root), [])

    def test_reports_missing_and_empty_core_documents(self) -> None:
        self.write_valid_core()
        (self.project_root / "docs/VISION.md").unlink()
        self.write_document("docs/ARCHITECTURE.md", "\n")

        errors = validate_project(self.project_root)

        self.assertTrue(any("VISION.md" in error and "missing" in error for error in errors))
        self.assertTrue(
            any("ARCHITECTURE.md" in error and "empty" in error for error in errors)
        )

    def test_reports_placeholders_broken_links_and_missing_index_entries(self) -> None:
        self.write_valid_core()
        self.write_document(
            "docs/VISION.md",
            "# Vision\n\n{{PROJECT_NAME}}\n\n[Missing](missing.md)\n",
        )
        self.write_document("AGENTS.md", "# Agent instructions\n")

        errors = validate_project(self.project_root)

        self.assertTrue(any("unresolved placeholder" in error for error in errors))
        self.assertTrue(any("local link target does not exist" in error for error in errors))
        self.assertTrue(any("does not reference docs/VISION.md" in error for error in errors))

    def test_reports_invalid_adr_shape(self) -> None:
        self.write_valid_core()
        self.write_document("docs/adr/decision.md", "# Decision\n\nNo metadata.\n")

        errors = validate_project(self.project_root)

        self.assertTrue(any("ADR filename" in error for error in errors))
        self.assertTrue(any("ADR status" in error for error in errors))
        self.assertTrue(any("missing ADR section" in error for error in errors))

    def test_checks_existing_compatibility_documents(self) -> None:
        self.write_valid_core()
        self.write_document("CLAUDE.md", "# Local instructions\n")

        errors = validate_project(self.project_root)

        self.assertTrue(any("does not reference AGENTS.md" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
