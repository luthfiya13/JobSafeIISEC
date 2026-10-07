import sys, csv, unittest
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from jobsafe import JobsafeEngine

class TestGoldRegression(unittest.TestCase):
    def test_all_gold_cases(self):
        e = JobsafeEngine()
        bad = 0
        csv_path = ROOT / "data/gold_regression_cases.csv"
        with open(csv_path, encoding="utf-8-sig") as f:
            for r in csv.DictReader(f):
                x = e.analyze(r["text"])
                ok = (x["risk_level"] == r["expected_level"])
                if not ok:
                    bad += 1
                print("OK  " if ok else "FAIL", r["case_id"], r["tag"], r["expected_level"], "->", x["risk_level"], x["risk_score"], [i["code"] for i in x["indicators"]])
        self.assertEqual(bad, 0, f"Found {bad} failing gold regression cases.")

if __name__ == "__main__":
    unittest.main()

