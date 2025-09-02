from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from app.database import get_db
from app.services.auth import get_current_user

# CRUD
from app.crud import rss_feed as crud_feed
from app.crud import rss_article as crud_rss

# Modèles
from app.models import RSSFeed, UserArticleAssociation, UserFeedAssociation

# Schémas
from app.schemas.rss_feed import  RSSFeedOut,  UserFeedAssociationOut, UserFeedAssociationCreate, UserFeedAssociationUpdate
from app.schemas.rss_article import RSSArticleCreate, RSSArticleOut

# Lecture du flux
from app.routes.reader import fetch_rss_feed

router = APIRouter(prefix="/feeds", tags=["Flux RSS"])

# ------------------ Création d'un flux RSS ------------------ #


@router.post("/", response_model=UserFeedAssociationOut)
def create_rss_feed(
    feed: UserFeedAssociationCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    # Récupérer et analyser le flux RSS
    parsed = fetch_rss_feed(feed.url, limit=feed.article_limit)

    # Si le titre n'est pas fourni, on utilise celui du flux
    if not feed.title:
        feed.title = parsed["feed_title"]

    # Créer ou associer le flux RSS
    db_feed = crud_feed.create_or_associate_feed(db, current_user.id, feed)

    # Créer ou associer les articles à l'utilisateur
    for entry in parsed["articles"]:
        article_data = RSSArticleCreate(
            title=entry["title"],
            link=entry["link"],
            published_at=entry["published"],
            summary=entry["summary"],
            source_name=parsed["feed_title"],
            feed_id=db_feed.id,
            tags=feed.tags,
            user_id=current_user.id,
        )

        # Vérifie si l'article existe déjà
        article = crud_rss.get_article_by_link(db, article_data.link)
        if not article:
            article = crud_rss.create_article(db, article_data)

        # Vérifie si l'association utilisateur-article existe
        existing_association = db.query(UserArticleAssociation).filter_by(
            user_id=current_user.id,
            article_id=article.id
        ).first()

        if not existing_association:
            db.add(UserArticleAssociation(article_id=article.id, user_id=current_user.id))

    db.commit()

    # Récupérer l'association utilisateur-flux avec les infos du flux
    user_feed_association = (
        db.query(UserFeedAssociation)
        .options(joinedload(UserFeedAssociation.feed))
        .filter_by(user_id=current_user.id, feed_id=db_feed.id)
        .first()
    )

    if not user_feed_association:
        raise HTTPException(status_code=404, detail="User association not found for this feed")

    return user_feed_association



# ------------------ Liste des flux RSS ------------------ #

@router.get("/", response_model=list[UserFeedAssociationOut])
def list_rss_feeds(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    return crud_feed.get_all_feeds(db, current_user.id)

# ------------------ Mise à jour d'un flux RSS ------------------ #

@router.put("/{feed_id}", response_model=UserFeedAssociationOut)
def update_rss_feed(
    feed_id: int,
    feed_update: UserFeedAssociationUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    return crud_feed.update_user_feed_association(
        db=db,
        user_id=current_user.id,
        feed_id=feed_id,
        update_data=feed_update
    )


# ------------------ Suppression d'un flux RSS ------------------ #

@router.delete("/{feed_id}")
def delete_rss_feed(
    feed_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    db_feed = crud_feed.get_feed_by_id(db, feed_id, current_user.id)
    if not db_feed:
        raise HTTPException(status_code=404, detail="Flux RSS non trouvé ou accès refusé")

    crud_feed.delete_feed(db, feed_id, current_user.id)
    return {"message": "Flux RSS dissocié de votre compte"}


# ------------------ Articles liés à un flux RSS ------------------ #

@router.get("/{feed_id}/articles", response_model=list[RSSArticleOut])
def get_articles_by_feed(
    feed_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    db_feed = crud_feed.get_feed_by_id(db, feed_id, current_user.id)
    if not db_feed:
        raise HTTPException(status_code=404, detail="Flux RSS non trouvé")
    return crud_rss.get_articles_by_feed(db, feed_id)

# ------------------ Informations sur un flux RSS ------------------ #

@router.get("/{feed_id}", response_model=RSSFeedOut)
def get_feed_by_id(
    feed_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    db_feed = crud_feed.get_feed_by_id(db, feed_id, current_user.id)
    if not db_feed:
        raise HTTPException(status_code=404, detail="Flux RSS non trouvé")
    return db_feed
