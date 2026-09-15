import argparse
import contextlib
import io
import json
import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import closeout


class CloseoutTests(unittest.TestCase):
    def setUp(self):
        self.scratch = tempfile.TemporaryDirectory()
        self.addCleanup(self.scratch.cleanup)
        self.root = Path(self.scratch.name)
        self.session_id = "test-root-123"
        self.source = self.root / "rollout.jsonl"
        self.run_dir = self.root / "experiments" / "99_Test" / "Test"
        self.run_dir.mkdir(parents=True)
        self.archive = self.run_dir / "experiment_99_test_conversation.jsonl"
        self.archive.write_bytes(b"previous archive\n")
        for name in ("agent", "brief", "concept", "requirements", "sources", "design_notes", "version_notes"):
            (self.run_dir / (name + ".md")).write_text("present", encoding="utf-8")
        self.rationale = self.run_dir / "experiment_99_test_design_rationale.md"
        self.rationale.write_text("\n".join("## " + s + ". Test" for s in closeout.RATIONALE_SECTIONS), encoding="utf-8")
        input_dir = self.run_dir.parent / "input"
        input_dir.mkdir()
        (input_dir / "experiment_99_prompts_test.txt").write_text("brief", encoding="utf-8")

    def write_codex(self, session_id=None, source="cli"):
        self.source.write_text(json.dumps({"type": "session_meta", "payload": {
            "id": session_id or self.session_id, "source": source}}) + "\n" +
            json.dumps({"type": "event_msg", "payload": {"type": "task_complete"}}) + "\n", encoding="utf-8")

    def execute(self, failed_tool=None, no_archive=False, explicit=True):
        args = argparse.Namespace(exp="99", agent="Test", session_id=None if no_archive else self.session_id,
                                  transcript_source=str(self.source) if explicit and not no_archive else None,
                                  no_archive=no_archive)

        def run_tool(cmd, **kwargs):
            return (1, "test failure") if failed_tool and failed_tool in cmd[1] else (0, "ok")

        with patch.object(closeout, "REPO", str(self.root)), patch.object(closeout, "run", side_effect=run_tool), \
                patch.object(closeout, "SESSIONS_DIR", str(self.root / "sessions")), \
                contextlib.redirect_stdout(io.StringIO()):
            return closeout.closeout_run(args)

    def test_explicit_codex_source_is_archived_exactly(self):
        self.write_codex()
        self.assertTrue(self.execute())
        self.assertEqual(self.archive.read_bytes(), self.source.read_bytes())
        self.assertIn("13 passed, 0 failed", (self.run_dir / "closeout_run.md").read_text())

    def test_failed_check_preserves_previous_archive(self):
        self.write_codex()
        for failure in ("callouts.py", "api_card.py", "export_all_models.py"):
            with self.subTest(failure=failure):
                self.assertFalse(self.execute(failed_tool=failure))
                self.assertEqual(self.archive.read_bytes(), b"previous archive\n")
        self.rationale.write_text("missing sections", encoding="utf-8")
        self.assertFalse(self.execute())
        self.assertEqual(self.archive.read_bytes(), b"previous archive\n")

    def test_wrong_session_and_child_session_are_rejected(self):
        for session_id, source in (("wrong-id", "cli"),
                                   (self.session_id, {"subagent": {"thread_spawn": {"parent_thread_id": "parent"}}})):
            self.write_codex(session_id, source)
            self.assertFalse(self.execute())
            self.assertEqual(self.archive.read_bytes(), b"previous archive\n")

    def test_failed_check_never_calls_archive(self):
        with patch.object(closeout, "archive_transcript") as archive:
            self.assertFalse(self.execute(failed_tool="callouts.py"))
            archive.assert_not_called()

    def test_copy_failure_preserves_previous_archive(self):
        self.assertFalse(self.execute())  # source is absent
        self.assertEqual(self.archive.read_bytes(), b"previous archive\n")
        self.assertFalse(list(self.run_dir.glob(".transcript-*")))

    def test_claude_child_and_mixed_session_ids_rejected(self):
        for records in ([dict(sessionId=self.session_id, isSidechain=True)],
                        [dict(sessionId=self.session_id), dict(sessionId="another-root")]):
            self.source.write_text("\n".join(json.dumps(r) for r in records), encoding="utf-8")
            self.assertFalse(self.execute())
            self.assertEqual(self.archive.read_bytes(), b"previous archive\n")

    def test_malformed_and_unidentified_transcripts_are_rejected(self):
        for content in ("", "not json\n", "{}\n", '[1,2]\n',
                        json.dumps({"sessionId": self.session_id}) + "\n{broken"):
            self.source.write_text(content, encoding="utf-8")
            self.assertFalse(self.execute())
            self.assertEqual(self.archive.read_bytes(), b"previous archive\n")
        self.assertFalse(list(self.run_dir.glob(".transcript-*")))

    def test_legacy_claude_lookup_still_works(self):
        folder = self.root / "sessions" / "project"
        folder.mkdir(parents=True)
        transcript = folder / (self.session_id + ".jsonl")
        transcript.write_text(json.dumps({"type": "user", "sessionId": self.session_id,
                                           "isSidechain": False}) + "\n", encoding="utf-8")
        self.assertTrue(self.execute(explicit=False))
        self.assertEqual(self.archive.read_bytes(), transcript.read_bytes())

    def test_ambiguous_legacy_lookup_is_rejected(self):
        for project in ("one", "two"):
            folder = self.root / "sessions" / project
            folder.mkdir(parents=True)
            (folder / (self.session_id + ".jsonl")).write_text("{}\n", encoding="utf-8")
        self.assertFalse(self.execute(explicit=False))
        self.assertEqual(self.archive.read_bytes(), b"previous archive\n")

    def test_no_archive_preflight_leaves_archive_and_final_report_alone(self):
        final_report = self.run_dir / "closeout_run.md"
        final_report.write_text("previous report", encoding="utf-8")
        self.assertTrue(self.execute(no_archive=True))
        self.assertEqual(self.archive.read_bytes(), b"previous archive\n")
        self.assertEqual(final_report.read_text(), "previous report")
        self.assertTrue((self.run_dir / "closeout_preflight.md").is_file())


if __name__ == "__main__":
    unittest.main()
