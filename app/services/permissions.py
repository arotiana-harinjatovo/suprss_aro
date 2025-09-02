from sqlalchemy.orm import Session
from app.models import Collection,  CollectionMember, CollectionPermission
from fastapi import HTTPException
from app.schemas.collection import UserPermissions, CollectionRole


def get_user_permissions_for_collection(db, collection, user):
    # Si l'utilisateur est le créateur
    if collection.creator_id == user.id:
        return UserPermissions(
            is_creator=True,
            can_add_feed=True,
            can_read=True,
            can_comment=True,
            role=CollectionRole.creator,
            user_id=user.id,
        )

    # Sinon on regarde s'il est membre
    member = db.query(CollectionMember).filter_by(
        collection_id=collection.id,
        user_id=user.id
    ).first()

    # On récupère ses permissions spécifiques si elles existent
    permission = db.query(CollectionPermission).filter_by(
        collection_id=collection.id,
        user_id=user.id
    ).first()

    # On renvoie les permissions, sinon on met des permissions par défaut pour viewer
    return UserPermissions(
        is_creator=False,
        can_add_feed=permission.can_add_feed if permission else False,
        can_read=permission.can_read if permission else False,
        can_comment=permission.can_comment if permission else False,
        role=member.role if member else CollectionRole.viewer,
        user_id=user.id,
    )


def get_user_permissions(db: Session, collection_id: int, user_id: int):
    member = db.query(CollectionMember).filter_by(
        collection_id=collection_id,
        user_id=user_id
    ).first()

    permission = db.query(CollectionPermission).filter_by(
        collection_id=collection_id,
        user_id=user_id
    ).first()

    return {
        "is_creator": member.role == "creator",
        "can_add_feed": permission.can_add_feed if permission else False,
        "can_read": permission.can_read if permission else False,
        "can_comment": permission.can_comment if permission else False,
        "role": member.role if member else "unknown"
    }


def is_creator(collection: Collection, user_id: int) -> bool:
    return collection.creator_id == user_id

def get_permissions_for_role(role: str) -> dict:
    if role == "creator":
        return {
            "can_add_feed": True,
            "can_read": True,
            "can_comment": True
        }
    elif role == "editor":
        return {
            "can_add_feed": True,
            "can_read": True,
            "can_comment": True
        }
    elif role == "viewer":
        return {
            "can_add_feed": False,
            "can_read": True,
            "can_comment": False
        }
    else:
        # Valeurs par défaut si le rôle est inconnu
        return {
            "can_add_feed": False,
            "can_read": False,
            "can_comment": False
        }

def get_collection_members_with_permissions(db: Session, collection_id: int):
    """
    Retourne la liste des membres d'une collection avec leurs permissions et leur rôle.
    """
    collection = db.query(Collection).filter(Collection.id == collection_id).first()
    if not collection:
        raise HTTPException(status_code=404, detail="Collection non trouvée")

    permissions = db.query(CollectionPermission).filter_by(collection_id=collection_id).all()
    members = db.query(CollectionMember).filter_by(collection_id=collection_id).all()

    # Créer un dictionnaire des rôles par user_id
    roles_by_user = {member.user_id: member.role for member in members}

    result = []
    for perm in permissions:
        result.append({
            "user_id": perm.user_id,
            "is_creator": perm.user_id == collection.creator_id,
            "role": roles_by_user.get(perm.user_id, "member"),
            "can_add_feed": perm.can_add_feed,
            "can_read": perm.can_read,
            "can_comment": perm.can_comment
        })
    return result


def user_has_access_to_collection(db: Session, collection_id: int, user_id: int) -> bool:
    collection = db.query(Collection).filter(Collection.id == collection_id).first()
    if not collection:
        return False

    # Le créateur a toujours accès
    if collection.creator_id == user_id:
        return True

    # Vérifie s'il a des permissions explicites
    has_permission = db.query(CollectionPermission).filter_by(
        collection_id=collection_id,
        user_id=user_id
    ).first()

    return has_permission is not None


def user_can_modify_collection(db: Session, collection_id: int, user_id: int) -> bool:
    collection = db.query(Collection).filter(Collection.id == collection_id).first()
    if not collection:
        return False
    if collection.creator_id == user_id:
        return True
    permission = db.query(CollectionPermission).filter_by(collection_id=collection_id, user_id=user_id).first()
    return permission and permission.can_add_feed
