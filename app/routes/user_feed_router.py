from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models import User, RSSFeed, UserFeedAssociation
from app.schemas.rss_feed import UserFeedAssociationOut, UserFeedAssociationCreate, FeedFilter
from app.services.auth import get_current_user
from app.crud.user import get_user_by_id

router = APIRouter(tags=["User Feeds"])

# Lier un flux à un utilisateur
@router.post("/{user_id}/feeds/{feed_id}/link", response_model=UserFeedAssociationOut)
def link_feed_to_user(
    user_id: int,
    feed_id: int,
    link_data: UserFeedAssociationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Accès interdit : vous ne pouvez lier des flux que pour vous-même.")

    feed = db.query(RSSFeed).filter_by(id=feed_id).first()
    if not feed:
        raise HTTPException(status_code=404, detail="Flux non trouvé")

    user = get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")

    association = db.query(UserFeedAssociation).filter_by(
        user_id=user_id, feed_id=feed_id
    ).first()

    if association:
        # Mise à jour de l'association existante
        association.is_active = link_data.is_active
    else:
        # Créer une nouvelle association
        association = UserFeedAssociation(
            user_id=user_id,
            feed_id=feed_id,
            is_active=link_data.is_active
        )
        db.add(association)

    db.commit()
    db.refresh(association)
    return association

# Obtenir tous les flux associés à un utilisateur
@router.get("/{user_id}/feeds", response_model=List[UserFeedAssociationOut])
def get_user_feeds(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Accès interdit")

    associations = db.query(UserFeedAssociation).filter_by(user_id=user_id).all()
    return associations

# Filtrer les flux associés à un utilisateur
@router.post("/{user_id}/feeds/filter", response_model=List[UserFeedAssociationOut])
def filter_user_feeds(
    user_id: int,
    filters: FeedFilter,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Accès interdit")

    query = db.query(UserFeedAssociation).join(RSSFeed).filter(UserFeedAssociation.user_id == user_id)

    # Appliquer les filtres selon les critères
    if filters.source_name:
        query = query.filter(RSSFeed.source_name == filters.source_name)
    if filters.tags:
        query = query.filter(RSSFeed.tags.contains(filters.tags))
    if filters.active is not None:
        query = query.filter(UserFeedAssociation.is_active == filters.active)
    if filters.search_text:
        query = query.filter(RSSFeed.title.ilike(f"%{filters.search_text}%"))

    return query.all()

# Obtenir tous les flux de l'utilisateur connecté
@router.get("/me/feeds", response_model=List[UserFeedAssociationOut])
def get_my_feeds(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    associations = db.query(UserFeedAssociation).filter_by(user_id=current_user.id).all()
    return associations
