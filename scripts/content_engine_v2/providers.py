"""OpenRouter provider with bounded retries and model fallback; no fake local success."""
from __future__ import annotations
import json, os, re, time
import requests

API_URL = "https://openrouter.ai/api/v1/chat/completions"
DEFAULT_MODELS = ["xingchen-agi/xing4.0-29b-a4b:free"]


def parse_json(text: str) -> dict:
    raw = str(text or "").strip()
    raw = re.sub(r"^\x60{3}(?:json)?\s*|\s*\x60{3}$", "", raw, flags=re.I)
    start, end = raw.find("{"), raw.rfind("}")
    if start < 0 or end <= start: raise ValueError("پاسخ مدل JSON معتبر ندارد")
    value = json.loads(raw[start:end+1])
    if not isinstance(value, dict): raise ValueError("خروجی مدل باید شیء JSON باشد")
    return value


def configured_models() -> list[str]:
    raw = os.getenv("OPENROUTER_MODELS", "")
    models = [x.strip() for x in raw.split(",") if x.strip()]
    return models or DEFAULT_MODELS


def generate_json(prompt: str, *, api_key: str | None = None, models: list[str] | None = None,
                  timeout: int = 60, retries_per_model: int = 2, session=None) -> dict:
    key = api_key or os.getenv("OPENROUTER_API_KEY")
    if not key: raise RuntimeError("OPENROUTER_API_KEY تنظیم نشده است")
    client = session or requests
    failures = []
    for model in (models or configured_models()):
        for attempt in range(max(1, retries_per_model)):
            try:
                response = client.post(API_URL, headers={"Authorization":f"Bearer {key}","Content-Type":"application/json"},
                    json={"model":model,"messages":[{"role":"user","content":prompt}],"temperature":0.55}, timeout=timeout)
                if response.status_code == 429 or response.status_code >= 500:
                    failures.append(f"{model}: HTTP {response.status_code}")
                    if attempt + 1 < retries_per_model: time.sleep(min(2 ** attempt, 4))
                    continue
                response.raise_for_status()
                payload = response.json()
                content = payload["choices"][0]["message"]["content"]
                result = parse_json(content)
                result["_provider"] = "openrouter"
                result["_model"] = model
                return result
            except (requests.Timeout, requests.ConnectionError) as exc:
                failures.append(f"{model}: {type(exc).__name__}")
                if attempt + 1 < retries_per_model: time.sleep(min(2 ** attempt, 4))
            except (KeyError, IndexError, TypeError, ValueError, requests.HTTPError) as exc:
                failures.append(f"{model}: {type(exc).__name__}: {str(exc)[:120]}")
                break
    raise RuntimeError("تولید محتوا انجام نشد؛ هیچ محتوای ساختگی جایگزین نشد. " + " | ".join(failures))


def resolve_sources(source_ids: list[str], source_pack: list[dict]) -> list[dict]:
    by_id = {str(s.get("id")):s for s in source_pack if isinstance(s, dict) and s.get("id")}
    unknown = [str(x) for x in source_ids if str(x) not in by_id]
    if unknown: raise ValueError("مدل به شناسه منبع ناموجود ارجاع داده است: " + ", ".join(unknown))
    return [{"title":by_id[str(x)].get("title",""),"url":by_id[str(x)].get("url","")} for x in source_ids]
