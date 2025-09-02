from sqlalchemy import  Column, Integer, ForeignKey, DateTime
from app.database import Base
from sqlalchemy.orm import relationship
from datetime import datetime

class CollectionFeed(Base):
    __tablename__ = "collection_feeds"

    id = Column(Integer, primary_key=True)
    collection_id = Column(Integer, ForeignKey("collections.id", ondelete="CASCADE"))
    feed_id = Column(Integer, ForeignKey("rss_feeds.id", ondelete="CASCADE"))
    added_at = Column(DateTime, default=datetime.utcnow)
    added_by = Column(Integer, ForeignKey("users.id"))

    collection = relationship("Collection", back_populates="collection_feeds")
    rss_feed = relationship("RSSFeed", back_populates="collection_feeds")
    added_by_user = relationship("User") 
