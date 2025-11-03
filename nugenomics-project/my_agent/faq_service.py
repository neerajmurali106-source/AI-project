import os
import json
import requests
from bs4 import BeautifulSoup
from difflib import SequenceMatcher
from threading import Lock

FAQ_URL = "https://www.nugenomics.in/faqs/"
CACHE_DIR = os.path.join(os.path.dirname(__file__), "data")
os.makedirs(CACHE_DIR, exist_ok=True)
CACHE_PATH = os.path.join(CACHE_DIR, "faqs_cache.txt")
MIN_SCORE = 0.20
TOP_K = 3

_lock = Lock()
_index = []


def _similar(a, b):
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()


def _fetch_and_cache():
    headers = {"User-Agent": "nugenomics-faq-cache/1.0"}
    resp = requests.get(FAQ_URL, headers=headers, timeout=15)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")

    faqs = []
    headings = soup.find_all(['h2', 'h3', 'h4'])
    idc = 0
    for h in headings:
        q = h.get_text(strip=True)
        ans_parts = []
        sib = h.find_next_sibling()
        while sib and sib.name in ['p', 'div', 'ul', 'ol', 'span']:
            ans_parts.append(sib.get_text(separator=' ', strip=True))
            sib = sib.find_next_sibling()
        if q and ans_parts:
            faqs.append({"id": idc, "question": q, "answer": " ".join(ans_parts), "url": FAQ_URL})
            idc += 1

    if not faqs:
        full = soup.get_text(separator=' ', strip=True)
        faqs.append({"id": 0, "question": "NuGenomics FAQ", "answer": full, "url": FAQ_URL})

    with open(CACHE_PATH, "w", encoding="utf-8") as f:
        json.dump(faqs, f, ensure_ascii=False, indent=2)

    return faqs


def _load_index():
    global _index
    with _lock:
        if _index:
            return _index
        if os.path.exists(CACHE_PATH):
            try:
                with open(CACHE_PATH, "r", encoding="utf-8") as f:
                    _index = json.load(f)
                    return _index
            except Exception:
                pass
        _index = _fetch_and_cache()
        return _index


def query_faq(query):
    q = (query or "").strip()
    if not q:
        return {"query": q, "results": []}
    index = _load_index()
    scored = []
    for item in index:
        text = (item.get("question", "") + " " + item.get("answer", "")).lower()
        score = _similar(q, text)
        if score >= MIN_SCORE or q.lower() in text:
            scored.append((score, item))
    scored.sort(key=lambda x: x[0], reverse=True)
    results = []
    for s, item in scored[:TOP_K]:
        results.append({
            "score": float(s),
            "question": item.get("question"),
            "answer": item.get("answer"),
            "url": item.get("url")
        })
    return {"query": q, "results": results}
