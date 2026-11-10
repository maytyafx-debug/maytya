"""Allowlisted HTTPS source verification with bounded response reads."""
from __future__ import annotations
import ipaddress, re, socket
from urllib.parse import urlparse
import requests

DEFAULT_ALLOWLIST = {
    "nist.gov", "cftc.gov", "who.int", "olympics.com", "olympic.org",
    "fifa.com", "uefa.com", "fiba.basketball", "worldathletics.org",
    "sec.gov", "investor.gov", "finra.org", "consumerfinance.gov",
}

def _host_allowed(host: str, allowlist: set[str]) -> bool:
    host = (host or "").lower().rstrip(".")
    return any(host == domain or host.endswith("." + domain) for domain in allowlist)

def _safe_url(url: str, allowlist: set[str]) -> tuple[bool,str]:
    try:
        p=urlparse(url)
        if p.scheme != "https" or not p.hostname or p.username or p.password or p.port not in (None,443):
            return False,"only public HTTPS URLs on port 443 are accepted"
        host=p.hostname.lower().rstrip(".")
        if not _host_allowed(host,allowlist): return False,"domain is not in the official-source allowlist"
        try:
            infos=socket.getaddrinfo(host,443,type=socket.SOCK_STREAM)
            for info in infos:
                ip=ipaddress.ip_address(info[4][0])
                if not ip.is_global: return False,"non-public destination rejected"
        except OSError:
            return False,"domain could not be resolved"
        return True,host
    except ValueError:
        return False,"invalid URL"

def verify_source(source: dict, *, allowlist: set[str] | None = None, session=None,
                  timeout: int = 12, max_bytes: int = 65536) -> dict:
    allowed=allowlist or DEFAULT_ALLOWLIST
    url=str(source.get("url",""))
    safe,detail=_safe_url(url,allowed)
    if not safe: return {"ok":False,"url":url,"reason":detail}
    client=session or requests
    try:
        response=client.get(url,headers={"User-Agent":"MetatyaSourceVerifier/2.0","Range":f"bytes=0-{max_bytes-1}"},
                            timeout=timeout,stream=True,allow_redirects=False)
        status=response.status_code
        if status != 200 and status != 206:
            response.close()
            return {"ok":False,"url":url,"status":status,"reason":"source did not return a direct 200/206 response"}
        content_type=response.headers.get("Content-Type","").split(";")[0].lower()
        if content_type not in {"text/html","application/pdf","application/xhtml+xml"}:
            response.close()
            return {"ok":False,"url":url,"status":status,"content_type":content_type,"reason":"unsupported source content type"}
        chunks=[]; total=0
        for chunk in response.iter_content(chunk_size=8192):
            if not chunk: continue
            remaining=max_bytes-total
            chunks.append(chunk[:remaining]); total+=min(len(chunk),remaining)
            if total>=max_bytes: break
        response.close()
        sample=b"".join(chunks)
        title=""
        if content_type in {"text/html","application/xhtml+xml"}:
            match=re.search(rb"<title[^>]*>(.*?)</title>",sample,re.I|re.S)
            if match: title=re.sub(r"\s+"," ",match.group(1).decode("utf-8","ignore")).strip()[:240]
        return {"ok":True,"url":url,"status":status,"content_type":content_type,
                "title":title or source.get("title",""),"bytes_checked":total,
                "reason":"direct HTTPS source responded; content is not a full fact-check"}
    except requests.RequestException as exc:
        return {"ok":False,"url":url,"reason":type(exc).__name__}
