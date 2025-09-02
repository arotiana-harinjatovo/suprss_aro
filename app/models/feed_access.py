from sqlalchemy import Column, Integer, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base  # ou ton fichier de base

class FeedAccess(Base):
    __tablename__ = "feed_access"

    id = Column(Integer, primary_key=True, index=True)
    feed_id = Column(Integer, ForeignKey("rss_feeds.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    can_edit = Column(Boolean, default=False)
    can_delete = Column(Boolean, default=False)

    # Relations (optionnelles si tu veux accéder aux objets liés)
    rss_feed = relationship("RSSFeed", back_populates="accesses")
    user = relationship("User", back_populates="feed_permissions")
    
