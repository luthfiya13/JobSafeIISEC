#!/usr/bin/env python3
"""
Comprehensive Smoke Test Suite for JOBSAFE.
Runs:
1. Gold regression test cases (test_gold.py)
2. VerificationLayer unit tests (test_verification.py)
3. Hybrid engine & schema conformance tests (test_hybrid.py)
"""
import subprocess
import sys
from pathlib import Path

TESTS_DIR = Path(__file__).resolve().parent

def run_suite(script_name: str) -> bool:
    script_p = TESTS_DIR / script_name
    print(f"\n[RUNNING] {script_name}...")
    res = subprocess.run([sys.executable, str(script_p)], capture_output=True, text=True)
    if res.returncode == 0:
        print(f"[PASS] {script_name}")
        if res.stdout:
            for line in res.stdout.strip().split("\n")[-10:]:
                print(f"       {line}")
        return True
    else:
        print(f"[FAIL] {script_name} (Exit code: {res.returncode})")
        if res.stdout:
            print(res.stdout)
        if res.stderr:
            print(res.stderr)
        return False

def main():
    print("=" * 60)
    print("JOBSAFE COMPREHENSIVE TEST SUITE")
    print("=" * 60)
    
    suites = [
        "test_gold.py",
        "test_verification.py",
        "test_hybrid.py"
    ]
    
    results = {}
    for suite in suites:
        passed = run_suite(suite)
        results[suite] = passed

    print("\n" + "=" * 60)
    print("TEST SUITE SUMMARY:")
    all_passed = True
    for suite, passed in results.items():
        status = "PASS" if passed else "FAIL"
        print(f"  - {suite:<25} : {status}")
        if not passed:
            all_passed = False
            
    print("=" * 60)
    if all_passed:
        print("OVERALL RESULT: ALL TESTS PASSED [PASS]\n")
        sys.exit(0)
    else:
        print("OVERALL RESULT: SOME TESTS FAILED [FAIL]\n")
        sys.exit(1)

if __name__ == "__main__":
    main()
