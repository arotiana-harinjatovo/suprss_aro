from sqlalchemy.orm import Session
from app.models import Notification, Collection, CollectionMember
from datetime import datetime

# Crée une notification lorsqu'un utilisateur est invité à une collection.

def notify_collection_invite(
    db: Session,
    requester_id: int,
    receiver_id: int,
    collection_id: int
):
    
    collection = db.query(Collection).filter_by(id=collection_id).first()
    if not collection:
        return None

    message = f"Vous avez été invité à rejoindre la collection « {collection.name} »."
    notification = Notification(
        requester_id=requester_id,
        receiver_id=receiver_id,
        type="collection_invite",
        message=message,
        collection_id=collection_id,
        timestamp=datetime.utcnow()
    )
    db.add(notification)
    db.commit()
    return notification

# Crée des notifications pour les membres d'une collection lorsqu'un commentaire est ajouté.

def notify_collection_comment(
    db: Session,
    requester_id: int,
    collection_id: int,
    comment_id: int,
    receivers: list[int]
):
    collection = db.query(Collection).filter_by(id=collection_id).first()
    if not collection:
        return None

    message = f"Nouveau commentaire dans la collection « {collection.name} »."
    notifications = []

    for receiver_id in receivers:
        if receiver_id == requester_id:
            continue

        notification = Notification(
            requester_id=requester_id,
            receiver_id=receiver_id,
            type="collection_comment",
            message=message,
            collection_id=collection_id,
            comment_id=comment_id,
            timestamp=datetime.utcnow()
        )
        db.add(notification)
        notifications.append(notification)

    db.commit()
    return notifications


