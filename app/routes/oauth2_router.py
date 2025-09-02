from fastapi import APIRouter, Request, Depends, HTTPException
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from authlib.integrations.starlette_client import OAuth
from starlette.config import Config
from datetime import timedelta

from app.database import get_db
from app.crud.user import get_user_by_identifier, create_user
from app.schemas.user import UserCreate
from app.services.auth import create_access_token

router = APIRouter(tags=["OAuth2"])

# ------------------ Configuration ------------------ #
config = Config('.env')
oauth = OAuth(config)


# URLs de base
BACKEND_BASE_URL = config("BACKEND_BASE_URL", default="http://localhost:8000")
FRONTEND_BASE_URL = config("FRONTEND_BASE_URL", default="http://localhost:5173")
ACCESS_TOKEN_EXPIRE_MINUTES = int(config("ACCESS_TOKEN_EXPIRE_MINUTES", default="30"))


# ------------------ Register ------------------ #

def register_oauth_providers():
    providers = {
        "google": {
            "client_id": config("GOOGLE_CLIENT_ID"),
            "client_secret": config("GOOGLE_CLIENT_SECRET"),
            "server_metadata_url": "https://accounts.google.com/.well-known/openid-configuration",
            "client_kwargs": {"scope": "openid email profile"},
        },
        "github": {
            "client_id": config("GITHUB_CLIENT_ID"),
            "client_secret": config("GITHUB_CLIENT_SECRET"),
            "access_token_url": "https://github.com/login/oauth/access_token",
            "authorize_url": "https://github.com/login/oauth/authorize",
            "api_base_url": "https://api.github.com/",
            "client_kwargs": {"scope": "user:email"},
        },
        "microsoft": {
            "client_id": config("MICROSOFT_CLIENT_ID"),
            "client_secret": config("MICROSOFT_CLIENT_SECRET"),
            "server_metadata_url": "https://login.microsoftonline.com/e6171cd3-2e3f-4d7d-97e4-f24dbfcd1019/v2.0/.well-known/openid-configuration",
            "client_kwargs": {"scope": "openid email profile User.Read"},
        }
    }

    for provider_name, params in providers.items():
        if not params.get("client_id") or not params.get("client_secret"):
            raise RuntimeError(f"Variables manquantes pour le provider {provider_name.upper()}")
        
    for name, params in providers.items():
        oauth.register(name=name, **params)
    

register_oauth_providers()



# ------------------ Démarrer l'authentification ------------------ #
@router.get("/auth/{provider}")
async def login_via_provider(provider: str, request: Request):
    redirect_path = config(f"{provider.upper()}_REDIRECT_PATH")
    redirect_uri = f"{BACKEND_BASE_URL}{redirect_path}"
    return await oauth.create_client(provider).authorize_redirect(request, redirect_uri)

# ------------------ Callback ------------------ #
@router.get("/auth/{provider}/callback")
async def provider_callback(provider: str, request: Request, db: Session = Depends(get_db)):
    try:
        token = await oauth.create_client(provider).authorize_access_token(request)

        if provider == "github":
            user_info_response = await oauth.github.get("user", token=token)
            user_info = user_info_response.json()
            email = user_info.get("email")
            full_name = user_info.get("name") or user_info.get("login")
            username = user_info.get("login")

            # Si l'email est manquant, on le récupère via l'endpoint /user/emails
            if not email:
                emails_response = await oauth.github.get("user/emails", token=token)
                emails = emails_response.json()
                primary_email = next((e["email"] for e in emails if e.get("primary") and e.get("verified")), None)
                email = primary_email

        elif provider == "microsoft":
            user_info_response = await oauth.microsoft.get("https://graph.microsoft.com/v1.0/me", token=token)
            user_info = user_info_response.json()
            email = user_info.get("mail") or user_info.get("userPrincipalName")
            full_name = user_info.get("displayName")
            username = email.split("@")[0]

        else:  # Google
            user_info_response = await oauth.google.userinfo(token=token)
            user_info = dict(user_info_response)
            email = user_info.get("email")
            full_name = user_info.get("name")
            username = email.split("@")[0]

    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=400, detail=f"Échec de l'authentification {provider}")

    if not email or not full_name:
        raise HTTPException(status_code=400, detail="Informations utilisateur incomplètes")

    user = get_user_by_identifier(db, email)
    if not user:
        user_data = UserCreate(
            username=username,
            full_name=full_name,
            email=email,
            password=f"{provider}_oauth"
        )
        user = create_user(db, user_data)

    access_token = create_access_token(
        data={"sub": str(user.id)},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )

    return RedirectResponse(url=f"{FRONTEND_BASE_URL}/auth/{provider}/callback?token={access_token}")
