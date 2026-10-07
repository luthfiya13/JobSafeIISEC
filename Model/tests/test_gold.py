import sys, csv
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; sys.path.insert(0,str(ROOT))
from jobsafe import JobsafeEngine
e=JobsafeEngine(); bad=0
for r in csv.DictReader(open(ROOT/"data/gold_regression_cases.csv",encoding="utf-8-sig")):
    x=e.analyze(r["text"]); ok=x["risk_level"]==r["expected_level"]; bad+=not ok
    print("OK  " if ok else "FAIL", r["case_id"], r["tag"], r["expected_level"], "->", x["risk_level"], x["risk_score"], [i["code"] for i in x["indicators"]])
print("FAILED:",bad); sys.exit(1 if bad else 0)
