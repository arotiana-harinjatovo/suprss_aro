import feedparser
from email.utils import parsedate_to_datetime

def fetch_rss_feed(url: str, limit: int = 5):
    feed = feedparser.parse(url)
    articles = []

    for entry in feed.entries[:limit]:
        # Titre
        title = entry.get("title", "")

        # Lien
        link = entry.get("link", "")

        # Date de publication
        published_raw = entry.get("published", entry.get("updated", None))
        try:
            published = parsedate_to_datetime(published_raw) if published_raw else None
        except Exception:
            published = None

        # Résumé ou description
        summary = entry.get("summary", entry.get("description", ""))

        # Nettoyage pour YouTube (souvent trop de balises HTML)
        if "youtube.com" in url and summary:
            import re
            summary = re.sub(r"<[^>]+>", "", summary)  # Supprime les balises HTML

        articles.append({
            "title": title,
            "link": link,
            "published": published,
            "summary": summary
        })

    return {
        "feed_title": feed.feed.get("title", "Flux RSS"),
        "articles": articles
    }
