from sqlalchemy import Column, Integer, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base  

class CollectionArticle(Base):
    __tablename__ = "collection_articles"

    id = Column(Integer, primary_key=True, index=True)
    collection_id = Column(Integer, ForeignKey("collections.id", ondelete="CASCADE"))
    article_id = Column(Integer, ForeignKey("rss_articles.id", ondelete="CASCADE"))
    added_at = Column(DateTime, default=datetime.utcnow)

    collection = relationship("Collection", back_populates="collection_articles")
    rss_article = relationship("RSSArticle", back_populates="collection_articles")
