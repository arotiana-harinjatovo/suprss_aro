from typing import List
from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session, joinedload
from app.database import get_db
from app.services.auth import get_current_user
from app.services.permissions import user_has_access_to_collection, is_creator, get_permissions_for_role, get_user_permissions_for_collection
from app.services.notifications import notify_collection_invite 

from app.models import (
    User, UserFeedAssociation, Collection, 
    CollectionArticle, CollectionFeed, CollectionMember, 
    CollectionPermission, RSSArticle, Comment, 
    CollectionRoleEnum
    )
from app.schemas.collection import (
    CollectionCreate, CollectionOut, InviteUserRequest, 
    UserPermissions, CollectionPermissionUpdate, 
    CollectionFeedOut, CollectionUpdate, UserPublic
    )
from app.schemas.rss_article import RSSArticleOut
from app.schemas.rss_feed import RSSFeedOut, UserFeedAssociationOut


router = APIRouter(prefix="/collections", tags=["Collections"])


# ------------------ Récupérer toutes les collections avec leurs flux et articles ------------------ #

@router.get("/", response_model=List[CollectionOut])
def get_all_collections(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    collections = (
        db.query(Collection)
        .filter(
            (Collection.creator_id == current_user.id) |
            (Collection.id.in_(
                db.query(CollectionPermission.collection_id)
                .filter(CollectionPermission.user_id == current_user.id)
            ))
        )
        .all()
    )

    response = []

    for col in collections:
        user_permissions = get_user_permissions_for_collection(db, col, current_user)

        collection_feeds = (
            db.query(CollectionFeed)
            .options(
                joinedload(CollectionFeed.rss_feed),
                joinedload(CollectionFeed.added_by_user)
            )
            .filter(CollectionFeed.collection_id == col.id)
            .all()
        )

        feeds_out = []
        for cf in collection_feeds:
            user_feed = db.query(UserFeedAssociation).filter_by(
                user_id=cf.added_by,
                feed_id=cf.feed_id
            ).first()

            if user_feed and user_feed.title:
                feeds_out.append(
                    CollectionFeedOut(
                        title=user_feed.title,
                        rss_feed=RSSFeedOut.from_orm(cf.rss_feed),
                        added_at=cf.added_at,
                        added_by=UserPublic.from_orm(cf.added_by_user) if cf.added_by_user else None
                    )
                )

        collection_articles = (
            db.query(CollectionArticle)
            .options(joinedload(CollectionArticle.rss_article))
            .filter(CollectionArticle.collection_id == col.id)
            .all()
        )

        articles_out = [
            RSSArticleOut.model_validate(ca.rss_article)
            for ca in collection_articles
        ]

        response.append(
            CollectionOut(
                id=col.id,
                name=col.name,
                description=col.description,
                creator_id=col.creator_id,
                creator_name=col.creator.username if col.creator else None,
                feeds=feeds_out,
                articles=articles_out,
                current_user_permissions=user_permissions
            )
        )

    return response




# ------------------ Créer une collection ------------------ #

@router.post("/", response_model=CollectionOut)
def create_collection(
    collection_data: CollectionCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    # Étape 1 : Créer la collection
    new_collection = Collection(**collection_data.dict(), creator_id=current_user.id)
    db.add(new_collection)
    db.commit()
    db.refresh(new_collection)

    # Étape 2 : Ajouter le créateur comme membre avec rôle
    existing_member = db.query(CollectionMember).filter_by(
        collection_id=new_collection.id,
        user_id=current_user.id
    ).first()

    if not existing_member:
        db.add(CollectionMember(
            collection_id=new_collection.id,
            user_id=current_user.id,
            role="creator"
        ))

    # Étape 3 : Ajouter les permissions du créateur
    existing_permissions = db.query(CollectionPermission).filter_by(
        collection_id=new_collection.id,
        user_id=current_user.id
    ).first()

    if not existing_permissions:
        db.add(CollectionPermission(
            collection_id=new_collection.id,
            user_id=current_user.id,
            can_add_feed=True,
            can_read=True,
            can_comment=True
        ))

    db.commit()

    # Étape 4 : Récupérer la collection avec le nom du créateur
    collection_with_creator = (
        db.query(Collection, User.username.label("creator_name"))
        .join(User, Collection.creator_id == User.id)
        .filter(Collection.id == new_collection.id)
        .first()
    )

    if not collection_with_creator:
        raise HTTPException(status_code=404, detail="Erreur lors de la récupération de la collection")

    collection, creator_name = collection_with_creator
    collection_dict = collection.__dict__.copy()
    collection_dict["creator_name"] = creator_name

    return collection_dict


# ------------------ Afficher les détails de la collection ------------------ #

@router.get("/{collection_id}", response_model=CollectionOut)
def get_collection_by_id(
    collection_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    # 1. Vérifie l'accès
    if not user_has_access_to_collection(db, collection_id, current_user.id):
        raise HTTPException(status_code=403, detail="Accès interdit à cette collection")

    # 2. Récupère la collection
    collection = db.query(Collection).filter(Collection.id == collection_id).first()
    if not collection:
        raise HTTPException(status_code=404, detail="Collection non trouvée")

    # 3. Détermine si l'utilisateur est le créateur
    is_user_creator = collection.creator_id == current_user.id

    # 4. Récupère les permissions
    if is_user_creator:
        user_permissions = UserPermissions(
            is_creator=True,
            can_add_feed=True,
            can_read=True,
            can_comment=True,
            role="creator",
            user_id=current_user.id, 
        )
    else:
        member = db.query(CollectionMember).filter_by(
            collection_id=collection_id,
            user_id=current_user.id
        ).first()

        permission = db.query(CollectionPermission).filter_by(
            collection_id=collection_id,
            user_id=current_user.id
        ).first()

        user_permissions = UserPermissions(
            is_creator=False,
            can_add_feed=permission.can_add_feed if permission else False,
            can_read=permission.can_read if permission else False,
            can_comment=permission.can_comment if permission else False,
            role=member.role if member else "viewer",
            user_id = current_user.id
        )

    # 5. Récupère les feeds avec leurs dates d'ajout
    collection_feeds = (
        db.query(CollectionFeed)
        .filter(CollectionFeed.collection_id == collection_id)
        .all()
    )

    feeds = []
    for cf in collection_feeds:
        # Essaye de récupérer le titre depuis UserFeedAssociation
        user_feed = db.query(UserFeedAssociation).filter_by(
            user_id=cf.added_by,
            feed_id=cf.feed_id
        ).first()

        # Fallback si le titre est absent
        title = None
        if user_feed and user_feed.title:
            title = user_feed.title
        elif cf.rss_feed and cf.rss_feed.title:
            title = cf.rss_feed.title
        else:
            title = "Flux sans titre"

        feeds.append(
            CollectionFeedOut(
                title=title,
                rss_feed=RSSFeedOut.from_orm(cf.rss_feed),
                added_at=cf.added_at,
                added_by=UserPublic.model_validate(cf.added_by_user) if cf.added_by_user else None
            )
        )


    # 6. Récupère les articles
    articles = (
        db.query(RSSArticle)
        .join(CollectionArticle, CollectionArticle.article_id == RSSArticle.id)
        .filter(CollectionArticle.collection_id == collection_id)
        .all()
    )

    # 7. Retourne la réponse
    return {
        "id": collection.id,
        "name": collection.name,
        "description": collection.description,
        "creator_id": collection.creator_id,
        "creator_name": collection.creator.username if collection.creator else None,
        "feeds": feeds,
        "articles": articles,
        "current_user_permissions": user_permissions,
        "current_user": UserPublic.model_validate(current_user),

    }

# ------------------ Modifier une collection ------------------ #


@router.put("/{collection_id}/edit")
def update_collection(
    collection_id: int,
    update_data: CollectionUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    collection = db.query(Collection).filter(Collection.id == collection_id).first()

    if not collection:
        raise HTTPException(status_code=404, detail="Collection non trouvée")

    if collection.creator_id != current_user.id:
        raise HTTPException(status_code=403, detail="Permission refusée")

    collection.name = update_data.name
    collection.description = update_data.description

    db.commit()
    db.refresh(collection)

    return {"message": "Collection mise à jour avec succès"}

# ------------------ Supprimer une collection ------------------ #

@router.delete("/{collection_id}")
def delete_collection(
    collection_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    if not user_has_access_to_collection(db, collection_id, current_user.id):
        raise HTTPException(status_code=403, detail="Accès interdit à cette collection")

    collection = db.query(Collection).filter(Collection.id == collection_id).first()
    if not collection:
        raise HTTPException(status_code=404, detail="Collection non trouvée")
    db.delete(collection)
    db.commit()
    return {"message": "Collection supprimée"}

# ------------------ Ajouter un article à une collection ------------------ #

@router.post("/{collection_id}/articles/{article_id}")
def add_article_to_collection(
    collection_id: int,
    article_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):  
    if not user_has_access_to_collection(db, collection_id, current_user.id):
        raise HTTPException(status_code=403, detail="Accès interdit à cette collection")

    link = CollectionArticle(collection_id=collection_id, article_id=article_id)
    db.add(link)
    db.commit()
    return {"message": "Article ajouté à la collection"}

# ------------------ Supprimer un article d'une collection ------------------ #

@router.delete("/{collection_id}/articles/{article_id}")
def remove_article_from_collection(
    collection_id: int,
    article_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):  

    if not user_has_access_to_collection(db, collection_id, current_user.id):
        raise HTTPException(status_code=403, detail="Accès interdit à cette collection")

    link = db.query(CollectionArticle).filter_by(collection_id=collection_id, article_id=article_id).first()
    if not link:
        raise HTTPException(status_code=404, detail="Lien non trouvé")

    db.delete(link)
    db.commit()

    # Suppression des commentaires associés à cet article
    comments = db.query(Comment).filter(Comment.article_id == article_id).all()
    for comment in comments:
        db.delete(comment)
    
    db.commit()

    # Optionnel : Si l'article n'est plus associé à aucune autre collection, on peut le supprimer
    remaining_links = db.query(CollectionArticle).filter_by(article_id=article_id).all()
    if not remaining_links:  
        article = db.query(RSSArticle).filter(RSSArticle.id == article_id).first()
        if article:
            db.delete(article)  
            db.commit()

    return {"message": "Article retiré de la collection et commentaires supprimés"}


# ------------------ Ajouter un flux RSS à une collection ------------------ #

@router.post("/{collection_id}/feeds/{feed_id}")
def add_feed_to_collection(
    collection_id: int,
    feed_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):  
    # Vérifie l'accès à la collection
    if not user_has_access_to_collection(db, collection_id, current_user.id):
        raise HTTPException(status_code=403, detail="Accès interdit à cette collection")

    # Vérifie que l'utilisateur est bien lié au flux
    user_feed = db.query(UserFeedAssociation).filter_by(
        user_id=current_user.id,
        feed_id=feed_id
    ).first()
    if not user_feed:
        raise HTTPException(status_code=403, detail="Ce flux ne vous appartient pas ou vous n'y êtes pas abonné.")

    # Vérifie que le lien n'existe pas déjà
    existing_link = db.query(CollectionFeed).filter_by(
        collection_id=collection_id,
        feed_id=feed_id
    ).first()
    if existing_link:
        raise HTTPException(status_code=400, detail="Ce flux est déjà dans la collection.")

    # Ajout du lien
    link = CollectionFeed(
        collection_id=collection_id, 
        feed_id=feed_id, 
        added_by=current_user.id
    )
    
    db.add(link)
    db.commit()
    return {"message": "Flux RSS ajouté à la collection"}


# ------------------ Supprimer un flux RSS d'une collection ------------------ #

@router.delete("/{collection_id}/feeds/{feed_id}")
def remove_feed_from_collection(
    collection_id: int,
    feed_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):  
    
    if not user_has_access_to_collection(db, collection_id, current_user.id):
        raise HTTPException(status_code=403, detail="Accès interdit à cette collection")

    link = db.query(CollectionFeed).filter_by(collection_id=collection_id, feed_id=feed_id).first()
    if not link:
        raise HTTPException(status_code=404, detail="Lien non trouvé")
    db.delete(link)
    db.commit()
    return {"message": "Flux RSS retiré de la collection"}

# ------------------ Récupérer les articles d'une collection ------------------ #

@router.get("/{collection_id}/articles", response_model=list[RSSArticleOut])
def get_articles_in_collection(
    collection_id: int,
    db: Session = Depends(get_db),
    
    current_user=Depends(get_current_user)
):  
    
    if not user_has_access_to_collection(db, collection_id, current_user.id):
        raise HTTPException(status_code=403, detail="Accès interdit à cette collection")

    return (
        db.query(RSSArticle)
        .join(CollectionArticle)
        .filter(CollectionArticle.collection_id == collection_id)
        .all()
    )

# ------------------ Récupérer les flux RSS d'une collection ------------------ #

router.get("/{collection_id}/feeds", response_model=list[UserFeedAssociationOut])
def get_feeds_in_collection(
    collection_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):  
    if not user_has_access_to_collection(db, collection_id, current_user.id):
        raise HTTPException(status_code=403, detail="Accès interdit à cette collection")

    # Récupère les feed_id liés à la collection
    feed_ids = db.query(CollectionFeed.feed_id).filter_by(collection_id=collection_id).all()
    feed_ids = [fid[0] for fid in feed_ids]

    # Récupère les associations utilisateur-flux correspondantes
    associations = (
        db.query(UserFeedAssociation)
        .options(joinedload(UserFeedAssociation.feed))
        .filter(
            UserFeedAssociation.user_id == current_user.id,
            UserFeedAssociation.feed_id.in_(feed_ids)
        )
        .all()
    )

    return associations



# ------------------ Inviter les utilisateur et permission ------------------ #


@router.post("/{collection_id}/invite/{user_id}")
def invite_user_to_collection(
    collection_id: int,
    user_id: int,
    request: InviteUserRequest = Body(...),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    # Vérification de la collection
    collection = db.query(Collection).filter(Collection.id == collection_id).first()
    if not collection:
        return {"message": "Collection non trouvée", "status": "error"}

    # Vérifie que le current_user est le créateur
    if not is_creator(collection, current_user.id):
        return {"message": "Seul le créateur peut inviter", "status": "error"}

    # Vérifie que l'utilisateur n'est pas déjà membre
    if user_has_access_to_collection(db, collection_id, user_id):
        return {
            "message": "Utilisateur déjà membre de la collection",
            "user_id": user_id,
            "status": "warning"
        }

    # Récupère les permissions à partir du rôle
    permissions = get_permissions_for_role(request.role)

    # Ajoute le membre
    db.add(CollectionMember(
        collection_id=collection_id,
        user_id=user_id,
        role=request.role
    ))

    # Ajoute les permissions
    db.add(CollectionPermission(
        collection_id=collection_id,
        user_id=user_id,
        **permissions
    ))

    db.commit()

    # Envoie une notification à l'utilisateur invité
    notify_collection_invite(
        db=db,
        requester_id=current_user.id,
        receiver_id=user_id,
        collection_id=collection_id
    )

    return {
        "message": "Utilisateur invité avec succès",
        "user_id": user_id,
        "role": request.role,
        "permissions": permissions,
        "status": "success"
    }



# ------------------ Lire les permissions d'une collection ------------------ #
@router.get("/{collection_id}/permissions")
def get_collection_permissions(
    collection_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    
    if not user_has_access_to_collection(db, collection_id, current_user.id):
        raise HTTPException(status_code=403, detail="Accès interdit à cette collection")

    collection = db.query(Collection).filter(Collection.id == collection_id).first()
    if not collection:
        raise HTTPException(status_code=404, detail="Collection non trouvée")

    permissions = db.query(CollectionPermission).filter_by(collection_id=collection_id).all()
    return [
        {
            "user_id": p.user_id,
            "user_name": p.user.full_name,
            "can_add_feed": p.can_add_feed,
            "can_read": p.can_read,
            "can_comment": p.can_comment,
            "is_creator": p.user_id == collection.creator_id
        }
        for p in permissions
    ]


# ------------------ Mis à jour des permission ------------------ #
@router.put("/{collection_id}/permissions/{user_id}")
def update_user_permissions(
    collection_id: int,
    user_id: int,
    permissions: CollectionPermissionUpdate,  # <- Utilisation du modèle Pydantic
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    collection = db.query(Collection).filter(Collection.id == collection_id).first()
    if not collection:
        raise HTTPException(status_code=404, detail="Collection non trouvée")

    if collection.creator_id != current_user.id:
        raise HTTPException(status_code=403, detail="Seul le créateur peut modifier les permissions")

    permission = db.query(CollectionPermission).filter_by(
        collection_id=collection_id,
        user_id=user_id
    ).first()

    if not permission:
        permission = CollectionPermission(
            collection_id=collection_id,
            user_id=user_id
        )
        db.add(permission)

    # Mets à jour uniquement les champs présents dans le body (optionnels)
    if permissions.can_add_feed is not None:
        permission.can_add_feed = permissions.can_add_feed
    if permissions.can_read is not None:
        permission.can_read = permissions.can_read
    if permissions.can_comment is not None:
        permission.can_comment = permissions.can_comment

    db.commit()
    return {"message": "Permissions mises à jour avec succès"}

# ------------------ Suppression d’un membre ------------------ #
@router.delete("/{collection_id}/members/{user_id}")
def remove_user_from_collection(
    collection_id: int,
    user_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    # Vérifie que la collection existe
    collection = db.query(Collection).filter(Collection.id == collection_id).first()
    if not collection:
        raise HTTPException(status_code=404, detail="Collection non trouvée")

    # Seul le créateur peut supprimer des membres
    if collection.creator_id != current_user.id:
        raise HTTPException(status_code=403, detail="Seul le créateur peut supprimer des membres")

    # Empêche la suppression du créateur lui-même
    if user_id == collection.creator_id:
        raise HTTPException(status_code=400, detail="Le créateur ne peut pas être supprimé")

    permission = db.query(CollectionPermission).filter_by(
    collection_id=collection_id,
    user_id=user_id
    ).first()

    member = db.query(CollectionMember).filter_by(
        collection_id=collection_id,
        user_id=user_id
    ).first()

    if not permission and not member:
        raise HTTPException(status_code=404, detail="Membre non trouvé dans cette collection")

    if permission:
        db.delete(permission)
    if member:
        db.delete(member)

    db.commit()

    return {"message": "Membre supprimé avec succès"}

# ------------------ Quitter la collection ------------------ #
@router.post("/{collection_id}/leave")
def leave_collection(
    collection_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    # Vérifie s'il est membre
    member = db.query(CollectionMember).filter_by(
        collection_id=collection_id,
        user_id=current_user.id
    ).first()

    if not member:
        raise HTTPException(status_code=404, detail="Vous n'êtes pas membre de cette collection.")

    if member.role == CollectionRoleEnum.creator:
        raise HTTPException(status_code=403, detail="Le créateur ne peut pas quitter la collection.")

    # Supprime le membre
    db.delete(member)

    # Supprime les permissions associées
    permission = db.query(CollectionPermission).filter_by(
        collection_id=collection_id,
        user_id=current_user.id
    ).first()
    if permission:
        db.delete(permission)

    db.commit()
    return {"message": "Vous avez quitté la collection."}

