from pydantic import BaseModel
from typing import Optional

class FeedAccessBase(BaseModel):
    feed_id: int
    user_id: int
    can_edit: Optional[bool] = False
    can_delete: Optional[bool] = False

class FeedAccessCreate(FeedAccessBase):
    pass

class FeedAccessOut(FeedAccessBase):
    id: int

    model_config = {
        "from_attributes": True
    }
