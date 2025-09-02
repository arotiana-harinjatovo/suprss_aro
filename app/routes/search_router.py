from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import cast, String
from app.database import get_db
from app.models.rss_article import RSSArticle
from app.models.collection import Collection
from app.models.rss_feed import RSSFeed  
router = APIRouter(tags=["Search"])


@router.get("/search")
def search_items(q: str = Query(..., min_length=1), db: Session = Depends(get_db)):
    articles = (
        db.query(RSSArticle)
        .join(RSSFeed, RSSArticle.feed_id == RSSFeed.id)
        .options(joinedload(RSSArticle.rss_feed))
        .filter(
            RSSArticle.title.ilike(f"%{q}%") |
            cast(RSSArticle.tags, String).ilike(f"%{q}%") |
            RSSFeed.url.ilike(f"%{q}%")
        )
        .all()
    )

    collections = db.query(Collection).filter(Collection.name.ilike(f"%{q}%")).all()

    article_results = [
        {
            "id": a.id,
            "title": a.title,
            "feed_name": a.rss_feed.url if a.rss_feed else None,
            "tags": a.tags if isinstance(a.tags, list) else [],
            "link": a.link,
            "type": "article"
        }
        for a in articles
    ]

    collection_results = [
        {"id": c.id, "title": c.name, "type": "collection"}
        for c in collections
    ]

    return {
        "articles": article_results,
        "collections": collection_results
    }
