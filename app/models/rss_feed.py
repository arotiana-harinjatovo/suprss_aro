from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.database import Base
from sqlalchemy.ext.associationproxy import association_proxy


class RSSFeed(Base):
    __tablename__ = "rss_feeds"

    id = Column(Integer, primary_key=True, index=True)
    url = Column(String, unique=True, nullable=False) 
    user_associations = relationship("UserFeedAssociation", back_populates="feed", cascade="all, delete")
    articles = relationship("RSSArticle", back_populates="rss_feed", cascade="all, delete-orphan", passive_deletes=True)
    accesses = relationship("FeedAccess", back_populates="rss_feed")
    collection_feeds = relationship("CollectionFeed", back_populates="rss_feed", cascade="all, delete-orphan", passive_deletes=True)
    collections = association_proxy("collection_feeds", "collection")


