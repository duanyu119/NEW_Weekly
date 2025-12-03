from typing import List, Dict
import httpx


def check_links(urls: List[str]) -> List[Dict]:
    out: List[Dict] = []
    for u in urls:
        try:
            with httpx.Client(follow_redirects=True, timeout=8.0) as client:
                r = client.get(u, headers={"User-Agent": "Mozilla/5.0"})
                ok = 200 <= r.status_code < 400
                out.append({"url": u, "status": r.status_code, "ok": ok})
        except Exception:
            out.append({"url": u, "status": 0, "ok": False})
    return out
