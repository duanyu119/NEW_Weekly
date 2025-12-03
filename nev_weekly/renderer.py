from typing import Dict, Any


def render_html(narrative: str, sections: Dict[str, Any]) -> str:
    meta = sections.get("meta", {})
    generated = meta.get("generated_at", "")
    return f"""
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8"/>
  <meta name="viewport" content="width=device-width,initial-scale=1"/>
  <title>NEV Weekly Newsletter</title>
  <link rel="stylesheet" href="./style.css"/>
</head>
<body>
  <div class="container">
    <header>
      <h1>NEV Weekly Newsletter</h1>
      <p class="meta">Generated at {generated}</p>
    </header>

    <section class="section">
      <h2>Executive Summary</h2>
      <pre style="white-space:pre-wrap">{narrative}</pre>
    </section>

    <section class="section">
      <h2>Sales Rankings</h2>
      <div class="item">
        <strong>&gt; 250k RMB</strong>
        <ol>
          {''.join([f'<li>{r.get('model','')} (rank {r.get('rank','')}) <a href="{r.get('source','')}">source</a></li>' for r in sections.get('sales', {}).get('over_250k', [])])}
        </ol>
      </div>
      <div class="item">
        <strong>&gt; 350k RMB</strong>
        <ol>
          {''.join([f'<li>{r.get('model','')} (rank {r.get('rank','')}) <a href="{r.get('source','')}">source</a></li>' for r in sections.get('sales', {}).get('over_350k', [])])}
        </ol>
      </div>
    </section>

    <section class="section">
      <h2>New Car Launches</h2>
      {''.join([f"<div class='item'><strong>{it.get('model','')}</strong> — {it.get('price','N/A')}<br/><small>{', '.join(it.get('highlights', []))}</small> <a href='{it.get('source','')}'>source</a></div>" for it in sections.get('launches', [])])}
    </section>

    <section class="section">
      <h2>Upcoming Releases (Next Month)</h2>
      {''.join([f"<div class='item'><strong>{it.get('model','')}</strong> — {it.get('window','')}<br/><small>{', '.join(it.get('notes', []))}</small> <a href='{it.get('source','')}'>source</a></div>" for it in sections.get('upcoming', [])])}
    </section>

    <section class="section">
      <h2>VIP Voices</h2>
      {''.join([f"<div class='item'><strong>{it.get('name','')}</strong><br/><small>{it.get('summary','')}</small>" + ''.join([f"<blockquote>{q}</blockquote>" for q in it.get('quotes', [])]) + ''.join([f" <a href='{s}'>source</a>" for s in it.get('sources', [])]) + "</div>" for it in sections.get('vip_voices', [])])}
    </section>

    <section class="section">
      <h2>Smart Dimming Intelligence</h2>
      <ol>
        {''.join([f"<li><a href='{it.get('url','')}'>{it.get('title','')}</a><br/><small>{it.get('summary','')}</small></li>" for it in sections.get('dimming_news', [])])}
      </ol>
    </section>

    {'' if not sections.get('competitors') else f"<section class='section'><h2>Competitor Analysis</h2>" + ''.join([f"<div class='item'><strong>[{it.get('category','')}] {it.get('domain','')}</strong> — status {it.get('status',0)}<br/><small>{', '.join(it.get('features', []))}</small></div>" for it in sections.get('competitors', {}).get('items', [])]) + "</section>"}

    <footer class="section">
      <small>Powered by Tavily search + LLM summarization. This page updates weekly via GitHub Actions.</small>
    </footer>
  </div>
</body>
</html>
"""
