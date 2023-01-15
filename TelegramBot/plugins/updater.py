from TelegramBot.helpers.decorators import dev_commands, ratelimiter
from TelegramBot.logging import LOGGER
from TelegramBot.config import prefixes
from pyrogram import filters, Client
from pyrogram.types import Message
import sys
import os


@Client.on_message(filters.command("update", **prefixes))
@dev_commands
@ratelimiter
async def update(_, message: Message):
    """
    Update the bot with latest commit changes from GitHub.
    """

    msg = await message.reply_text("Pulling changes with latest commits...", quote=True)
    os.system("git pull")
    LOGGER(__name__).info("Bot Updated with latest commits. Restarting now..")
    await msg.edit("Changes pulled with latest commits. Restarting bot now... ")
    os.execl(sys.executable, sys.executable, "-m", "TelegramBot")


@Client.on_message(filters.command("restart", **prefixes))
@dev_commands
@ratelimiter
async def restart(_, message: Message):
    """
    This function just Restart the bot.
    """

    LOGGER(__name__).info("Restarting the bot. shutting down this instance")
    await message.reply_text("Starting a new instance and shutting down this one.", quote=True)
    os.execl(sys.executable, sys.executable, "-m", "TelegramBot")
