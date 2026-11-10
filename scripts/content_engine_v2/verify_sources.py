"""Verify curated source URLs and emit a report; does not crawl or publish."""
from __future__ import annotations
import argparse,json
from pathlib import Path
from .source_registry import verify_source

def main():
    p=argparse.ArgumentParser()
    p.add_argument("input",help="JSON file containing sources[]")
    p.add_argument("--output",default="out/source-verification.json")
    a=p.parse_args()
    data=json.loads(Path(a.input).read_text(encoding="utf-8"))
    sources=data.get("sources")
    if not isinstance(sources,list): raise SystemExit("ورودی باید آرایه sources داشته باشد.")
    results=[{"source":s,"verification":verify_source(s)} for s in sources]
    report={"schema":"metatya.source-verification.v1","total":len(results),
            "verified":sum(x["verification"]["ok"] for x in results),
            "failed":sum(not x["verification"]["ok"] for x in results),"results":results}
    out=Path(a.output); out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({k:report[k] for k in ("total","verified","failed")},ensure_ascii=False))
    if report["failed"]: raise SystemExit(2)

if __name__=="__main__": main()
