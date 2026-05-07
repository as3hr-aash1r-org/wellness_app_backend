# Import all models to ensure they are registered with SQLAlchemy
from app.models.user import User, AppLevel
from app.models.chat import ChatRoom, Message
from app.models.dxn_directory import DXNDirectory
from app.models.fact import Fact, FactTODPointer, UserFactLibrary
from app.models.feed import FeedCategory, FeedItem
from app.models.notifications import Notifications
from app.models.password_reset_tokens import PasswordResetTokens
from app.models.product import ProductCategory, Product
from app.models.referrals import Referrals
from app.models.user_rewards import UserReward
from app.models.challenge import Challenge, UserChallenge
from app.models.wellness import Wellness
from app.models.submission import Submission
from app.models.desire_list import DesireListItem
from app.models.user_level import UserLevelCondition, AppSession, ConditionKey
from app.models.card import Card, CardType
from app.models.support_ticket import SupportTicket, TicketStatus

__all__ = [
    "User",
    "AppLevel",
    "ChatRoom", 
    "Message",
    "DxnDirectory",
    "Fact",
    "FactTODPointer",
    "UserFactLibrary",
    "FeedCategory",
    "FeedItem", 
    "Notification",
    "PasswordResetToken",
    "ProductCategory",
    "Product",
    "Referrals",
    "UserReward",
    "Challenge",
    "UserChallenge",
    "Wellness",
    "Submission",
    "DesireListItem",
    "UserLevelCondition",
    "AppSession",
    "ConditionKey",
    "Card",
    "CardType",
    "SupportTicket",
    "TicketStatus"
]