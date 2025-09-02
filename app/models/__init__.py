from .rss_article import RSSArticle
from .rss_feed import RSSFeed
from .user import User
from .collection import Collection
from .collection_feeds import CollectionFeed 
from .collection_articles import CollectionArticle  
from .collection_members import CollectionRoleEnum, CollectionMember
from .collection_permission import CollectionPermission
from .feed_access import FeedAccess
from .followers import Follow, Friendship, Notification
from .comment import Comment
from app.database import Base
from .associations import UserArticleAssociation, UserFeedAssociation, CollectionUserAssociation
from .collection_message import CollectionMessage

target_metadata = Base.metadata
from sqlalchemy.orm import configure_mappers
configure_mappers()
