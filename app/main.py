from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import Base, engine
from app.routes.users_router import router as users_router
from app.routes.feeds_router import router as feeds_router
from app.routes.articles_router import router as articles_router
from app.routes.user_feed_router import router as user_feed_router
from app.routes.user_article_router import router as user_article_router
from app.routes.collection_router import router as collection_router
from app.routes.oauth2_router import router as oauth2_router
from app.routes.followers_router import router as followers_router
from app.routes.comment_router import router as comment_router
from app.routes.export_import_router import router as export_import_router
from app.routes.collection_chat_router import router as collection_chat_router
from app.routes.search_router import router as search_router

from starlette.middleware.sessions import SessionMiddleware
import secrets

from app.models.user import User  
import os
from dotenv import load_dotenv

load_dotenv()
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

# Création automatique des tables
# Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Mon API RSS",
    description="API pour la gestion de flux RSS, collections partagées et articles.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)


# Middleware CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.add_middleware(
    SessionMiddleware,
    secret_key=SECRET_KEY,
    same_site="lax",  # "none" si HTTPS
    https_only=False  # True en production
)


# Inclusion des routeurs
app.include_router(users_router, prefix="/user")
app.include_router(oauth2_router)
app.include_router(followers_router)
app.include_router(feeds_router, prefix="/rss")
app.include_router(articles_router, prefix="/rss")
app.include_router(user_feed_router, prefix="/users")
app.include_router(user_article_router, prefix="/users")
app.include_router(collection_router, prefix="/rss")
app.include_router(comment_router)
app.include_router(export_import_router, prefix="/rss")
app.include_router(collection_chat_router)
app.include_router(search_router, prefix="/rss")

@app.get("/")
def read_root():
    return {
        "message": "Bienvenue sur votre API FastAPI.",
        "status": "Maintenance en cours. Revenez ultérieurement. Merci !"
    }
