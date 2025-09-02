from celery import shared_task
from datetime import datetime, timedelta
from app.database import SessionLocal
from app.models import UserFeedAssociation
from app.routes.reader import fetch_rss_feed  

@shared_task
def update_rss_feeds():
    db = SessionLocal()
    now = datetime.utcnow()

    frequency_map = {
        "hourly": timedelta(hours=1),
        "6h": timedelta(hours=6),
        "daily": timedelta(days=1),
        "weekly": timedelta(weeks=1),
    }

    # Récupérer tous les flux actifs
    feeds = db.query(UserFeedAssociation).filter(
        UserFeedAssociation.is_active == True
    ).all()

    for feed_assoc in feeds:
        freq = feed_assoc.update_frequency
        delta = frequency_map.get(freq)

        # Vérifie si le flux doit être mis à jour
        if delta and (feed_assoc.last_updated is None or feed_assoc.last_updated <= now - delta):
            try:
                # Récupère l'URL du flux via la relation avec RSSFeed
                feed_url = feed_assoc.feed.url
                fetch_rss_feed(feed_url)  
                # Met à jour la date
                feed_assoc.last_updated = now
                db.commit()
                print(f"✅ Flux {feed_url} mis à jour.")
            except Exception as e:
                print(f"❌ Erreur pour le flux {feed_assoc.feed_id} : {e}")

    db.close()
