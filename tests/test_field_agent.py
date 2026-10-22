import json
from pathlib import Path
import tempfile
import unittest
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import field_agent


class FieldAgentTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        (self.root / "field_rules.py").write_text(field_agent.rule_source(1, 0), encoding="utf-8")

    def tearDown(self):
        self.temp.cleanup()

    def test_real_file_reused_on_subsequent_run_without_api(self):
        first = field_agent.run(self.root, "demo")
        self.assertEqual("run_research_probe", first["decision_before"])
        self.assertEqual("adopted", first["adoption"])
        self.assertEqual("read_primary_source", first["decision_after"])
        self.assertEqual(2, field_agent.read_rule(self.root)["version"])
        second = field_agent.run(self.root, "demo")
        self.assertEqual("read_primary_source", second["decision_before"])
        self.assertEqual("unchanged", second["adoption"])
        self.assertEqual(0, first["api_usage"]["total_tokens"])
        self.assertEqual(2, len(json.loads((self.root / "field_runs.json").read_text())))

    def test_comparison_keeps_verified_source_path(self):
        c = field_agent.compare_rules({"minimum_verified_sources": 0}, {"minimum_verified_sources": 1})
        self.assertTrue(c["passed"])
        self.assertEqual(["unverified"], c["changed_cases"])
        self.assertTrue(c["invariants"]["verified_source_still_allows_probe"])

    def test_does_not_evaluate_untrusted_source(self):
        (self.root / "field_rules.py").write_text("import os\nos.system('false')\n")
        with self.assertRaises(ValueError):
            field_agent.run(self.root, "demo")

    def test_live_without_source_does_not_call_api(self):
        with self.assertRaisesRegex(ValueError, "requires --source-url"):
            field_agent.run(self.root, "live")
        self.assertEqual(1, field_agent.read_rule(self.root)["version"])

    def test_rejects_non_arxiv_or_redirect_source(self):
        for url in ("http://arxiv.org/abs/2505.06120", "https://localhost/abs/2505.06120",
                    "https://arxiv.org.evil.com/abs/2505.06120", "https://arxiv.org/redirect"):
            with self.subTest(url=url), self.assertRaises(ValueError):
                field_agent.read_primary(url)


if __name__ == "__main__":
    unittest.main()
