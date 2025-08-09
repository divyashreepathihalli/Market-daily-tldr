from __future__ import annotations

import os
from datetime import datetime, timedelta
from typing import Dict, List

import requests

try:
    import feedparser  # type: ignore
except Exception:  # pragma: no cover
    feedparser = None  # type: ignore

CATEGORIES_AND_QUERIES: Dict[str, str] = {
    "Political News": "(politics OR election OR legislation OR regulatory OR geopolitical)",
    "World News": "(global OR world OR conflict OR treaty OR \"trade agreement\" OR \"policy change\")",
    "U.S. News": "(United States OR U.S. OR US) AND (economy OR \"Federal Reserve\" OR CPI OR unemployment OR inflation)",
    "Technology News": "(technology OR AI OR cybersecurity OR semiconductor OR chip OR \"product launch\" OR merger)",
    "Trending Infrastructure & Energy News": "(infrastructure OR \"renewable energy\" OR oil OR gas OR transportation OR \"power grid\")",
    "Market-Relevant Trends": "(consumer trend OR earnings OR outlook OR guidance OR demand OR revenue)",
}

RSS_FEEDS_BY_CATEGORY: Dict[str, List[str]] = {
    "Political News": [
        "https://feeds.a.dj.com/rss/RSSOpinion.xml",
        "https://www.politico.com/rss/politics08.xml",
    ],
    "World News": [
        "https://feeds.bbci.co.uk/news/world/rss.xml",
        "https://www.reutersagency.com/feed/?best-topics=world&post_type=best",
    ],
    "U.S. News": [
        "https://feeds.bbci.co.uk/news/world/us_and_canada/rss.xml",
        "https://www.reutersagency.com/feed/?best-topics=us&post_type=best",
    ],
    "Technology News": [
        "https://www.reutersagency.com/feed/?best-topics=technology&post_type=best",
        "https://feeds.arstechnica.com/arstechnica/index",
    ],
    "Trending Infrastructure & Energy News": [
        "https://www.reutersagency.com/feed/?best-topics=energy&post_type=best",
        "https://www.reutersagency.com/feed/?best-topics=business&post_type=best",
    ],
    "Market-Relevant Trends": [
        "https://www.reutersagency.com/feed/?best-topics=markets&post_type=best",
        "https://www.ft.com/companies?format=rss",
    ],
}


class NewsFetcher:
    def __init__(self, api_key: str | None = None) -> None:
        self.api_key = api_key or os.getenv("NEWSAPI_KEY")

    def is_configured(self) -> bool:
        return bool(self.api_key)

    def fetch_context(self, per_category: int = 4, lookback_days: int = 2) -> str:
        if self.is_configured():
            return self._fetch_via_newsapi(per_category=per_category, lookback_days=lookback_days)
        return self._fetch_via_rss(per_category=per_category)

    def _fetch_via_newsapi(self, per_category: int, lookback_days: int) -> str:
        base_url = "https://newsapi.org/v2/everything"
        from datetime import datetime, timedelta
        from_param = (datetime.utcnow() - timedelta(days=lookback_days)).strftime("%Y-%m-%dT%H:%M:%SZ")
        sections: List[str] = []
        for category, query in CATEGORIES_AND_QUERIES.items():
            params = {
                "q": query,
                "language": "en",
                "from": from_param,
                "sortBy": "publishedAt",
                "pageSize": per_category,
            }
            resp = requests.get(base_url, params=params, headers={"X-Api-Key": self.api_key}, timeout=20)
            if resp.status_code != 200:
                continue
            data = resp.json()
            articles = data.get("articles", [])
            if not articles:
                continue
            lines: List[str] = [f"{category}:"]
            for a in articles[:per_category]:
                title = a.get("title") or "Untitled"
                source = (a.get("source") or {}).get("name") or "Unknown"
                url = a.get("url") or ""
                published_at = a.get("publishedAt") or ""
                lines.append(f"- {title} ({source}, {published_at}) — {url}")
            sections.append("\n".join(lines))
        return "\n\n".join(sections)

    def _fetch_via_rss(self, per_category: int) -> str:
        if feedparser is None:
            return ""
        sections: List[str] = []
        for category, feeds in RSS_FEEDS_BY_CATEGORY.items():
            lines: List[str] = [f"{category}:"]
            added = 0
            for url in feeds:
                try:
                    parsed = feedparser.parse(url)
                except Exception:
                    continue
                for entry in parsed.entries[: per_category * 2]:
                    title = getattr(entry, "title", None) or "Untitled"
                    link = getattr(entry, "link", None) or ""
                    published = getattr(entry, "published", getattr(entry, "updated", ""))
                    lines.append(f"- {title} ({published}) — {link}")
                    added += 1
                    if added >= per_category:
                        break
                if added >= per_category:
                    break
            if added > 0:
                sections.append("\n".join(lines))
        return "\n\n".join(sections) 