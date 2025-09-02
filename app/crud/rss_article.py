from typing import List, Optional
from sqlalchemy.orm import Session

from sqlalchemy.orm import aliased
from sqlalchemy import or_

from app.models import RSSArticle, CollectionArticle, Collection, UserArticleAssociation, CollectionUserAssociation
from app.models.rss_article import RSSArticle
from app.schemas.rss_article import RSSArticleCreate, ArticleFilter
from fastapi import HTTPException


def create_article(db: Session, article: RSSArticleCreate):
    db_article = RSSArticle(
        title=article.title,
        link=article.link,
        published_at=article.published_at,
        summary=article.summary,
        source_name=article.source_name,
        feed_id=article.feed_id,  
        tags=article.tags
    )
    db.add(db_article)
    db.commit()
    db.refresh(db_article)
    return db_article


def get_article_by_link(db: Session, link: str):
    return db.query(RSSArticle).filter(RSSArticle.link == link).first()

def get_articles_by_feed(db: Session, feed_id: int):
    return db.query(RSSArticle).filter(RSSArticle.feed_id == feed_id).all()

def filter_articles_in_collection(
    db: Session,
    collection_id: Optional[int],
    filters: ArticleFilter,
    user_id: int
) -> List[RSSArticle]:
    # Alias pour éviter les conflits
    assoc = aliased(UserArticleAssociation)

    # Base de la requête
    query = db.query(RSSArticle).join(assoc, RSSArticle.id == assoc.article_id).filter(assoc.user_id == user_id)

    # Filtrage par collection
    if collection_id is not None:
        collection = db.query(Collection).filter(Collection.id == collection_id).first()
        if not collection:
            raise HTTPException(status_code=404, detail="Collection introuvable")
        if not collection.is_shared and collection.owner_id != user_id:
            raise HTTPException(status_code=403, detail="Accès interdit à cette collection")

        query = query.join(CollectionArticle).filter(CollectionArticle.collection_id == collection_id)

    # Filtres sur les champs de l'article
    if filters.source_name:
        query = query.filter(RSSArticle.source_name == filters.source_name)

    if filters.tags:
        query = query.filter(RSSArticle.tags.overlap(filters.tags))

    if filters.search_text:
        search = f"%{filters.search_text}%"
        query = query.filter(or_(
            RSSArticle.title.ilike(search),
            RSSArticle.description.ilike(search),
            RSSArticle.content.ilike(search),
            RSSArticle.source_name.ilike(search),
            RSSArticle.summary.ilike(search)
        ))

    # Filtres sur les statuts utilisateur
    if filters.status == "read":
        query = query.filter(assoc.is_read == True)
    elif filters.status == "unread":
        query = query.filter(assoc.is_read == False)

    if filters.favorite is not None:
        query = query.filter(assoc.is_favorite == filters.favorite)

    return query.all()

def get_accessible_articles(db: Session, user_id: int) -> List[RSSArticle]:
    # Articles associés directement
    direct_articles = db.query(RSSArticle).join(UserArticleAssociation).filter(UserArticleAssociation.user_id == user_id)

    # Articles dans les collections où l'utilisateur est membre
    collection_articles = db.query(RSSArticle).join(CollectionArticle).join(CollectionUserAssociation).filter(
        CollectionUserAssociation.user_id == user_id
    )

    # Union des deux requêtes
    return direct_articles.union(collection_articles).distinct().all()
