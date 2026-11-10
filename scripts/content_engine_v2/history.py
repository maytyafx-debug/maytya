"""Read-only adapter for the live V1 content archive."""
from __future__ import annotations
import json
from pathlib import Path

def load_v1_history(path: str | Path = "docs/content.json") -> list[dict]:
    source=Path(path)
    if not source.exists(): return []
    data=json.loads(source.read_text(encoding="utf-8"))
    sections=data.get("sections",{})
    history=[]
    for domain,section in sections.items():
        for item in section.get("items",[]) if isinstance(section,dict) else []:
            if not isinstance(item,dict): continue
            history.append({"id":item.get("v2_id"),"domain":domain,"tab":item.get("tab",""),
                "title":item.get("title",""),"body":item.get("body",""),
                "date":item.get("date",""),"provider":item.get("provider","legacy-v1")})
    return history
