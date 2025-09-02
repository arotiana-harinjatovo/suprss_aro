from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class RSSFeedBase(BaseModel):
    url: str

class RSSFeedOut(RSSFeedBase):
    id: int

    model_config = {
        "from_attributes": True
    }

class UserFeedAssociationBase(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    tags: Optional[List[str]] = Field(default_factory=list)
    update_frequency: Optional[str] = Field(
        default="daily",
        description="Fréquence de mise à jour du flux",
        pattern="^(hourly|6h|daily|weekly)$"
    )
    is_active: Optional[bool] = True
    is_shared: Optional[bool] = False
    article_limit: Optional[int] = 5

class UserFeedAssociationCreate(UserFeedAssociationBase):
    url: str  # Pour créer le lien, on passe l'URL du flux

class UserFeedAssociationUpdate(UserFeedAssociationBase):
    pass  # Tous les champs sont déjà optionnels

class UserFeedAssociationOut(UserFeedAssociationBase):
    user_id: int
    feed_id: int
    feed: RSSFeedOut  # Inclure les infos du flux
    created_at: Optional[str] = None  # Si tu as un champ de date
    last_updated: Optional[datetime] = None

    model_config = {
        "from_attributes": True
    }

class FeedFilter(BaseModel):
    source_name: Optional[str] = None
    tags: Optional[List[str]] = None
    active: Optional[bool] = None
    search_text: Optional[str] = None
