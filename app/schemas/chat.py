from pydantic import BaseModel
from datetime import datetime

class CollectionMessageCreate(BaseModel):
    content: str


class CollectionMessageResponse(BaseModel):
    user_id: int
    user_name: str
    content: str
    timestamp: datetime

    model_config = {
        "from_attributes": True
    }
