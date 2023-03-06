import sys, os
from pyrogram.types import Message
from pyrogram import Client, filters

from TelegramBot.logging import LOGGER
from TelegramBot.helpers.filters import sudo_cmd


@Client.on_message(filters.command(["update", "gitpull"]) & sudo_cmd)
async def update(_, message: Message):
    """
    Update the bot with the latest commit changes from GitHub.
    """

    msg = await message.reply_text("Pulling changes with latest commits...", quote=True)
    os.system("git pull")
    LOGGER(__name__).info("Bot Updated with latest commits. Restarting now..")
    await msg.edit("Changes pulled with latest commits. Restarting bot now... ")
    os.execl(sys.executable, sys.executable, "-m", "TelegramBot")


@Client.on_message(filters.command(["log", "logs"]) & sudo_cmd)
async def log(client: Client, message: Message):
    """
    upload log file of the bot in telegram.
    """

    try:
        await client.send_document(
            message.chat.id,
            "logs.txt",
            caption="logs.txt",
            reply_to_message_id=message.id)

    except Exception as error:
        await message.reply_text(f"{error}", quote=True)
