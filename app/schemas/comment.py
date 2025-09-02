from pydantic import BaseModel
from datetime import datetime
from app.schemas.user import UserOut

class CommentBase(BaseModel):
    text: str

class CommentCreate(CommentBase):
    article_id: int

class CommentOut(CommentBase):
    id: int
    user: UserOut
    article_id: int
    created_at: datetime

    model_config = {
        "from_attributes": True
    }

