"""V2 CLI for validating and rendering staged content without touching live publication."""
from __future__ import annotations
import argparse, json
from pathlib import Path
from .quality import evaluate
from .render import render_all


def main():
    parser = argparse.ArgumentParser(description="Metatya Content Engine V2 (safe staging mode)")
    parser.add_argument("input", help="JSON file containing {items:[...]}")
    parser.add_argument("--output", default="out/content-v2-review.json")
    parser.add_argument("--site-url", default="")
    args = parser.parse_args()
    data = json.loads(Path(args.input).read_text(encoding="utf-8"))
    if not isinstance(data, dict) or not isinstance(data.get("items"), list):
        raise SystemExit("ورودی باید دارای آرایه items باشد.")
    results = []
    seen = set()
    for item in data["items"]:
        report = evaluate(item, existing_titles=seen, existing_items=seen_items)
        item["quality"] = report
        item["channel_copy"] = render_all(item, args.site_url) if report["ok"] else {}
        results.append({"id":item.get("id"), "title":item.get("title"), **report})
        if report["ok"]:\n            seen.add(item.get("title", ""))\n            seen_items.append(item)
    out = {"schema":"metatya.content.v2.review", "items":data["items"], "summary":{"total":len(results),"passed":sum(x["ok"] for x in results),"failed":sum(not x["ok"] for x in results)}}
    path = Path(args.output); path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(out, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
    print(json.dumps(out["summary"], ensure_ascii=False))
    if out["summary"]["failed"]: raise SystemExit(2)

if __name__ == "__main__": main()
