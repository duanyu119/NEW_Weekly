from typing import Dict, List, Any, Tuple
import re
import httpx

from .tavily_client import TavilyWrapper


def _domain(url: str) -> str:
    m = re.search(r"https?://([^/]+)/?", url)
    return m.group(1) if m else url


def _keywords() -> List[str]:
    return [
        "electrochromic",
        "EC glass",
        "smart window",
        "PDLC",
        "SPD",
        "privacy glass",
        "automotive",
        "architectural",
        "factory",
        "manufacturing",
        "partnership",
        "patent",
    ]


def fetch_home(url: str, timeout: float = 10.0) -> Tuple[int, str]:
    try:
        with httpx.Client(follow_redirects=True, timeout=timeout) as client:
            r = client.get(url, headers={"User-Agent": "Mozilla/5.0"})
            return r.status_code, r.text[:2000]
    except Exception:
        return 0, ""


def analyze_competitors(tavily: TavilyWrapper, url_map: Dict[str, List[str]], min_search: int = 100) -> Dict[str, Any]:
    items: List[Dict[str, Any]] = []
    for cat, urls in url_map.items():
        for u in urls:
            code, text = fetch_home(u)
            feats: List[str] = []
            low = text.lower()
            for k in _keywords():
                if k in low and k not in feats:
                    feats.append(k)
            dom = _domain(u)
            q = f"{dom} electrochromic PDLC SPD smart window automotive architectural factory partnership"
            res = tavily.search(q, max_results=10)
            items.append({"category": cat, "url": u, "domain": dom, "status": code, "features": feats[:6], "links": [r.get("url") for r in res][:5]})

    collected: List[str] = []
    for it in items:
        collected.extend(it["links"])
    collected = [x for x in collected if x]
    uniq = []
    seen = set()
    for x in collected:
        if x in seen:
            continue
        seen.add(x)
        uniq.append(x)

    if len(uniq) < min_search:
        for cat, urls in url_map.items():
            for name in urls:
                extra = tavily.search(f"site:{_domain(name)} smart window electrochromic", max_results=20)
                for r in extra:
                    u = r.get("url")
                    if u and u not in seen:
                        seen.add(u)
                        uniq.append(u)
                    if len(uniq) >= min_search:
                        break
                if len(uniq) >= min_search:
                    break
            if len(uniq) >= min_search:
                break

    summary = {
        "total_competitors": len(items),
        "unique_links": len(uniq),
        "items": items,
        "links": uniq,
    }
    return summary
