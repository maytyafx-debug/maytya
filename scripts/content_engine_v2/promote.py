"""Explicit, reversible V2-to-V1 promotion. Dry-run is the default; no deletion or truncation."""
from __future__ import annotations
import argparse, json, os, tempfile
from datetime import datetime, timezone
from pathlib import Path
from .schema import to_v1
from .render import render_all


def prepare_promotion(v2_data: dict, legacy_data: dict, approved_ids: set[str]) -> tuple[dict,dict]:
    items=v2_data.get("items")
    if not isinstance(items,list): raise ValueError("V2 input must contain items[]")
    by_id={str(x.get("id")):x for x in items if isinstance(x,dict) and x.get("id")}
    missing=approved_ids-set(by_id)
    if missing: raise ValueError("Unknown approved IDs: "+", ".join(sorted(missing)))
    selected=[]
    for item_id in sorted(approved_ids):
        item=by_id[item_id]
        if item.get("status") != "approved": raise ValueError(f"Item {item_id} is not marked approved")
        if not item.get("quality",{}).get("ok"): raise ValueError(f"Item {item_id} failed quality gate")
        if not item.get("sources"): raise ValueError(f"Item {item_id} has no traceable sources")
        item=dict(item)
        item["channel_copy"]=render_all(item)
        selected.append((item.get("domain"),to_v1(item)))
    result=json.loads(json.dumps(legacy_data,ensure_ascii=False))
    sections=result.setdefault("sections",{})
    counts={}
    for domain,legacy in selected:
        if domain not in sections: sections[domain]={"name":domain,"items":[]}
        section=sections[domain]
        section.setdefault("items",[])
        if any(x.get("v2_id")==legacy.get("v2_id") for x in section["items"]):
            raise ValueError("Item already promoted: "+str(legacy.get("v2_id")))
        section["items"].insert(0,legacy)
        counts[domain]=counts.get(domain,0)+1
    result["updated"]=datetime.now(timezone.utc).isoformat(timespec="seconds")
    return result,{"approved":len(selected),"by_domain":counts,"total_after":sum(len(s.get("items",[])) for s in sections.values())}


def main():
    p=argparse.ArgumentParser(description="Promote only explicitly approved Metatya V2 items.")
    p.add_argument("input")
    p.add_argument("--approval-file",required=True,help='JSON: {"approved_ids":["..."]}')
    p.add_argument("--target",default="docs/content.json")
    p.add_argument("--backup-dir",default="docs/archive")
    p.add_argument("--apply",action="store_true",help="Write after making a timestamped backup; default is dry-run.")
    a=p.parse_args()
    v2=json.loads(Path(a.input).read_text(encoding="utf-8"))
    approval=json.loads(Path(a.approval_file).read_text(encoding="utf-8"))
    ids=set(approval.get("approved_ids",[]))
    if not ids: raise SystemExit("No approved_ids supplied; refusing empty promotion.")
    target=Path(a.target)
    legacy=json.loads(target.read_text(encoding="utf-8"))
    result,summary=prepare_promotion(v2,legacy,ids)
    print(json.dumps({"mode":"apply" if a.apply else "dry-run",**summary},ensure_ascii=False))
    if not a.apply: return
    backup_dir=Path(a.backup_dir); backup_dir.mkdir(parents=True,exist_ok=True)
    stamp=datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    backup=backup_dir/f"content-pre-v2-{stamp}.json"
    if backup.exists(): raise SystemExit("Backup already exists; refusing to overwrite.")
    backup.write_text(json.dumps(legacy,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    target.parent.mkdir(parents=True,exist_ok=True)
    fd,tmp=tempfile.mkstemp(prefix=target.name+".",suffix=".tmp",dir=str(target.parent))
    try:
        with os.fdopen(fd,"w",encoding="utf-8") as handle:
            json.dump(result,handle,ensure_ascii=False,indent=2); handle.write("\n")
        os.replace(tmp,target)
    except Exception:
        if os.path.exists(tmp): os.unlink(tmp)
        raise
    print(json.dumps({"written":str(target),"backup":str(backup)},ensure_ascii=False))

if __name__=="__main__":
    main()
