from typing import Optional, List
from pydantic import BaseModel
from datetime import datetime

# Base article structure
class RSSArticleBase(BaseModel):
    title: str
    link: str
    published_at: Optional[datetime] = None
    summary: Optional[str] = None
    author: Optional[str] = None
    source_name: Optional[str] = None
    tags: Optional[List[str]] = []

# Pour créer un article RSS (sans is_read/is_favorite)
class RSSArticleCreate(RSSArticleBase):
    feed_id: int  # Lien vers le flux RSS parent

# Pour lier un article existant à un utilisateur
class UserArticleLinkCreate(BaseModel):
    user_id: int
    article_id: int
    is_read: Optional[bool] = False
    is_favorite: Optional[bool] = False

# Pour afficher un article (sans les infos utilisateur)
class RSSArticleOut(RSSArticleBase):
    id: int
    feed_id: int

    model_config = {
        "from_attributes": True
    }

# Pour afficher un article lié à un utilisateur avec is_read/is_favorite
class UserArticleAssociationOut(BaseModel):
    user_id: int
    is_read: bool
    is_favorite: bool
    article: RSSArticleOut

    model_config = {
        "from_attributes": True
    }

# Pour filtrer les articles dans une recherche
class ArticleFilter(BaseModel):
    source_name: Optional[str] = None
    tags: Optional[List[str]] = None
    status: Optional[str] = None  # ex: "read", "unread"
    favorite: Optional[bool] = None
    search_text: Optional[str] = None
