from __future__ import annotations
import json
import re
from pathlib import Path
from typing import Any, Dict, List, Optional
from .text_utils import domain_from_url, SHORTENERS, EMAIL_RE

BASE_DIR = Path(__file__).resolve().parents[1]

class VerificationLayer:
    """
    Verification Layer for JOBSAFE.
    Evaluates employer identity, domain authenticity, and recruitment channel legitimacy.
    Produces 3 discrete states: VERIFIED | UNVERIFIED | CONTRADICTORY.
    
    Philosophy:
    - CONTRADICTORY: Explicit evidence of impersonation or mismatched official channels.
    - VERIFIED: Claimed employer matches verified corporate/government domain or trusted portal.
    - UNVERIFIED: Neutral baseline for independent employers, startups, UMKM without official registry entry.
      (UNVERIFIED is NEVER escalated to HIGH on its own).
    """
    def __init__(self, official_config_path: Optional[str] = None):
        p = Path(official_config_path) if official_config_path else BASE_DIR / "config/official_domains.json"
        self.official_db = json.loads(p.read_text(encoding="utf-8"))
        self.trusted_platforms = set(self.official_db.get("trusted_job_platforms", []))
        self.gov_suffixes = tuple(self.official_db.get("gov_domain_suffixes", ["go.id", "fhcibumn.id"]))
        self.orgs = self.official_db.get("orgs", [])

    def _is_domain_valid_for_org(self, domain: str, org: Dict[str, Any]) -> bool:
        d = domain.lower()
        allowed = set(self.trusted_platforms) | set(org.get("domains", []))
        if any(d == x or d.endswith("." + x) for x in allowed):
            return True
        if any(d.endswith("." + suf) or d == suf for suf in self.gov_suffixes):
            # Check if org is government/BUMN
            if "pemerintah" in org.get("name", "").lower() or "bumn" in org.get("name", "").lower() or any(d.endswith("." + x) for x in org.get("domains", [])):
                return True
        return False

    def verify(self, claimed_orgs: List[Dict[str, Any]], entities: Dict[str, List[str]], context: Dict[str, Any]) -> Dict[str, Any]:
        urls = entities.get("urls", [])
        emails = entities.get("emails", [])
        has_generic_email = context.get("generic_email", False)
        
        if not claimed_orgs:
            # Independent employer, UMKM, or startup not in official catalog
            return {
                "status": "UNVERIFIED",
                "claimed_employer": None,
                "official_domain_match": False,
                "application_channel": "independent_or_unregistered",
                "details": "Pemberi kerja independen / belum terdaftar di direktori resmi. Lakukan verifikasi mandiri (tabayyun).",
                "is_contradictory": False,
                "is_verified": False,
            }

        # For each claimed organization, check for contradictions or verification
        contradictions = []
        verified_matches = []
        org_names = [o["name"] for o in claimed_orgs]

        for org in claimed_orgs:
            org_name = org["name"]
            non_shortener_urls = [u for u in urls if u not in SHORTENERS and not u.endswith(".bit.ly")]
            
            # Check URL consistency
            if non_shortener_urls:
                mismatched_urls = [u for u in non_shortener_urls if not self._is_domain_valid_for_org(u, org)]
                matched_urls = [u for u in non_shortener_urls if self._is_domain_valid_for_org(u, org)]
                
                if mismatched_urls:
                    contradictions.append(f"Mencatut nama {org_name}, namun pendaftaran diarahkan ke domain non-resmi ({', '.join(mismatched_urls)}).")
                elif matched_urls:
                    verified_matches.append(f"Kanal pendaftaran sesuai domain resmi / platform terpercaya {org_name} ({', '.join(matched_urls)}).")

            # Check generic email on prominent organizations
            if has_generic_email and not any(self._is_domain_valid_for_org(u, org) for u in non_shortener_urls):
                generic_emails_found = [e for e in emails if re.search(r"@(?:gmail|yahoo|hotmail|outlook)\.[a-z.]{2,}", e, re.I)]
                if generic_emails_found:
                    contradictions.append(f"{org_name} diklaim, tetapi kontak pendaftaran menggunakan email gratisan ({', '.join(generic_emails_found)}).")

        if contradictions:
            return {
                "status": "CONTRADICTORY",
                "claimed_employer": org_names,
                "official_domain_match": False,
                "application_channel": "unauthorized_or_impersonated",
                "details": " | ".join(contradictions),
                "is_contradictory": True,
                "is_verified": False,
            }

        if verified_matches:
            return {
                "status": "VERIFIED",
                "claimed_employer": org_names,
                "official_domain_match": True,
                "application_channel": "official_corporate_or_trusted_platform",
                "details": " | ".join(verified_matches),
                "is_contradictory": False,
                "is_verified": True,
            }

        # Claimed org mentioned but no external domain/email to confirm or contradict
        return {
            "status": "UNVERIFIED",
            "claimed_employer": org_names,
            "official_domain_match": False,
            "application_channel": "unconfirmed_channel",
            "details": f"Nama {', '.join(org_names)} disebutkan, namun kanal pendaftaran belum dapat dikonfirmasi dengan domain resmi.",
            "is_contradictory": False,
            "is_verified": False,
        }
