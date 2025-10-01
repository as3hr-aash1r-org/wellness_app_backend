# Import all models to ensure they are registered with SQLAlchemy
from app.models.user import User
from app.models.chat import ChatRoom, Message
from app.models.dxn_directory import DXNDirectory
from app.models.fact import Fact
from app.models.feed import FeedCategory, FeedItem
from app.models.notifications import Notifications
from app.models.password_reset_tokens import PasswordResetTokens
from app.models.product import ProductCategory, Product
from app.models.referrals import Referrals
from app.models.user_rewards import UserReward
from app.models.challenge import Challenge, UserChallenge

__all__ = [
    "User",
    "ChatRoom", 
    "Message",
    "DxnDirectory",
    "Fact",
    "FeedCategory",
    "FeedItem", 
    "Notification",
    "PasswordResetToken",
    "ProductCategory",
    "Product",
    "Referrals",
    "UserReward",
    "Challenge",
    "UserChallenge"
]