from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.ext.associationproxy import association_proxy
from datetime import datetime
from app.database import Base

class RSSArticle(Base):
    __tablename__ = "rss_articles"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    link = Column(String, nullable=False, unique=True)
    published_at = Column(DateTime, default=datetime.utcnow)
    tags = Column(JSON, nullable=True)
    author = Column(String, nullable=True)
    summary = Column(String, nullable=True)
    source_name = Column(String)
    feed_id = Column(Integer, ForeignKey("rss_feeds.id", ondelete="CASCADE"), nullable=False)

    # Relation vers le flux RSS
    rss_feed = relationship("RSSFeed", back_populates="articles", passive_deletes=True)

    # Relation vers les utilisateurs via la table d'association
    user_associations = relationship("UserArticleAssociation", back_populates="article", cascade="all, delete-orphan")
    users = association_proxy("user_associations", "user")

    # Autres relations
    collection_articles = relationship("CollectionArticle", back_populates="rss_article")
    comments = relationship("Comment", back_populates="article", cascade="all, delete-orphan")
