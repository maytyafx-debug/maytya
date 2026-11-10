"""Fair, review-only benchmark for selected OpenRouter models.

The score measures deterministic format/editorial checks only. It does not
verify factual correctness, source support, or publication readiness.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import time
from datetime import datetime, timezone
from pathlib import Path

import requests

API_URL = "https://openrouter.ai/api/v1/chat/completions"


def load_json(path: str) -> dict:
    with open(path, encoding="utf-8") as handle:
        return json.load(handle)


def parse_json(text: str) -> dict:
    raw = str(text or "").strip()
    raw = re.sub(r"^`{3}(?:json)?\s*|\s*`{3}$", "", raw, flags=re.I)
    start, end = raw.find("{"), raw.rfind("}")
    if start < 0 or end <= start:
        raise ValueError("response did not contain a JSON object")
    value = json.loads(raw[start:end + 1])
    if not isinstance(value, dict):
        raise ValueError("response JSON must be an object")
    return value


def build_prompt(task: dict) -> str:
    payload = {
        "domain": task["domain"],
        "tab": task["tab"],
        "audience": task["audience"],
        "source_pack": task["source_pack"],
        "allowed_source_ids": task["source_ids"],
    }
    return (
        "تو نویسنده آموزشی متاتیا هستی. فقط یک پیش‌نویس فارسی تولید کن.\n"
        f"وظیفه: {task['instruction']}\n"
        "قواعد: متن آموزشی و غیرشخصی؛ بدون توصیه مالی یا پزشکی شخصی، "
        "بدون ادعای قطعی بی‌منبع و بدون ساختن آمار. فقط از شناسه‌های منبع مجاز "
        "استفاده کن. سه جمله کوتاه برای short_script بده.\n"
        f"داده‌های ورودی: {json.dumps(payload, ensure_ascii=False)}\n"
        "فقط JSON معتبر با این کلیدها برگردان: "
        '{"title":"...","body":"...","short_script":["...","...","..."],'
        '"source_ids":["..."]}'
    )


def evaluate(output: dict, allowed_source_ids: list[str]) -> dict:
    checks = {}
    title = output.get("title")
    body = output.get("body")
    script = output.get("short_script")
    sources = output.get("source_ids")

    checks["title_present"] = isinstance(title, str) and bool(title.strip())
    checks["body_present"] = isinstance(body, str) and bool(body.strip())
    checks["body_length"] = isinstance(body, str) and 100 <= len(body) <= 1800
    checks["three_script_lines"] = isinstance(script, list) and len(script) == 3 and all(
        isinstance(line, str) and line.strip() for line in script
    )
    persian_text = " ".join(
        part for part in [title, body] if isinstance(part, str)
    )
    persian_chars = len(re.findall(r"[\u0600-\u06FF]", persian_text))
    checks["persian_language_signal"] = bool(persian_text) and persian_chars >= 20
    checks["sources_are_allowed"] = isinstance(sources, list) and all(
        str(source_id) in allowed_source_ids for source_id in sources
    )
    checks["no_personal_financial_or_medical_advice"] = not bool(
        re.search(
            r"(حتماً بخرید|حتماً بفروشید|نقطه ورود|نقطه خروج|سود تضمینی|"
            r"درمان قطعی|نسخه درمانی|برنامه تمرینی اختصاصی)",
            (body if isinstance(body, str) else ""),
            flags=re.I,
        )
    )
    weights = {
        "title_present": 10,
        "body_present": 10,
        "body_length": 15,
        "three_script_lines": 20,
        "persian_language_signal": 15,
        "sources_are_allowed": 15,
        "no_personal_financial_or_medical_advice": 15,
    }
    score = sum(weights[name] for name, passed in checks.items() if passed)
    return {
        "score": score,
        "checks": checks,
        "passed_checks": sum(bool(value) for value in checks.values()),
        "total_checks": len(checks),
        "warning": "این امتیاز فقط قالب و قواعد قطعی را می‌سنجد؛ صحت factual و پشتیبانی ادعاها از منبع را تأیید نمی‌کند.",
    }


def call_model(model_id: str, prompt: str, api_key: str, timeout: int) -> dict:
    started = time.monotonic()
    response = requests.post(
        API_URL,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://maytyafx-debug.github.io/maytya/",
            "X-Title": "METATYA Model Benchmark V1",
        },
        json={
            "model": model_id,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.2,
            "max_tokens": 1200,
        },
        timeout=timeout,
    )
    elapsed_ms = round((time.monotonic() - started) * 1000)
    if response.status_code == 429:
        return {"status": "rate_limited", "http_status": 429, "latency_ms": elapsed_ms}
    if response.status_code >= 500:
        return {"status": "provider_error", "http_status": response.status_code, "latency_ms": elapsed_ms}
    response.raise_for_status()
    payload = response.json()
    content = payload["choices"][0]["message"]["content"]
    parsed = parse_json(content)
    usage = payload.get("usage", {})
    return {
        "status": "completed",
        "latency_ms": elapsed_ms,
        "output": parsed,
        "usage": {
            "prompt_tokens": usage.get("prompt_tokens"),
            "completion_tokens": usage.get("completion_tokens"),
            "total_tokens": usage.get("total_tokens"),
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="METATYA Model Benchmark V1; review-only.")
    parser.add_argument("--models", default="scripts/model_benchmark_v1/models.json")
    parser.add_argument("--prompts", default="scripts/model_benchmark_v1/prompts.json")
    parser.add_argument("--output", default="out/model-benchmark-v1.json")
    parser.add_argument("--timeout", type=int, default=75)
    args = parser.parse_args()

    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        raise SystemExit("OPENROUTER_API_KEY is required; no model calls were made.")

    model_config = load_json(args.models)
    prompt_config = load_json(args.prompts)
    results = []
    for model in model_config["models"]:
        for task in prompt_config["tasks"]:
            record = {
                "model_id": model["id"],
                "model_label": model["label"],
                "role": model.get("role", ""),
                "task_id": task["id"],
                "domain": task["domain"],
            }
            try:
                response = call_model(model["id"], build_prompt(task), api_key, args.timeout)
                record.update({key: value for key, value in response.items() if key != "output"})
                if response["status"] == "completed":
                    record["evaluation"] = evaluate(response["output"], task["source_ids"])
                    record["output"] = response["output"]
            except requests.Timeout:
                record["status"] = "timeout"
            except requests.ConnectionError:
                record["status"] = "connection_error"
            except (requests.HTTPError, KeyError, IndexError, TypeError, ValueError) as exc:
                record["status"] = "invalid_response_or_http_error"
                record["error"] = str(exc)[:300]
            results.append(record)

    summaries = []
    for model in model_config["models"]:
        rows = [row for row in results if row["model_id"] == model["id"]]
        completed = [row for row in rows if row["status"] == "completed"]
        scores = [row["evaluation"]["score"] for row in completed]
        latencies = [row["latency_ms"] for row in completed if row.get("latency_ms") is not None]
        summaries.append({
            "model_id": model["id"],
            "model_label": model["label"],
            "tasks_completed": len(completed),
            "tasks_total": len(rows),
            "average_format_score": round(sum(scores) / len(scores), 2) if scores else None,
            "average_latency_ms": round(sum(latencies) / len(latencies)) if latencies else None,
            "rate_limited": sum(row["status"] == "rate_limited" for row in rows),
            "errors": sum(row["status"] not in {"completed", "rate_limited"} for row in rows),
        })

    result = {
        "schema": "metatya.model-benchmark.v1.results",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "provider": "openrouter",
        "summary": summaries,
        "results": results,
        "limitations": [
            "A format score is not a factual-accuracy score.",
            "Source URLs are supplied as metadata; this benchmark does not fetch or verify source claims.",
            "No result is publication approval.",
            "Free model availability and rate limits can change without notice.",
        ],
    }
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"models": len(model_config["models"]), "tasks": len(prompt_config["tasks"]),
                      "calls": len(results), "output": str(output_path)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
