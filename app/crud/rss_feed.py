from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.models import RSSFeed, UserFeedAssociation, RSSArticle
from app.schemas.rss_feed import UserFeedAssociationCreate, UserFeedAssociationUpdate
from sqlalchemy.orm import joinedload


def create_or_associate_feed(db: Session, user_id: int, feed_data: UserFeedAssociationCreate):
    # Vérifier si un flux avec la même URL existe déjà
    existing_feed = db.query(RSSFeed).filter(RSSFeed.url == feed_data.url).first()

    if not existing_feed:
        # Créer le flux uniquement avec l'URL
        existing_feed = RSSFeed(url=feed_data.url)
        db.add(existing_feed)
        db.flush()  # Pour récupérer l'ID sans commit immédiat

    # Vérifier si une association existe déjà
    existing_association = db.query(UserFeedAssociation).filter_by(
        user_id=user_id,
        feed_id=existing_feed.id
    ).first()

    if not existing_association:
        # Créer l'association avec les métadonnées personnalisées
        user_feed_association = UserFeedAssociation(
            user_id=user_id,
            feed_id=existing_feed.id,
            title=feed_data.title,
            description=feed_data.description,
            tags=feed_data.tags,
            update_frequency=feed_data.update_frequency,
            is_active=feed_data.is_active,
            is_shared=feed_data.is_shared,
            article_limit=feed_data.article_limit
        )
        db.add(user_feed_association)

    db.commit()
    db.refresh(existing_feed)
    return existing_feed


def get_all_feeds(db: Session, user_id: int):
    return (
        db.query(UserFeedAssociation)
        .options(joinedload(UserFeedAssociation.feed)) 
        .filter(
            (UserFeedAssociation.user_id == user_id) |
            (UserFeedAssociation.is_shared == True)
        )
        .all()
    )


def get_feeds_by_user(db: Session, user_id: int) -> list[RSSFeed]:
    return db.query(RSSFeed).filter(RSSFeed.user_id == user_id).all()


def get_feed_by_id(db: Session, feed_id: int, user_id: int) -> RSSFeed | None:
    association = db.query(UserFeedAssociation).filter_by(
        feed_id=feed_id,
        user_id=user_id
    ).first()

    if association and (association.user_id == user_id or association.is_shared):
        return association.feed

    return None


def get_feed_by_url(db: Session, url: str, user_id: int):
    return db.query(RSSFeed).filter(RSSFeed.url == url, RSSFeed.user_id == user_id).first()

def update_user_feed_association(
    db: Session,
    user_id: int,
    feed_id: int,
    update_data: UserFeedAssociationUpdate
) -> UserFeedAssociation:
    association = db.query(UserFeedAssociation).filter_by(
        user_id=user_id,
        feed_id=feed_id
    ).first()

    if not association:
        raise HTTPException(status_code=404, detail="Association not found")

    updated_fields = update_data.dict(exclude_unset=True)

    # Mise à jour des champs de l'association
    for field, value in updated_fields.items():
        setattr(association, field, value)

    # Si les tags ont été modifiés, mettre à jour ceux des articles liés au feed
    if "tags" in updated_fields:
        articles = db.query(RSSArticle).filter(RSSArticle.feed_id == feed_id).all()
        for article in articles:
            article.tags = updated_fields["tags"]  # ou fusionner si tu préfères

    db.commit()
    db.refresh(association)
    return association
