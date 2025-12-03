import re
from datetime import datetime, timedelta
from typing import Dict, List, Tuple

from .tavily_client import TavilyWrapper


def _extract_models(text: str) -> List[str]:
    patterns = [
        r"[A-Z][A-Za-z0-9\-\s]{1,20}\b(?:Pro|Max|Plus)?",
        r"理想[LM][0-9]?",  # Li Auto L series
        r"问界[\w\-]+",
        r"比亚迪[\w\-]+",
        r"蔚来[\w\-]+",
        r"小鹏[\w\-]+",
        r"特斯拉Model\s?[S|3|X|Y]",
    ]
    found: List[str] = []
    for p in patterns:
        for m in re.findall(p, text):
            val = m.strip()
            if val and val not in found:
                found.append(val)
    return found[:20]


def get_sales_rankings(tavily: TavilyWrapper, top_n: int = 10) -> Dict[str, List[Dict]]:
    queries = [
        "中国 新能源 周销量 高端 SUV 轿车 25万以上 乘联会 懂车帝",
        "中国 新能源 周销量 高端 SUV 轿车 35万以上 乘联会 懂车帝",
    ]
    results = [tavily.search(q, max_results=20) for q in queries]

    def parse(items: List[Dict]) -> List[Dict]:
        ranking: List[Dict] = []
        for it in items:
            models = _extract_models((it.get("title") or "") + "\n" + (it.get("content") or ""))
            for idx, m in enumerate(models[:top_n]):
                ranking.append({"model": m, "rank": idx + 1, "price_hint": ">250k", "source": it.get("url")})
        # dedupe by model
        seen = set()
        dedup: List[Dict] = []
        for r in ranking:
            if r["model"] in seen:
                continue
            seen.add(r["model"])
            dedup.append(r)
        return dedup[:top_n]

    over_250 = parse(results[0])
    over_350 = [{**r, "price_hint": ">350k"} for r in parse(results[1])]

    return {"over_250k": over_250, "over_350k": over_350}


def get_new_car_launches(tavily: TavilyWrapper, max_items: int = 3) -> List[Dict]:
    seven_days_ago = (datetime.utcnow() - timedelta(days=7)).date().isoformat()
    q = f"过去一周 新车 发布 上市 中国 NEV {seven_days_ago}"
    items = tavily.search(q, max_results=25)
    launches: List[Dict] = []
    for it in items:
        models = _extract_models(it.get("title", "") + "\n" + it.get("content", ""))
        if not models:
            continue
        launches.append(
            {
                "model": models[0],
                "price": _find_price(it.get("content", "")),
                "highlights": _find_highlights(it.get("content", "")),
                "source": it.get("url"),
            }
        )
        if len(launches) >= max_items:
            break
    return launches


def get_upcoming_releases(tavily: TavilyWrapper, max_items: int = 5) -> List[Dict]:
    q = "下月 预计 发布 新车 中国 NEV 上市 预告"
    items = tavily.search(q, max_results=30)
    upcoming: List[Dict] = []
    for it in items:
        models = _extract_models(it.get("title", "") + "\n" + it.get("content", ""))
        if not models:
            continue
        upcoming.append(
            {
                "model": models[0],
                "window": "Next Month",
                "notes": _find_highlights(it.get("content", ""))[:2],
                "source": it.get("url"),
            }
        )
        if len(upcoming) >= max_items:
            break
    return upcoming


def get_vip_voices(tavily: TavilyWrapper, vip_names: List[str]) -> List[Dict]:
    end = datetime.utcnow().date().isoformat()
    start = (datetime.utcnow() - timedelta(days=7)).date().isoformat()
    out: List[Dict] = []
    for name in vip_names:
        q = f"{name} 演讲 采访 观点 {start}..{end} 新能源 汽车"
        items = tavily.search(q, max_results=10)
        if not items:
            out.append({"name": name, "quotes": [], "summary": "No recent coverage found", "sources": []})
            continue
        quotes: List[str] = []
        sources: List[str] = []
        for it in items:
            snippet = it.get("content", "")
            for s in re.findall(r"“([^”]{10,200})”|\"([^\"]{10,200})\"", snippet):
                qtxt = next((x for x in s if x), None)
                if qtxt and qtxt not in quotes:
                    quotes.append(qtxt)
            if it.get("url"):
                sources.append(it["url"])
        summary = _summarize_text("\n".join(quotes) or (items[0].get("content", "")[:300]))
        out.append({"name": name, "quotes": quotes[:3], "summary": summary, "sources": sources[:3]})
    return out


def get_smart_dimming_news(
    tavily: TavilyWrapper,
    competitors: List[str],
    keywords: List[str],
    target_count: int = 50,
    top_n: int = 10,
) -> List[Dict]:
    queries = []
    for comp in competitors:
        for kw in keywords:
            queries.append(f"{comp} {kw} 智能 调光 玻璃 新闻 合作 工厂 技术")

    collected: List[Tuple[str, str, str]] = []
    for q in queries:
        for it in tavily.search(q, max_results=min(10, target_count)):
            title = it.get("title", "").strip()
            url = it.get("url", "").strip()
            content = it.get("content", "")
            if title and url:
                collected.append((title, url, content))
            if len(collected) >= target_count:
                break
        if len(collected) >= target_count:
            break

    # score by keyword presence
    def score(content: str) -> int:
        s = 0
        low = content.lower()
        for kw in keywords:
            if kw.lower() in low:
                s += 2
        for tag in ["partnership", "合作", "技术", "factory", "工厂", "量产", "专利"]:
            if tag in low:
                s += 1
        return s

    unique: Dict[str, Dict] = {}
    for title, url, content in collected:
        if title in unique:
            continue
        unique[title] = {"title": title, "url": url, "score": score(content), "summary": _summarize_text(content[:600])}

    ranked = sorted(unique.values(), key=lambda x: x["score"], reverse=True)
    return ranked[:top_n]


def _find_price(text: str) -> str:
    m = re.search(r"(\d{2,3})\s*万|RMB\s*(\d{5,6})", text)
    if m:
        return m.group(0)
    return "N/A"


def _find_highlights(text: str) -> List[str]:
    bullets = re.findall(r"[•\-]\s*(.{10,120})", text)
    if bullets:
        return [b.strip() for b in bullets[:5]]
    # fallback: split sentences
    parts = re.split(r"[。.!?]\s+", text)
    return [p.strip() for p in parts if len(p.strip()) > 30][:3]


def _summarize_text(text: str) -> str:
    s = re.sub(r"\s+", " ", text).strip()
    if len(s) <= 240:
        return s
    return s[:240] + "…"
