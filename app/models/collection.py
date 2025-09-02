from sqlalchemy import Column, Integer, String, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.database import Base

class Collection(Base):
    __tablename__ = "collections"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)

    creator_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"))
    creator = relationship("User", back_populates="created_collections")

    # Relations avec les articles et les flux
    collection_articles = relationship(
        "CollectionArticle",
        back_populates="collection",
        cascade="all, delete-orphan",
        passive_deletes=True
    )
    collection_feeds = relationship(
        "CollectionFeed",
        back_populates="collection",
        cascade="all, delete-orphan",
        passive_deletes=True
    )
    # Relations avec les membres
    member_links = relationship(
        "CollectionMember",
        back_populates="collection",
        cascade="all, delete-orphan",
        overlaps="collections"
    )

    members = relationship(
        "User",
        secondary="collection_members",
        back_populates="collections",
        overlaps="member_links,collection_links"
    )
    # Permissions
    permissions = relationship(
        "CollectionPermission",
        back_populates="collection",
        cascade="all, delete-orphan",
        passive_deletes=True
    )

    # Messages instantanées
    messages = relationship(
        "CollectionMessage", 
        back_populates="collection", 
        cascade="all, delete-orphan"
        )

    user_associations = relationship("CollectionUserAssociation", back_populates="collection")
