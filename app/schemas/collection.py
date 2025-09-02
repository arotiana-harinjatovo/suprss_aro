from pydantic import BaseModel
from typing import Optional, List
from enum import Enum
from app.schemas.rss_feed import RSSFeedOut
from app.schemas.rss_article import RSSArticleOut
from datetime import datetime

class CollectionRole(str, Enum):
    creator = "creator"
    editor = "editor"
    viewer = "viewer"  # ou read_only

class InviteUserRequest(BaseModel):
    role: CollectionRole

class UserPermissions(BaseModel):
    user_id : int
    is_creator: bool
    can_add_feed: bool
    can_read: bool
    can_comment: bool
    role: CollectionRole

class CollectionPermissionUpdate(BaseModel):
    can_add_feed: Optional[bool]
    can_read: Optional[bool]
    can_comment: Optional[bool]

class CollectionCreate(BaseModel):
    name: str
    description: Optional[str] = None

class CollectionUpdate(BaseModel):
    name: str
    description: Optional[str] = None

class UserPublic(BaseModel):
    id: int
    username: str

    model_config = {
        "from_attributes": True
    }

class CollectionFeedOut(BaseModel):
    title: str
    rss_feed: RSSFeedOut
    added_at: datetime
    added_by: Optional[UserPublic]

class CollectionOut(BaseModel):
    id: int
    name: str
    description: Optional[str]
    creator_id: int
    creator_name: Optional[str] = None
    
    feeds: List[CollectionFeedOut] = []
    articles: List[RSSArticleOut] = []

    current_user_permissions: Optional[UserPermissions] = None  


    model_config = {
        "from_attributes": True
    }



