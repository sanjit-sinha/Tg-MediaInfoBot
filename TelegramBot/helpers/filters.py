from pyrogram import filters
from pyrogram.types import Message
from TelegramBot.config import SUDO_USERID, AUTHORIZED_CHATS


def authorized(_, __, message: Message) -> bool:
    """
    returns True if message is from sudo user or authorized chat,
    False otherwise.
    """

    if not message.from_user:
        return False
    if 0 in AUTHORIZED_CHATS:
        return True
    if message.chat.id in AUTHORIZED_CHATS:
        return True
    if message.from_user.id in SUDO_USERID:
        return True

    return False


def sudo_users(_, __, message: Message) -> bool:
    """
    returns True if message is from sudo user, False otherwise.
    """

    if not message.from_user:
        return False
    if message.from_user.id in SUDO_USERID:
        return True

    return False


check_auth = filters.create(authorized)
sudo_cmd = filters.create(sudo_users)
