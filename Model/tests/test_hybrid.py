import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from jobsafe.hybrid_engine import JobsafeHybridEngine
from jobsafe.engine import JobsafeEngine

class TestHybridEngine(unittest.TestCase):
    def setUp(self):
        self.engine = JobsafeHybridEngine()

    def test_schema_conformance(self):
        text = "Lowongan Staff Admin PT Sinar Abadi. Gaji UMR, kualifikasi S1. Info resmi di karir.sinarabadi.co.id."
        res = self.engine.analyze(text, mode="hybrid")
        
        # Verify mandatory output schema fields
        mandatory_keys = [
            "risk_score", "risk_level", "detected_indicators", "evidence",
            "dimension_scores", "verification_status", "context_flags",
            "risk_explanation", "recommended_actions", "disclaimer"
        ]
        for key in mandatory_keys:
            self.assertIn(key, res, f"Missing mandatory field '{key}' in engine output")

        # Verify backward compatibility fields
        compat_keys = [
            "message", "dimensions", "indicators", "recommendations",
            "verification_checklist", "context", "meta"
        ]
        for key in compat_keys:
            self.assertIn(key, res, f"Missing backward compatibility field '{key}' in engine output")

    def test_critical_scam_floor_override(self):
        # Explicit payment scam must result in HIGH in hybrid mode
        text = "Lolos seleksi tahap 1. Wajib transfer biaya pendaftaran Rp 250.000 untuk seragam ke rekening panitia."
        res = self.engine.analyze(text, mode="hybrid")
        self.assertEqual(res["risk_level"], "HIGH")
        self.assertGreaterEqual(res["risk_score"], 60)
        self.assertEqual(res["meta"]["hybrid_decision_type"], "CRITICAL_RULE_FLOOR_OVERRIDE")

    def test_task_scam_floor_override(self):
        # Like and subscribe task scam
        text = "Kerja sampingan like video TikTok komisi 100rb/hari. Wajib deposit modal 200rb untuk aktivasi akun tugas. Pasti profit."
        res = self.engine.analyze(text, mode="hybrid")
        self.assertEqual(res["risk_level"], "HIGH")
        self.assertGreaterEqual(res["risk_score"], 60)

    def test_legitimate_posting_safety(self):
        # Legitimate UMKM with WhatsApp and free statement
        text = "Warung Soto Hj. Hesti butuh kitchen helper, lokasi Depok, syarat SMP, gaji UMK. Kirim lamaran via WA 0812-2937-7625. Tidak dipungut biaya."
        res = self.engine.analyze(text, mode="hybrid")
        self.assertEqual(res["risk_level"], "LOW")
        self.assertLess(res["risk_score"], 25)

    def test_modes_switch(self):
        text = "PT Bank Central Asia membuka lowongan CS. Daftar di career.bca.co.id."
        res_rule = self.engine.analyze(text, mode="rule_only")
        res_ml = self.engine.analyze(text, mode="ml_only")
        res_hyb = self.engine.analyze(text, mode="hybrid")
        
        self.assertEqual(res_rule["meta"]["hybrid_mode"], "rule_only")
        self.assertEqual(res_ml["meta"]["hybrid_mode"], "ml_only")
        self.assertEqual(res_hyb["meta"]["hybrid_mode"], "hybrid")

if __name__ == "__main__":
    unittest.main()
