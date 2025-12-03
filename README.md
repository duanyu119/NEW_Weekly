# NEV Weekly Newsletter

This repository generates a weekly NEV (New Energy Vehicle) newsletter from Tavily search results and summarizes them with an LLM. The output is a static site under `public/`.

## Cloudflare Pages Deployment

- Create a new Cloudflare Pages project and connect this GitHub repository.
- Set the build preset to “None” (no build), because we publish ready-made static files.
- Set the output directory to `public`.
- Environment variables (optional but recommended):
  - `TAVILY_API_KEY` – Tavily search key
  - `OPENAI_API_KEY` – for LLM summarization (fallback is used if absent)
- On every push (and scheduled runs via GitHub Actions), the `public/index.html` will be updated and Cloudflare Pages will redeploy automatically.

## Local Development

- Python 3.10+
- `pip install -r requirements.txt`
- Set `TAVILY_API_KEY` and optionally `OPENAI_API_KEY` in your shell.
- Run `python main.py` to generate `public/index.html`.

## Configuration

Editable lists live under `config/` and are loaded at runtime:
- `competitors.yaml` – smart dimming/auto glass competitors
- `vips.yaml` – key industry figures
- `keywords.yaml` – smart dimming keywords

Update these files without changing any code.

## Notes

- Searches target CPCA (乘联会) or Dongchedi (懂车帝) for weekly sales, plus general sources for launches and VIP quotes.
- When API keys are missing, the generator uses conservative fallbacks to avoid crashes.
