from sqlalchemy.orm import Session
from models.collection import Collection, CollectionPermission
from models.collection_members import CollectionMember
from models.user import User
from services.permissions import get_user_permissions, is_creator
from datetime import datetime

def get_default_permissions_for_role(role: str) -> dict:
    """
    Retourne les permissions par défaut selon le rôle.
    """
    role_permissions = {
        "creator": {
            "can_add_feed": True,
            "can_read": True,
            "can_comment": True
        },
        "editor": {
            "can_add_feed": True,
            "can_read": True,
            "can_comment": True
        },
        "viewer": {
            "can_add_feed": False,
            "can_read": True,
            "can_comment": False
        },
        "member": {
            "can_add_feed": False,
            "can_read": True,
            "can_comment": False
        }
    }
    return role_permissions.get(role, role_permissions["member"])

def invite_user_to_collection(
    db: Session,
    collection_id: int,
    inviter_id: int,
    invited_user_id: int,
    role: str = "member",
    default_permissions: dict = None
):
    """
    Invite un utilisateur à une collection si l'invitant a les droits.
    Ajoute l'utilisateur dans CollectionMember et crée une CollectionPermission.
    """

    # Vérifier que la collection existe
    collection = db.query(Collection).get(collection_id)
    if not collection:
        raise ValueError("Collection not found.")

    # Vérifier que l'invitant est le créateur ou a le droit d'ajouter des membres
    if not is_creator(collection, inviter_id):
        inviter_perm = get_user_permissions(db, collection_id, inviter_id)
        if not inviter_perm or not inviter_perm.can_add_feed:
            raise PermissionError("Inviter does not have permission to add members.")

    # Vérifier que l'utilisateur invité existe
    invited_user = db.query(User).get(invited_user_id)
    if not invited_user:
        raise ValueError("Invited user not found.")

    # Ajouter dans CollectionMember
    member_entry = CollectionMember(
        collection_id=collection_id,
        user_id=invited_user_id,
        role=role,
        joined_at=datetime.utcnow()
    )
    db.add(member_entry)

    # Ajouter dans CollectionPermission avec permissions par défaut
    if default_permissions is None:
        default_permissions = get_default_permissions_for_role(role)


    permission_entry = CollectionPermission(
        collection_id=collection_id,
        user_id=invited_user_id,
        can_add_feed=default_permissions["can_add_feed"],
        can_read=default_permissions["can_read"],
        can_comment=default_permissions["can_comment"]
    )
    db.add(permission_entry)

    db.commit()
    return {"message": "User invited successfully."}
