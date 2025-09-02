from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class FriendshipCreate(BaseModel):
    receiver_id: int

class FriendshipResponse(BaseModel):
    id: int
    requester_id: int
    receiver_id: int
    status: str
    created_at: datetime

    model_config = {
        "from_attributes": True
    }

class FollowCreate(BaseModel):
    followed_id: int

class FollowResponse(BaseModel):
    id: int
    follower_id: int
    followed_id: int
    created_at: datetime

    model_config = {
        "from_attributes": True
    }

class NotificationCreate(BaseModel):
    requester_id: int
    receiver_id: int
    type: str  # 'friend_request', 'follow', 'collection_invite', 'collection_comment'
    message: str
    friendship_id: Optional[int] = None
    collection_id: Optional[int] = None
    comment_id: Optional[int] = None


class NotificationResponse(BaseModel):
    id: int
    requester_id: int
    receiver_id: int
    type: str
    message: str
    timestamp: datetime
    is_read: bool = False
    friendship_id: Optional[int]
    friendship_status: Optional[str]
    collection_id: Optional[int] = None
    comment_id: Optional[int] = None


    model_config = {
        "from_attributes": True
    }

