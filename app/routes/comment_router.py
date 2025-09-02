from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app import models, database
from app.schemas.comment import CommentOut, CommentCreate
from app.services.auth import get_current_user
from app.services.notifications import notify_collection_comment 
from sqlalchemy.orm import joinedload

router = APIRouter(prefix="/comments", tags=["Comments"])

# ------ Créer un commentaire ------ #

@router.post("/", response_model=CommentOut)
def create_comment(
    comment: CommentCreate, 
    db: Session = Depends(database.get_db), 
    current_user: models.User = Depends(get_current_user)
):
    # Création du commentaire
    db_comment = models.Comment(
        text=comment.text,
        article_id=comment.article_id,
        user_id=current_user.id
    )
    db.add(db_comment)
    db.commit()
    db.refresh(db_comment)

    #  Récupérer la collection liée à l'article via collection_articles
    
    link = db.query(models.CollectionArticle).filter_by(
        article_id=comment.article_id
    ).first()


    if link:
        collection_id = link.collection_id

        #  Récupérer les membres de la collection
        member_ids = db.query(models.CollectionMember.user_id).filter_by(
            collection_id=collection_id
        ).all()
        member_ids = [uid for (uid,) in member_ids if uid != current_user.id]

      
        notify_collection_comment(
            db=db,
            requester_id=current_user.id,
            collection_id=collection_id,
            comment_id=db_comment.id,
            receivers=member_ids
        )

    return db_comment



# ------ Lire un commentaire ------ #
@router.get("/article/{article_id}", response_model=list[CommentOut])
def get_comments(article_id: int, db: Session = Depends(database.get_db)):
    return (
        db.query(models.Comment)
        .options(joinedload(models.Comment.user))  
        .filter(models.Comment.article_id == article_id)
        .order_by(models.Comment.created_at.desc())
        .all()
    )

# ------ Supprimer un commentaire ------ #
@router.delete("/{comment_id}")
def delete_comment(comment_id: int, db: Session = Depends(database.get_db), current_user: models.User = Depends(get_current_user)):
    comment = db.query(models.Comment).filter(models.Comment.id == comment_id).first()
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")
    if comment.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this comment")
    db.delete(comment)
    db.commit()
    return {"detail": "Comment deleted"}
