from fastapi import APIRouter, Depends, HTTPException, Form
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from datetime import timedelta
from typing import List
from fastapi import Query

from app.models import User  
from app.database import get_db
from app.schemas.user import UserOut, UserCreate, UserUpdate, UserSearchOut,ForgotPasswordRequest
from app.schemas.token import Token
from app.crud.user import get_user_by_identifier, get_user_by_id, create_user, update_user, delete_user
from app.services.auth import authenticate_user, create_access_token, get_current_user

from fastapi import BackgroundTasks
from app.services.email import send_reset_password_email  # à adapter selon ton projet
from app.models import User, Friendship, Follow

from fastapi import Body
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")



import os
from dotenv import load_dotenv

load_dotenv()
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))


router = APIRouter(tags=["User"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/user/token")


# ------------------ Route d'enregistrement ------------------ #

@router.post("/register", response_model=UserOut)
def register_user(
    username: str = Form(...),
    full_name: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    if get_user_by_identifier(db, username) or get_user_by_identifier(db, email):
        raise HTTPException(status_code=400, detail="Nom d'utilisateur ou e-mail déjà utilisé")

    user_data = UserCreate(
        username=username,
        full_name=full_name,
        email=email,
        password=password
    )
    return create_user(db, user_data)

# ------------------ Route de connexion (JWT) ------------------ #

@router.post("/token", response_model=Token)
def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Nom d'utilisateur ou mot de passe incorrect")

    access_token = create_access_token(
        data={"sub": str(user.id)},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    return {"access_token": access_token, "token_type": "bearer"}

# ------------------ Récupération du profil connecté ------------------ #

@router.get("/me", response_model=UserOut)
def read_users_me(current_user: UserOut = Depends(get_current_user)):
    return current_user

# ------------------ Mise à jour du profil ------------------ #

@router.put("/me", response_model=UserOut)
def update_my_profile(
    updates: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Recharge l'utilisateur depuis la session active
    user_in_db = db.query(User).filter(User.id == current_user.id).first()
    return update_user(db, user_in_db, updates)


# ------------------ Suppression du compte ------------------ #

@router.delete("/me", response_model=UserOut)
def delete_my_account(
    db: Session = Depends(get_db),
    current_user: UserOut = Depends(get_current_user)
):
    deleted_user = delete_user(db, current_user.id)
    if deleted_user is None:
        raise HTTPException(status_code=400, detail="Échec de la suppression")
    return deleted_user


# ------------------ Mot de passe oublié ------------------ #
@router.post("/forgot-password")
def forgot_password(
    request: ForgotPasswordRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    user = get_user_by_identifier(db, request.email)
    if not user:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")

    # Génère un token de réinitialisation (à adapter selon ta logique)
    reset_token = create_access_token(data={"sub": str(user.id)}, expires_delta=timedelta(hours=1))

    # Envoie l'e-mail en tâche de fond
    background_tasks.add_task(send_reset_password_email, user.email, reset_token)

    return {"message": "Un e-mail de réinitialisation a été envoyé"}

# ------------------ Réinitialisation de Mot de passe oublié ------------------ #
@router.post("/reset-password")
def reset_password(
    token: str = Body(...),
    new_password: str = Body(...),
    db: Session = Depends(get_db)
):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: int = int(payload.get("sub"))
    except (JWTError, ValueError):
        raise HTTPException(status_code=400, detail="Token invalide ou expiré")

    user = get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")

    # Passe le mot de passe en clair, il sera haché dans update_user
    update_user(db, user, UserUpdate(password=new_password))

    return {"message": "Mot de passe réinitialisé avec succès"}



# ------------------ Recherche utilisateurs ------------------ #


@router.get("/search", response_model=List[UserSearchOut])
def search_users(
    query: str = Query(..., min_length=1),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    search = f"%{query.lower()}%"
    users = db.query(User).filter(
        (User.email.ilike(search)) |
        (User.username.ilike(search)) |
        (User.full_name.ilike(search))
    ).all()

    if not users:
        raise HTTPException(status_code=404, detail="Aucun utilisateur trouvé.")

    results = []
    for user in users:
        if user.id == current_user.id:
            continue

        # Vérifie si une relation d'amitié existe
        friendship = db.query(Friendship).filter(
            ((Friendship.requester_id == current_user.id) & (Friendship.receiver_id == user.id)) |
            ((Friendship.requester_id == user.id) & (Friendship.receiver_id == current_user.id))
        ).first()

        is_friend = friendship is not None and friendship.status == "accepted"
        friendship_id = friendship.id if friendship else None
        friendship_status = friendship.status if friendship else None

        # Vérifie si déjà suivi
        follow = db.query(Follow).filter_by(
            follower_id=current_user.id,
            followed_id=user.id
        ).first()

        is_following = follow is not None
        follow_id = follow.id if follow else None

        results.append({
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "is_friend": is_friend,
            "friendship_id": friendship_id,
            "friendship_status": friendship_status,
            "is_following": is_following,
            "follow_id": follow_id
        })

    return results



