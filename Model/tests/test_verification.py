import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from jobsafe.verification import VerificationLayer
from jobsafe.rules import detect

class TestVerificationLayer(unittest.TestCase):
    def setUp(self):
        self.verifier = VerificationLayer()

    def test_verified_official_domain(self):
        # Case 1: Pertamina claimed + official website pertamina.com
        text = "PT Pertamina (Persero) membuka lowongan MT 2026. Daftar melalui website resmi recruitment.pertamina.com."
        d = detect(text)
        res = self.verifier.verify(d["claimed_org_objects"], d["entities"], d["context"])
        self.assertEqual(res["status"], "VERIFIED")
        self.assertTrue(res["official_domain_match"])
        self.assertFalse(res["is_contradictory"])

    def test_verified_trusted_platform(self):
        # Case 2: BCA claimed + trusted job platform glints.com
        text = "PT Bank Central Asia (BCA) membuka lowongan Data Analyst. Pendaftaran melalui portal https://glints.com/id/opportunities/jobs/bca-data-analyst."
        d = detect(text)
        res = self.verifier.verify(d["claimed_org_objects"], d["entities"], d["context"])
        self.assertEqual(res["status"], "VERIFIED")
        self.assertTrue(res["official_domain_match"])

    def test_contradictory_phishing_domain(self):
        # Case 3: BNI claimed + unofficial third-party domain goletskerja.com
        text = "Rekrutmen BNI Bina BNI Teller 2026. Pendaftaran resmi dibuka di http://goletskerja.com/bni-teller-2026."
        d = detect(text)
        res = self.verifier.verify(d["claimed_org_objects"], d["entities"], d["context"])
        self.assertEqual(res["status"], "CONTRADICTORY")
        self.assertFalse(res["official_domain_match"])
        self.assertTrue(res["is_contradictory"])
        self.assertIn("goletskerja.com", res["details"])

    def test_contradictory_generic_email(self):
        # Case 4: Bank Mandiri claimed + free generic gmail
        text = "Lowongan Bank Mandiri Officer Development Program. Kirim berkas CV ke rekrutmen.mandiri2026@gmail.com."
        d = detect(text)
        res = self.verifier.verify(d["claimed_org_objects"], d["entities"], d["context"])
        self.assertEqual(res["status"], "CONTRADICTORY")
        self.assertTrue(res["is_contradictory"])

    def test_unverified_independent_umkm(self):
        # Case 5: Independent UMKM with Gmail / WA (Must remain UNVERIFIED, not CONTRADICTORY)
        text = "Toko Kue Armindo Magelang butuh kasir, kirim lamaran ke armindomagelang@gmail.com atau WA 0812345678."
        d = detect(text)
        res = self.verifier.verify(d["claimed_org_objects"], d["entities"], d["context"])
        self.assertEqual(res["status"], "UNVERIFIED")
        self.assertFalse(res["is_contradictory"])
        self.assertFalse(res["is_verified"])

    def test_unverified_startup_custom_domain(self):
        # Case 6: Independent startup with custom domain not in curated catalog
        text = "PT Herpil Nusantara Solusi mencari Software Engineer. Kirim CV ke jobs@herpil.id."
        d = detect(text)
        res = self.verifier.verify(d["claimed_org_objects"], d["entities"], d["context"])
        self.assertEqual(res["status"], "UNVERIFIED")
        self.assertFalse(res["is_contradictory"])

if __name__ == "__main__":
    unittest.main()
