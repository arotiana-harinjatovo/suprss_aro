from sqlalchemy import Column, Integer, ForeignKey, Boolean, String, JSON
from sqlalchemy.orm import relationship
from app.database import Base
from sqlalchemy import DateTime
from datetime import datetime



class UserArticleAssociation(Base):
    __tablename__ = 'user_article_association'

    user_id = Column(Integer, ForeignKey('users.id'), primary_key=True)
    article_id = Column(Integer, ForeignKey('rss_articles.id'), primary_key=True)
    is_read = Column(Boolean, default=False)
    is_favorite = Column(Boolean, default=False)
    # last_updated = Column(DateTime, default=datetime.utcnow)
    # A implémenter à la fin 
    
    # Ajout de single_parent=True pour la relation many-to-one
    user = relationship("User", back_populates="article_associations")
    article = relationship("RSSArticle", back_populates="user_associations")


class UserFeedAssociation(Base):
    __tablename__ = "user_feed_association"

    user_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
    feed_id = Column(Integer, ForeignKey("rss_feeds.id"), primary_key=True)
    
    title = Column(String, nullable=False)
    description = Column(String, nullable=True)
    tags = Column(JSON, nullable=True, default=[])
    update_frequency = Column(String, default="daily")
    is_active = Column(Boolean, default=True)
    is_shared = Column(Boolean, default=False)
    article_limit = Column(Integer, default=5)

    last_updated = Column(DateTime, default=datetime.utcnow)

    # Ajout de single_parent=True pour la relation many-to-one
    user = relationship("User", back_populates="feed_associations", single_parent=True)
    feed = relationship("RSSFeed", back_populates="user_associations", single_parent=True)


class CollectionUserAssociation(Base):
    __tablename__ = "collection_user_association"

    collection_id = Column(Integer, ForeignKey("collections.id", ondelete="CASCADE"), primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    role = Column(String, default="viewer")  # "creator", "editor", "viewer"
    is_active = Column(Boolean, default=True)  # Si l’utilisateur est encore membre

    # Relations
    user = relationship("User", back_populates="collection_associations")
    collection = relationship("Collection", back_populates="user_associations")
