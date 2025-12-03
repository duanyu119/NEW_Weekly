from typing import List, Dict, Optional
from tenacity import retry, stop_after_attempt, wait_exponential

try:
    from tavily import TavilyClient  # type: ignore
except Exception:
    TavilyClient = None  # type: ignore


class TavilyWrapper:
    def __init__(self, api_key: Optional[str] = None) -> None:
        self.enabled = bool(api_key and TavilyClient)
        self.client = TavilyClient(api_key=api_key) if self.enabled else None

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=1, max=8))
    def _search(self, query: str, max_results: int = 10) -> List[Dict]:
        assert self.client is not None
        res = self.client.search(query=query, max_results=max_results)
        items = []
        for r in res.get("results", []):
            items.append(
                {
                    "title": r.get("title") or "",
                    "content": r.get("content") or "",
                    "url": r.get("url") or "",
                }
            )
        return items

    def search(self, query: str, max_results: int = 10) -> List[Dict]:
        if not self.enabled:
            return []
        try:
            return self._search(query=query, max_results=max_results)
        except Exception:
            return []
