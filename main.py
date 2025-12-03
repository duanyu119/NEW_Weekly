import os
from pathlib import Path
from datetime import datetime

from nev_weekly.config_loader import load_yaml_list, load_yaml_map
from nev_weekly.tavily_client import TavilyWrapper
from nev_weekly.aggregators import (
    get_sales_rankings,
    get_new_car_launches,
    get_upcoming_releases,
    get_vip_voices,
    get_smart_dimming_news,
)
from nev_weekly.llm_helper import format_weekly_report, format_competitor_report
from nev_weekly.renderer import render_html
from nev_weekly.competitor_analysis import analyze_competitors
from nev_weekly.link_checker import check_links


# Entry point orchestrates the weekly newsletter generation.
# It reads YAML configs, runs Tavily-powered searches for each task,
# summarizes with an LLM (or fallback), and writes public/index.html.


def ensure_public_dir() -> Path:
    out_dir = Path("public")
    out_dir.mkdir(parents=True, exist_ok=True)
    return out_dir


def main() -> None:
    root = Path(__file__).parent
    config_dir = root / "config"

    competitors = load_yaml_list(config_dir / "competitors.yaml")
    vips = load_yaml_list(config_dir / "vips.yaml")
    keywords = load_yaml_list(config_dir / "keywords.yaml")
    comp_urls = load_yaml_map(config_dir / "competitor_urls.yaml")

    tavily = TavilyWrapper(api_key=os.getenv("TAVILY_API_KEY"))

    # Task A: Weekly NEV sales rankings for China.
    # Queries target CPCA (乘联会) and Dongchedi (懂车帝) summaries.
    sales = get_sales_rankings(tavily=tavily, top_n=10)

    # Task B: New car launches (past week) and upcoming releases (next month).
    launches = get_new_car_launches(tavily=tavily, max_items=3)
    upcoming = get_upcoming_releases(tavily=tavily, max_items=5)

    # Task C: VIP voices (last 7 days) based on vips.yaml.
    vip_items = get_vip_voices(tavily=tavily, vip_names=vips)

    # Task D: Smart dimming industry intelligence combining competitors + keywords.
    dimming_news = get_smart_dimming_news(
        tavily=tavily, competitors=competitors, keywords=keywords, target_count=50, top_n=10
    )

    competitor_summary = analyze_competitors(tavily=tavily, url_map=comp_urls, min_search=100)

    sections = {
        "meta": {"generated_at": datetime.utcnow().isoformat().replace("T", " ") + "Z"},
        "sales": sales,
        "launches": launches,
        "upcoming": upcoming,
        "vip_voices": vip_items,
        "dimming_news": dimming_news,
        "competitors": competitor_summary,
    }

    # Use LLM helper to turn raw data into a professional weekly report narrative.
    narrative = format_weekly_report(sections)

    html = render_html(narrative=narrative, sections=sections)

    out_dir = ensure_public_dir()
    (out_dir / "index.html").write_text(html, encoding="utf-8")

    # Ensure a basic stylesheet exists for clean presentation.
    style_path = out_dir / "style.css"
    if not style_path.exists():
        style_path.write_text(
            
            ".container{max-width:960px;margin:2rem auto;padding:0 1rem}"
            "body{font-family:-apple-system,BlinkMacSystemFont,Segoe UI,Roboto,Helvetica,Arial,sans-serif;"
            "color:#1f2937;background:#f9fafb}"
            "h1,h2{color:#111827}"
            ".section{background:#fff;border:1px solid #e5e7eb;border-radius:12px;padding:1rem;margin:1rem 0}"
            ".item{padding:.5rem 0;border-top:1px dashed #e5e7eb}"
            ".item:first-child{border-top:none}"
            ".meta{font-size:.875rem;color:#6b7280}"
            ,
            encoding="utf-8",
        )

    print("Generated public/index.html")

    comp_md = format_competitor_report(competitor_summary) or ""
    (out_dir / "competitor_report.md").write_text(comp_md, encoding="utf-8")

    link_report = check_links(competitor_summary.get("links", []))
    bad = [x for x in link_report if not x.get("ok")]
    lines = ["# Link Validation Report", f"Total checked: {len(link_report)}", f"Invalid: {len(bad)}", "", "## Invalid Links"]
    for x in bad:
        lines.append(f"- {x['url']} status={x['status']}")
    (out_dir / "link_report.md").write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__":
    main()
