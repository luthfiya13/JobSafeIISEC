from __future__ import annotations
import re, unicodedata
from typing import Dict, List

TLDS = r"(?:com|net|org|id|co|io|info|xyz|site|online|top|click|link|app|me|ly|gl|gle|in|cc|tk|ml|ga|cf|my|sg|asia|biz|shop|store|work|jobs|cam|page|dev)"
PHONE_RE = re.compile(r"(?<![\d+])(?:\+?62|0)\s?8\d{2}[\s-]?\d{3,4}[\s-]?\d{2,5}(?!\d)")
FOREIGN_PHONE_RE = re.compile(r"(?<!\d)\+(?!62)\d{1,3}[\s-]?\d{6,12}(?!\d)")
EMAIL_RE = re.compile(r"(?i)\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b")
# domain harus ber-TLD dikenal: "Jl.Sudirman", "No.2", "Microsoft.Office" tidak lagi dianggap URL
URL_RE = re.compile(rf"(?i)(?<![@\w.-])(?:https?://)?(?:www\.)?(?:[a-z0-9-]+\.)+{TLDS}(?![a-z0-9])(?:/[^\s<>()]*)?")
SHORTENERS = ("bit.ly","tinyurl.com","s.id","cutt.ly","shorturl.at","rb.gy","t.ly","is.gd","lnkd.in","forms.gle","linktr.ee","wa.me","t.me")

def clean(text: str) -> str:
    t = unicodedata.normalize("NFKC", str(text or "")).replace("\u200b", "")
    return t.replace("\r", "\n")

def normalize_text(text: str) -> str:
    return re.sub(r"[ \t\f\v]+", " ", re.sub(r"\n{2,}", "\n", clean(text))).strip()

def split_sentences(text: str) -> List[str]:
    parts = re.split(r"\n|(?<=[.!?])\s+(?=[A-Z0-9])", normalize_text(text))
    return [p.strip() for p in parts if p.strip()]

def mask_personal_data(text: str) -> str:
    return EMAIL_RE.sub("[EMAIL]", PHONE_RE.sub("[PHONE]", FOREIGN_PHONE_RE.sub("[PHONE]", normalize_text(text))))

def domain_from_url(url: str) -> str:
    u = re.sub(r"^https?://", "", str(url or "").lower().strip())
    u = u[4:] if u.startswith("www.") else u
    return u.split("/", 1)[0].split(":", 1)[0].split("?", 1)[0]

def extract_entities(text: str) -> Dict[str, List[str]]:
    t = normalize_text(text)
    emails = EMAIL_RE.findall(t)
    no_email = EMAIL_RE.sub(" ", t)
    urls = [domain_from_url(m.group(0)) for m in URL_RE.finditer(no_email)]
    return {"urls": list(dict.fromkeys(u for u in urls if u)), "emails": emails,
            "phones": PHONE_RE.findall(t), "foreign_phones": FOREIGN_PHONE_RE.findall(t)}
