from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.orm import relationship
from app.database import Base
from sqlalchemy.ext.associationproxy import association_proxy

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    full_name = Column(String)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)

    # Relation many-to-many vers les articles avec table d’association
    article_associations = relationship("UserArticleAssociation", back_populates="user", cascade="all, delete-orphan")
    articles = association_proxy("article_associations", "article")

    feed_associations = relationship("UserFeedAssociation", back_populates="user", cascade="all, delete-orphan")
    
    # Tes autres relations...
    feed_permissions = relationship("FeedAccess", back_populates="user", cascade="all, delete-orphan")
    created_collections = relationship("Collection", back_populates="creator", cascade="all, delete-orphan")
    permissions = relationship("CollectionPermission", back_populates="user", passive_deletes=True)

    collection_links = relationship(
        "CollectionMember",
        back_populates="user",
        cascade="all, delete-orphan",
    )
    collections = relationship(
        "Collection",
        secondary="collection_members",
        back_populates="members",
        overlaps="collection_links,user"
    )
    comments = relationship("Comment", back_populates="user", cascade="all, delete")

    collection_messages = relationship("CollectionMessage", back_populates="user", passive_deletes=True)

    collection_associations = relationship("CollectionUserAssociation", back_populates="user", passive_deletes=True)


