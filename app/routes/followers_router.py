from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime

from app.models import User, Friendship, Follow, Notification
from app.schemas.followers import (
    FriendshipCreate, FriendshipResponse,
    FollowCreate, FollowResponse,
    NotificationResponse
)
from app.services.auth import get_db, get_current_user
from app.schemas.user import UserOut

router = APIRouter(prefix="/followers", tags=["Followers"])

# -------------------- AMITIÉ --------------------

@router.post("/friend-request", response_model=FriendshipResponse)
def send_friend_request(
    request: FriendshipCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.id == request.receiver_id:
        raise HTTPException(status_code=400, detail="Erreur : vous ne pouvez pas être votre propre ami.")

    receiver = db.query(User).filter_by(id=request.receiver_id).first()
    if not receiver:
        raise HTTPException(status_code=404, detail="Utilisateur introuvable.")

    existing = db.query(Friendship).filter_by(
        requester_id=current_user.id,
        receiver_id=request.receiver_id,
        status="pending"
    ).first()

    if existing:
        raise HTTPException(status_code=400, detail="Demande déjà envoyée.")

    friendship = Friendship(
        requester_id=current_user.id,
        receiver_id=request.receiver_id,
        status="pending",
        created_at=datetime.utcnow()
    )
    db.add(friendship)
    db.commit()
    db.refresh(friendship)

    notification = Notification(
        requester_id=current_user.id,
        receiver_id=request.receiver_id,
        type="friend_request",
        message=f"{current_user.username} vous a envoyé une demande d'ami.",
        timestamp=datetime.utcnow(),
        is_read=False,
        friendship_id=friendship.id  
    )
    db.add(notification)
    db.commit()
    db.refresh(notification)

    return friendship


@router.post("/accept-friend/{friendship_id}", response_model=FriendshipResponse)
def accept_friend_request(
    friendship_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    friendship = db.query(Friendship).filter_by(id=friendship_id).first()
    if not friendship:
        raise HTTPException(status_code=404, detail="Demande non trouvée.")

    if friendship.receiver_id != current_user.id:
        raise HTTPException(status_code=403, detail="Action non autorisée.")

    friendship.status = "accepted"

    notification = db.query(Notification).filter_by(friendship_id=friendship_id).first()
    if notification:
        notification.status = "accepted"

    db.commit()
    db.refresh(friendship)
    return friendship


@router.delete("/remove-friend/{friendship_id}", response_model=dict)
def remove_friend(
    friendship_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    friendship = db.query(Friendship).filter_by(id=friendship_id).first()
    if not friendship:
        raise HTTPException(status_code=404, detail="Relation non trouvée.")

    if current_user.id not in [friendship.requester_id, friendship.receiver_id]:
        raise HTTPException(status_code=403, detail="Action non autorisée.")

    # Supprimer les notifications liées à cette amitié
    db.query(Notification).filter_by(friendship_id=friendship_id).delete()

    # Sauvegarder les IDs pour retour
    requester_id = friendship.requester_id
    receiver_id = friendship.receiver_id

    db.delete(friendship)
    db.commit()

    return {
        "message": "Amitié supprimée.",
        "requester_id": requester_id,
        "receiver_id": receiver_id
    }


# -------------------- SUIVI --------------------

@router.post("/follow", response_model=FollowResponse)
def follow_user(
    request: FollowCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    follow = Follow(
        follower_id=current_user.id,
        followed_id=request.followed_id,
        created_at=datetime.utcnow()
    )
    db.add(follow)
    db.commit()
    db.refresh(follow)

    notification = Notification(
        requester_id=current_user.id,
        receiver_id=request.followed_id,
        type="follow",
        message=f"{current_user.username} vous suit désormais.",
        timestamp=datetime.utcnow(),
        is_read=False
    )
    db.add(notification)
    db.commit()
    db.refresh(notification)

    return follow



@router.delete("/unfollow/{follow_id}", response_model=dict)
def unfollow_user(
    follow_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    follow = db.query(Follow).filter_by(id=follow_id).first()
    if not follow:
        raise HTTPException(status_code=404, detail="Abonnement non trouvé.")

    if follow.follower_id != current_user.id:
        raise HTTPException(status_code=403, detail="Action non autorisée.")

    # Supprimer les notifications liées à ce suivi
    db.query(Notification).filter_by(
        requester_id=current_user.id,
        receiver_id=follow.followed_id,
        type="follow"
    ).delete()

    followed_id = follow.followed_id

    db.delete(follow)
    db.commit()

    return {
        "message": "Désabonnement effectué.",
        "unfollowed_id": followed_id
    }


# -------------------- NOTIFICATIONS --------------------

@router.get("/notifications", response_model=list[NotificationResponse])
def get_user_notifications(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    notifications = db.query(Notification).filter_by(
        receiver_id=current_user.id
    ).order_by(Notification.timestamp.desc()).all()

    enriched = []
    for notif in notifications:
        friendship_status = None
        if notif.type == "friend_request" and notif.friendship_id:
            friendship = db.query(Friendship).filter_by(id=notif.friendship_id).first()
            friendship_status = friendship.status if friendship else "unknown"

        enriched.append(NotificationResponse(
            id=notif.id,
            requester_id=notif.requester_id,
            receiver_id=notif.receiver_id,
            message=notif.message,
            type=notif.type,
            timestamp=notif.timestamp,
            is_read=notif.is_read,
            friendship_id=notif.friendship_id,
            friendship_status=friendship_status
        ))

    return enriched



@router.put("/notifications/{notification_id}/read")
def mark_notification_as_read(
    notification_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    notification = db.query(Notification).filter_by(id=notification_id).first()
    if not notification:
        raise HTTPException(status_code=404, detail="Notification non trouvée.")

    if notification.receiver_id != current_user.id:
        raise HTTPException(status_code=403, detail="Action non autorisée.")

    notification.is_read = True
    db.commit()
    db.refresh(notification)
    return {"message": "Notification marquée comme lue.", "notification_id": notification.id}


@router.delete("/notifications/{notification_id}")
def delete_notification(
    notification_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    notification = db.query(Notification).filter_by(id=notification_id).first()
    if not notification:
        raise HTTPException(status_code=404, detail="Notification non trouvée.")

    if notification.receiver_id != current_user.id:
        raise HTTPException(status_code=403, detail="Action non autorisée.")

    db.delete(notification)
    db.commit()
    return {"message": "Notification supprimée.", "notification_id": notification_id}


@router.post("/notifications/mark_all_read")
def mark_all_notifications_as_read(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    notifications = db.query(Notification).filter_by(
        receiver_id=current_user.id,
        is_read=False
    ).all()

    for notif in notifications:
        notif.is_read = True

    db.commit()
    return {"message": f"{len(notifications)} notifications marquées comme lues."}


@router.get("/accepted", response_model=list[UserOut])
def get_accepted_friends(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    accepted_friendships = db.query(Friendship).filter(
        ((Friendship.requester_id == current_user.id) | (Friendship.receiver_id == current_user.id)),
        Friendship.status == "accepted"
    ).all()

    friend_ids = [
        f.receiver_id if f.requester_id == current_user.id else f.requester_id
        for f in accepted_friendships
    ]

    friends = db.query(User).filter(User.id.in_(friend_ids)).all()
    return friends
