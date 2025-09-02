from sqlalchemy.orm import Session
from app.models import (
    User, CollectionMessage, Comment,
    UserArticleAssociation, UserFeedAssociation,
    Friendship, Follow, Collection, CollectionPermission,
    Notification, CollectionUserAssociation, CollectionMember
    )
from sqlalchemy import select
from app.schemas import user as user_schema
from passlib.context import CryptContext
from pydantic import ValidationError
from app.services.security import get_password_hash

# Pour le hash du mot de passe
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_user(db: Session, user_id: int):
    return db.query(User).filter(User.id == user_id).first()

def get_user_by_identifier(db: Session, identifier: str):
    try:
        user_schema.EmailCheck(email=identifier)
        return db.query(User).filter(User.email == identifier).first()
    except ValidationError:
        return db.query(User).filter(User.username == identifier).first()

def get_user_by_id(db: Session, user_id: int):
    return db.query(User).filter(User.id == user_id).first()

def get_users(db: Session, skip: int = 0, limit: int = 10):
    return db.query(User).offset(skip).limit(limit).all()

def create_user(db: Session, user: user_schema.UserCreate):
    hashed_password = pwd_context.hash(user.password)
    db_user = User(
        username=user.username,
        full_name=user.full_name,
        email=user.email,
        hashed_password=hashed_password,
        is_active=True
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def delete_user(db: Session, user_id: int):
    # Supprimer les notifications liées à l'utilisateur
    db.query(Notification).filter(
        (Notification.requester_id == user_id) | 
        (Notification.receiver_id == user_id)
    ).delete()

    # Supprimer les notifications liées aux relations d’amitié
    friendship_ids = db.query(Friendship.id).filter(
        (Friendship.requester_id == user_id) | (Friendship.receiver_id == user_id)
    ).subquery()
    db.query(Notification).filter(Notification.friendship_id.in_(select(friendship_ids))).delete()

    # Supprimer les messages dans les collections
    db.query(CollectionMessage).filter(CollectionMessage.user_id == user_id).delete()

    # Supprimer les commentaires
    db.query(Comment).filter(Comment.user_id == user_id).delete()

    # Supprimer les abonnements à des flux RSS
    db.query(UserFeedAssociation).filter(UserFeedAssociation.user_id == user_id).delete()

    # Supprimer les associations d'articles
    db.query(UserArticleAssociation).filter(UserArticleAssociation.user_id == user_id).delete()

    # Supprimer les relations d’amis
    db.query(Friendship).filter(
        (Friendship.requester_id == user_id) | (Friendship.receiver_id == user_id)
    ).delete()

    # Supprimer les abonnements (follow)
    db.query(Follow).filter(
        (Follow.follower_id == user_id) | (Follow.followed_id == user_id)
    ).delete()

    # Supprimer les invitations d’amis (si modèle séparé)
    db.query(Friendship).filter(
        (Friendship.requester_id == user_id) | (Friendship.receiver_id == user_id)
    ).delete()

    # Supprimer les collections créées par l'utilisateur
    db.query(Collection).filter(Collection.creator_id == user_id).delete()

    # Supprimer les permissions et associations de collections
    db.query(CollectionPermission).filter(CollectionPermission.user_id == user_id).delete()
    db.query(CollectionUserAssociation).filter(CollectionUserAssociation.user_id == user_id).delete()
    db.query(CollectionMember).filter(CollectionMember.user_id == user_id).delete()

    # Supprimer l'utilisateur
    user = db.query(User).filter(User.id == user_id).first()
    if user:
        db.delete(user)
        db.commit()
        return user
    return None




def update_user(db: Session, user: User, updates: user_schema.UserUpdate):
    # Vérifie les champs à mettre à jour
    if updates.full_name is not None:
        user.full_name = updates.full_name
    if updates.email is not None:
        # Vérifie si l'email est déjà utilisé par un autre utilisateur
        existing_user = db.query(User).filter(User.email == updates.email, User.id != user.id).first()
        if existing_user:
            raise ValidationError("Cet e-mail a déjà été utilisé.")
        user.email = updates.email
    if updates.password is not None:
        user.hashed_password = get_password_hash(updates.password)

    db.commit()
    db.refresh(user)
    return user

def has_read_article(self, article_id):
    return any(assoc.article_id == article_id and assoc.is_read for assoc in self.article_associations)

def has_favorited_article(self, article_id):
    return any(assoc.article_id == article_id and assoc.is_favorite for assoc in self.article_associations)
