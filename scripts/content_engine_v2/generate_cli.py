"""Generate a review-only V2 batch from a JSON job manifest."""
from __future__ import annotations
import argparse, json
from pathlib import Path
from .generator import generate_item

def main():
    parser=argparse.ArgumentParser(description="Generate Metatya V2 drafts; never publishes them.")
    parser.add_argument("manifest", help="JSON with jobs[] and optional history_titles[]")
    parser.add_argument("--output",default="out/content-v2-generated.json")
    args=parser.parse_args()
    manifest=json.loads(Path(args.manifest).read_text(encoding="utf-8"))
    jobs=manifest.get("jobs")
    if not isinstance(jobs,list) or not jobs: raise SystemExit("manifest باید آرایه غیرخالی jobs داشته باشد.")
    history=manifest.get("history_titles",[])
    items=[]; failures=[]
    for index,job in enumerate(jobs):
        try:
            item=generate_item(domain=job["domain"],tab=job["tab"],audience=job["audience"],
                source_pack=job.get("source_pack",[]),history_titles=history,
                formats=job.get("formats",["website","telegram"]))
            items.append(item)
            if item["status"] == "review": history.append(item["title"])
            else: failures.append({"index":index,"title":item.get("title"),"errors":item["quality"]["errors"]})
        except Exception as exc:
            failures.append({"index":index,"error":str(exc)[:500]})
    result={"schema":"metatya.content.v2.batch","items":items,
        "summary":{"requested":len(jobs),"generated":len(items),"eligible_for_review":sum(x["status"]=="review" for x in items),"failed":len(failures)},
        "failures":failures}
    path=Path(args.output); path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(result["summary"],ensure_ascii=False))
    if failures: raise SystemExit(2)

if __name__ == "__main__": main()
