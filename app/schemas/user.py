from pydantic import BaseModel, EmailStr
from typing import Optional

class UserBase(BaseModel):
    username: str
    full_name: str
    email: EmailStr  # ← email validé automatiquement

class EmailCheck(BaseModel):
    email: EmailStr

class UserCreate(UserBase):
    password: str

class UserOut(UserBase):
    id: int
    is_active: bool

    model_config = {
        "from_attributes": True
    }

class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None


class UserSearchOut(BaseModel):
    id: int
    username: str
    email: str
    is_friend: bool
    friendship_id: Optional[int] = None
    friendship_status: Optional[str]
    is_following: bool
    follow_id: Optional[int] = None

class ForgotPasswordRequest(BaseModel):
    email: EmailStr
