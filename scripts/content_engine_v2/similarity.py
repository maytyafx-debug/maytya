"""Deterministic near-duplicate detection for Persian and multilingual drafts."""
from __future__ import annotations
import re
from difflib import SequenceMatcher
from .schema import normalize_text

STOP = {"و","در","به","از","که","را","با","برای","این","آن","یک","است","شود","می","ها","the","a","an","and","or","of","to","in"}

def tokens(value: str) -> set[str]:
    text = normalize_text(value)
    # Restore token boundaries after normalization removed whitespace.
    raw = re.sub(r"[،؛,.!?؟:()\[\]{}«»\"']", " ", str(value or "").casefold())
    raw = raw.replace("ي","ی").replace("ك","ک")
    return {x for x in re.findall(r"[\wآ-ی]+", raw) if len(x)>1 and x not in STOP}

def similarity(left: str, right: str) -> float:
    a, b = tokens(left), tokens(right)
    if not a or not b: return 0.0
    jaccard = len(a & b) / len(a | b)
    compact_a, compact_b = normalize_text(left), normalize_text(right)
    sequence = SequenceMatcher(None, compact_a, compact_b).ratio()
    return round(max(jaccard, sequence * 0.92), 4)

def find_near_duplicates(item: dict, existing_items: list[dict] | None = None,
                         *, threshold: float = 0.72) -> list[dict]:
    matches=[]
    candidate = str(item.get("title","")) + " " + str(item.get("body",""))
    for old in existing_items or []:
        old_text = str(old.get("title","")) + " " + str(old.get("body",""))
        score = similarity(candidate, old_text)
        if score >= threshold:
            matches.append({"id":old.get("id"),"title":old.get("title",""),"similarity":score})
    return sorted(matches,key=lambda x:x["similarity"],reverse=True)
