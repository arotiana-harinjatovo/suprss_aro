from sqlalchemy import Column, Integer, ForeignKey, Enum
from sqlalchemy.orm import relationship
from app.database import Base
import enum

class CollectionRoleEnum(str, enum.Enum):
    creator = "creator"
    editor = "editor"
    viewer = "viewer"

class CollectionMember(Base):
    __tablename__ = "collection_members"

    id = Column(Integer, primary_key=True, index=True)
    collection_id = Column(Integer, ForeignKey("collections.id", ondelete="CASCADE"))
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    role = Column(Enum(CollectionRoleEnum), nullable=False)

    collection = relationship("Collection", back_populates="member_links", overlaps="members,collections")
    user = relationship("User", back_populates="collection_links", overlaps="members")

