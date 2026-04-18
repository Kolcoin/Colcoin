"""Training scaffold for Telegram Managed Bots integrations."""

from .config import AppConfig, SecurityError, load_config
from .events import ManagedBotEvent, ManagedBotInfo, ManagedBotOwner, UserMessageEvent
from .links import create_customer_bot_link, generate_bot_creation_link
from .service import ManagedBotService
from .storage import InMemoryStorage

__all__ = [
    "AppConfig",
    "create_customer_bot_link",
    "generate_bot_creation_link",
    "InMemoryStorage",
    "ManagedBotEvent",
    "ManagedBotInfo",
    "ManagedBotOwner",
    "ManagedBotService",
    "SecurityError",
    "UserMessageEvent",
    "load_config",
]
