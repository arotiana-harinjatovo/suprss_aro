from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.services.auth import get_current_user
from app.crud import rss_article as crud_rss
from app.models import RSSArticle, RSSFeed, UserFeedAssociation, UserArticleAssociation
from app.schemas.rss_article import RSSArticleOut, RSSArticleCreate, ArticleFilter, UserArticleAssociationOut

router = APIRouter(prefix="/articles", tags=["Articles RSS"])

# ----------- Créer un article manuellement ----------- 
@router.post("/", response_model=RSSArticleOut)
def create_article(
    article_data: RSSArticleCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    existing = crud_rss.get_article_by_link(db, article_data.link)
    if existing:
        raise HTTPException(status_code=400, detail="Article déjà existant")
    return crud_rss.create_article(db, article_data)

# ----------- Lister tous les articles avec user_id via jointure (avec association pour is_read et is_favorite) -----------
@router.get("/", response_model=List[UserArticleAssociationOut])
def list_articles(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    # Récupérer tous les articles des flux suivis par l'utilisateur
    articles = (
        db.query(RSSArticle)
        .join(RSSFeed, RSSArticle.feed_id == RSSFeed.id)
        .join(UserFeedAssociation, UserFeedAssociation.feed_id == RSSFeed.id)
        .filter(UserFeedAssociation.user_id == current_user.id)
        .order_by(RSSArticle.published_at.desc())
        .all()
    )

    result = []
    for article in articles:
        # Vérifie s'il existe une association utilisateur pour cet article
        association = db.query(UserArticleAssociation).filter_by(
            user_id=current_user.id,
            article_id=article.id
        ).first()

        result.append(UserArticleAssociationOut(
        user_id=current_user.id,
        is_read=association.is_read if association else False,
        is_favorite=association.is_favorite if association else False,
        article=RSSArticleOut(
            id=article.id,
            title=article.title,
            link=article.link,
            published_at=article.published_at,
            summary=article.summary,
            author=article.author,
            source_name=article.source_name,
            tags=article.tags,
            feed_id=article.feed_id
        )
))


    return result



# ----------- Filtrer les articles globalement -----------
@router.post("/filter", response_model=List[RSSArticleOut])
def filter_articles(
    filters: ArticleFilter,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    return crud_rss.filter_articles_in_collection(db, collection_id=None, filters=filters)

# ----------- Filtrer les articles dans une collection spécifique -----------
@router.post("/collection/{collection_id}/filter", response_model=List[RSSArticleOut])
def filter_articles_in_collection(
    collection_id: int,
    filters: ArticleFilter,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    return crud_rss.filter_articles_in_collection(db, collection_id, filters, current_user.id)

# ----------- Récupérer un article par son ID (avec gestion de l'association) -----------
@router.get("/{article_id}", response_model=RSSArticleOut)
def get_article_by_id(
    article_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    article = (
        db.query(RSSArticle, RSSFeed.user_id, RSSArticle.user_articles_associations)
        .join(RSSFeed, RSSArticle.feed_id == RSSFeed.id)
        .join(RSSArticle.user_articles_associations)
        .filter(RSSArticle.id == article_id)
        .first()
    )
    if not article:
        raise HTTPException(status_code=404, detail="Article non trouvé")

    article_obj, user_id, user_association = article
    if user_id != current_user.id and not RSSFeed.is_shared:
        raise HTTPException(status_code=403, detail="Accès interdit")

    is_read = user_association.is_read if user_association else False
    is_favorite = user_association.is_favorite if user_association else False

    return RSSArticleOut(
        id=article_obj.id,
        title=article_obj.title,
        link=article_obj.link,
        published_at=article_obj.published_at,
        summary=article_obj.summary,
        author=article_obj.author,
        is_read=is_read,
        is_favorite=is_favorite,
        source_name=article_obj.source_name,
        tags=article_obj.tags,
        feed_id=article_obj.feed_id,
        user_id=user_id
    )

# ----------- Supprimer un article (avec vérification d'accès via l'association)
@router.delete("/{article_id}")
def remove_user_article_association(
    article_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    association = db.query(UserArticleAssociation).filter_by(
        article_id=article_id,
        user_id=current_user.id
    ).first()

    if not association:
        raise HTTPException(status_code=404, detail="Association utilisateur-article introuvable")

    db.delete(association)
    db.commit()
    return {"detail": "Article retiré de votre vue"}

# ----------- Réassocier un article via un flux
@router.post("/{article_id}/reassociate")
def reassociate_article_to_user(
    article_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    # Vérifie que l'article existe
    article = db.query(RSSArticle).filter(RSSArticle.id == article_id).first()
    if not article:
        raise HTTPException(status_code=404, detail="Article introuvable")

    # Vérifie que l'association n'existe pas déjà
    existing = db.query(UserArticleAssociation).filter_by(
        article_id=article_id,
        user_id=current_user.id
    ).first()

    if existing:
        raise HTTPException(status_code=400, detail="L'article est déjà associé à vous.")

    # Crée une nouvelle association
    new_assoc = UserArticleAssociation(
        article_id=article_id,
        user_id=current_user.id,
        is_read=False,
        is_favorite=False
    )
    db.add(new_assoc)
    db.commit()

    return {"detail": "Article réassocié avec succès"}
