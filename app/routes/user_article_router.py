from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models import User, RSSArticle, UserArticleAssociation
from app.schemas.rss_article import UserArticleLinkCreate, UserArticleAssociationOut, ArticleFilter
from app.services.auth import get_current_user
from app.crud.user import get_user_by_id

router = APIRouter(tags=["User Articles"])

@router.post("/{user_id}/articles/{article_id}/link", response_model=UserArticleAssociationOut)
def link_article_to_user(
    user_id: int,
    article_id: int,
    link_data: UserArticleLinkCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Accès interdit : vous ne pouvez lier des articles que pour vous-même.")

    article = db.query(RSSArticle).filter_by(id=article_id).first()
    if not article:
        raise HTTPException(status_code=404, detail="Article non trouvé")

    user = get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")

    association = db.query(UserArticleAssociation).filter_by(
        user_id=user_id, article_id=article_id
    ).first()

    if association:
        association.is_read = link_data.is_read
        association.is_favorite = link_data.is_favorite
    else:
        association = UserArticleAssociation(
            user_id=user_id,
            article_id=article_id,
            is_read=link_data.is_read,
            is_favorite=link_data.is_favorite
        )
        db.add(association)

    db.commit()
    db.refresh(association)
    return association


@router.post("/{user_id}/articles/filter", response_model=List[UserArticleAssociationOut])
def filter_user_articles(
    user_id: int,
    filters: ArticleFilter,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Accès interdit")

    query = db.query(UserArticleAssociation).join(RSSArticle).filter(UserArticleAssociation.user_id == user_id)

    if filters.source_name:
        query = query.filter(RSSArticle.source_name == filters.source_name)
    if filters.tags:
        query = query.filter(RSSArticle.tags.contains(filters.tags))
    if filters.favorite is not None:
        query = query.filter(UserArticleAssociation.is_favorite == filters.favorite)
    if filters.status == "read":
        query = query.filter(UserArticleAssociation.is_read == True)
    elif filters.status == "unread":
        query = query.filter(UserArticleAssociation.is_read == False)
    if filters.search_text:
        query = query.filter(RSSArticle.title.ilike(f"%{filters.search_text}%"))

    return query.all()



@router.put("/articles/{article_id}/read", response_model=UserArticleAssociationOut)
def mark_article_as_read(
    article_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    association = db.query(UserArticleAssociation).filter_by(user_id=current_user.id, article_id=article_id).first()
    if not association:
        association = UserArticleAssociation(user_id=current_user.id, article_id=article_id, is_read=True)
        db.add(association)
    else:
        association.is_read = True

    db.commit()
    db.refresh(association)
    return association



@router.put("/articles/{article_id}/favorite", response_model=UserArticleAssociationOut)
def mark_article_as_favorite(
    article_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    association = db.query(UserArticleAssociation).filter_by(user_id=current_user.id, article_id=article_id).first()
    if not association:
        association = UserArticleAssociation(user_id=current_user.id, article_id=article_id, is_favorite=True)
        db.add(association)
    else:
        association.is_favorite = not association.is_favorite

    db.commit()
    db.refresh(association)
    return association
