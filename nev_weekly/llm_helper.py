import os
from typing import Dict, Any

try:
    from openai import OpenAI  # type: ignore
except Exception:
    OpenAI = None  # type: ignore


def _fallback_report(sections: Dict[str, Any]) -> str:
    parts = []
    parts.append("NEV Weekly Report")
    parts.append(f"Generated: {sections.get('meta', {}).get('generated_at', '')}")
    parts.append("")
    parts.append("Sales Rankings (>250k and >350k):")
    for band, items in sections.get("sales", {}).items():
        parts.append(f"- {band}:")
        for r in items:
            parts.append(f"  {r.get('rank','')}. {r.get('model','')} ({r.get('price_hint','')})")
    parts.append("")
    parts.append("New Car Launches:")
    for it in sections.get("launches", []):
        parts.append(f"- {it.get('model','')} | {it.get('price','N/A')} | Highlights: {', '.join(it.get('highlights', []))}")
    parts.append("")
    parts.append("Upcoming (Next Month):")
    for it in sections.get("upcoming", []):
        parts.append(f"- {it.get('model','')} | {it.get('notes','')}")
    parts.append("")
    parts.append("VIP Voices (Last 7 Days):")
    for it in sections.get("vip_voices", []):
        parts.append(f"- {it.get('name','')}: {it.get('summary','')}")
    parts.append("")
    parts.append("Smart Dimming Top 10:")
    for it in sections.get("dimming_news", []):
        parts.append(f"- {it.get('title','')} | {it.get('summary','')}")
    return "\n".join(parts)


def format_weekly_report(sections: Dict[str, Any]) -> str:
    api_key = os.getenv("OPENAI_API_KEY")
    if not (OpenAI and api_key):
        return _fallback_report(sections)
    try:
        client = OpenAI(api_key=api_key)
        prompt = (
            "You are an automotive industry analyst. "
            "Generate a concise, professional NEV Weekly report with clear sections: "
            "Sales Rankings, New Launches, Upcoming Releases, VIP Voices, Smart Dimming Intelligence. "
            "Use bullet points for items and keep it factual."
        )
        content = {
            "role": "user",
            "content": f"Summarize this structured data into a weekly report:\n{sections}",
        }
        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "system", "content": prompt}, content],
            temperature=0.3,
        )
        return resp.choices[0].message.content or _fallback_report(sections)
    except Exception:
        return _fallback_report(sections)


def format_competitor_report(data: Dict[str, Any]) -> str:
    api_key = os.getenv("OPENAI_API_KEY")
    if not (OpenAI and api_key):
        lines = []
        lines.append("# Competitor Analysis")
        lines.append(f"Total competitors: {data.get('total_competitors', 0)}")
        lines.append(f"Unique links collected: {data.get('unique_links', 0)}")
        lines.append("")
        for it in data.get("items", []):
            lines.append(f"- [{it.get('category','')}] {it.get('domain','')} status={it.get('status',0)} features={', '.join(it.get('features', []))}")
        return "\n".join(lines)
    try:
        client = OpenAI(api_key=api_key)
        prompt = (
            "Generate a concise competitor analysis in Markdown with headings per category, "
            "bulleted features per company, and note notable partnerships, manufacturing, and patents."
        )
        content = {"role": "user", "content": f"Analyze this competitor dataset:\n{data}"}
        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "system", "content": prompt}, content],
            temperature=0.2,
        )
        return resp.choices[0].message.content or ""
    except Exception:
        return ""
