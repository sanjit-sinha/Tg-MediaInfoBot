from pyrogram import filters
from pyrogram.types import Message
from TelegramBot.config import OWNER_USERID


def dev_users(_, __, message: Message) -> bool:
    return message.from_user.id in OWNER_USERID if message.from_user else False

dev_cmd = filters.create(dev_users)
