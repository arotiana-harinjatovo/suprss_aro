from sqlalchemy import Column, Integer, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

class CollectionPermission(Base):
    __tablename__ = "collection_permissions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    collection_id = Column(Integer, ForeignKey("collections.id", ondelete="CASCADE"))

    can_add_feed = Column(Boolean, default=False)
    can_read = Column(Boolean, default=True)
    can_comment = Column(Boolean, default=False)

    user = relationship("User", back_populates="permissions", overlaps="collections,member_links")
    collection = relationship("Collection", back_populates="permissions", passive_deletes=True)
