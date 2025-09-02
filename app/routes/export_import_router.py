from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from fastapi.responses import FileResponse
from typing import List
from sqlalchemy.orm import Session
import json, csv, xml.etree.ElementTree as ET
import os
from sqlalchemy.exc import IntegrityError
from tempfile import NamedTemporaryFile
from app.services.auth import get_current_user
from app.database import get_db
from app.models import RSSFeed, User, RSSArticle, UserFeedAssociation, UserArticleAssociation
from app.models import User, RSSFeed
from app.routes.reader import fetch_rss_feed  

router = APIRouter(tags=["Export Import"])

# ----------- EXPORT -----------


@router.get("/export", response_class=FileResponse)
def export_feeds(format: str = "json", db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    # Récupération des associations utilisateur-flux
    user_feeds = (
        db.query(UserFeedAssociation)
        .join(RSSFeed, UserFeedAssociation.feed_id == RSSFeed.id)
        .filter(UserFeedAssociation.user_id == current_user.id)
        .all()
    )

    # Création du fichier temporaire selon le format
    if format == "json":
        tmp = NamedTemporaryFile(delete=False, suffix=".json", mode="w", encoding="utf-8")
        json.dump([{
            "title": f.title,
            "url": f.feed.url,
            "description": f.description,
            "tags": f.tags,
            "update_frequency": f.update_frequency,
            "is_active": f.is_active,
            "is_shared": f.is_shared,
            "article_limit": f.article_limit
        } for f in user_feeds], tmp, indent=2)

    elif format == "csv":
        tmp = NamedTemporaryFile(delete=False, suffix=".csv", mode="w", encoding="utf-8", newline="")
        writer = csv.DictWriter(tmp, fieldnames=[
            "title", "url", "description", "tags", "update_frequency", "is_active", "is_shared", "article_limit"
        ])
        writer.writeheader()
        for f in user_feeds:
            writer.writerow({
                "title": f.title,
                "url": f.feed.url,
                "description": f.description,
                "tags": ', '.join(f.tags) if f.tags else '',
                "update_frequency": f.update_frequency,
                "is_active": f.is_active,
                "is_shared": f.is_shared,
                "article_limit": f.article_limit
            })

    elif format == "opml":
        tmp = NamedTemporaryFile(delete=False, suffix=".opml", mode="w", encoding="utf-8")
        root = ET.Element("opml", version="1.0")
        head = ET.SubElement(root, "head")
        ET.SubElement(head, "title").text = "Export RSS"
        body = ET.SubElement(root, "body")
        for f in user_feeds:
            ET.SubElement(body, "outline", text=f.title, title=f.title, type="rss", xmlUrl=f.feed.url)
        tree = ET.ElementTree(root)
        tree.write(tmp.name, encoding="utf-8", xml_declaration=True)

    else:
        raise HTTPException(status_code=400, detail="Format non supporté")

    tmp.close()
    return FileResponse(tmp.name, filename=f"rss_export.{format}", media_type="application/octet-stream")

# ----------- IMPORT -----------
@router.post("/import")
async def import_feeds(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    content = await file.read()
    imported = []
    skipped = []
    seen_urls = set()

    def create_feed(data: dict):
        url = data.get("url")
        title = data.get("title") or "Sans titre"
        if not url:
            skipped.append("URL manquante")
            return

        if url in seen_urls:
            skipped.append(f"Doublon URL ignorée: {url}")
            return
        seen_urls.add(url)

        # Vérifie si le flux existe déjà
        feed = db.query(RSSFeed).filter(RSSFeed.url == url).first()
        if not feed:
            feed = RSSFeed(url=url)
            db.add(feed)
            db.flush()

        # Vérifie si l'association utilisateur-flux existe
        existing_association = db.query(UserFeedAssociation).filter_by(
            user_id=current_user.id,
            feed_id=feed.id
        ).first()

        if existing_association:
            skipped.append(f"Association existante ignorée: {url}")
            return

        # Crée l'association personnalisée
        association = UserFeedAssociation(
            user_id=current_user.id,
            feed_id=feed.id,
            title=title,
            description=data.get("description"),
            tags=data.get("tags", []),
            update_frequency=data.get("update_frequency", "daily"),
            is_active=data.get("is_active", True),
            is_shared=data.get("is_shared", False),
            article_limit=data.get("article_limit", 5)
        )
        db.add(association)
        db.flush()

        # Récupération des articles
        try:
            articles_data = fetch_rss_feed(url, limit=association.article_limit)
            print(f"Import {len(articles_data['articles'])} articles pour {url}")

            existing_links = set(
                a.link for a in db.query(RSSArticle).filter(RSSArticle.feed_id == feed.id).all()
            )

            for article in articles_data["articles"]:
                if article["link"] in existing_links:
                    continue

                rss_article = RSSArticle(
                    title=article["title"],
                    link=article["link"],
                    summary=article.get("summary"),
                    published_at=article.get("published"),
                    tags=association.tags,
                    source_name=association.title,
                    feed_id=feed.id
                )
                db.add(rss_article)
                db.flush()

                # Crée l'association utilisateur-article
                user_article_link = UserArticleAssociation(
                    user_id=current_user.id,
                    article_id=rss_article.id,
                    is_read=False,
                    is_favorite=False
                )
                db.add(user_article_link)

        except Exception as e:
            skipped.append(f"Articles non récupérés pour {url} : {str(e)}")

        imported.append(association)

    # Gestion des formats
    try:
        if file.filename.endswith(".json"):
            feeds = json.loads(content)
            for f in feeds:
                create_feed(f)

        elif file.filename.endswith(".csv"):
            decoded = content.decode('utf-8')
            reader = csv.DictReader(decoded.splitlines())
            for row in reader:
                create_feed(row)

        elif file.filename.endswith(".opml") or file.filename.endswith(".xml"):
            root = ET.fromstring(content)
            for outline in root.findall(".//outline"):
                url = outline.attrib.get("xmlUrl") or outline.attrib.get("url")
                if url:
                    data = {
                        "url": url,
                        "title": outline.attrib.get("title") or outline.attrib.get("text"),
                    }
                    create_feed(data)
        else:
            raise HTTPException(status_code=400, detail="Format de fichier non supporté")

        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Erreur à la sauvegarde : {str(e)}")

    return {
        "message": f"{len(imported)} flux ajoutés, {len(skipped)} ignorés.",
        "imported": [f.title for f in imported],
        "skipped": skipped
    }

