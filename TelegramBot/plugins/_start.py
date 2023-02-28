from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram import filters, Client

from TelegramBot.helpers.functions import get_readable_time
from TelegramBot.helpers.decorators import ratelimiter
from TelegramBot.helpers.filters import dev_cmd 
from TelegramBot.helpers.start_constants import *
from TelegramBot import BotStartTime

from datetime import datetime
import httpx
import time



START_BUTTON = [
    [
        InlineKeyboardButton("📖 Commands", callback_data="COMMAND_BUTTON"),
        InlineKeyboardButton("👨‍💻 About me", callback_data="ABOUT_BUTTON"),
    ],
    [InlineKeyboardButton("🔭 Original Repo", url=f"https://github.com/sanjit-sinha/Tg-MediaInfoBot")]]

GOBACK_1_BUTTON = [[InlineKeyboardButton("🔙 Go Back", callback_data="START_BUTTON")]]


@Client.on_callback_query(filters.regex("_BUTTON"))
@ratelimiter
async def botCallbacks(_, CallbackQuery):
    clicker_user_id = CallbackQuery.from_user.id
    user_id = CallbackQuery.message.reply_to_message.from_user.id

    if clicker_user_id != user_id:
        return await CallbackQuery.answer("This command is not initiated by you.", warn=True)

    if CallbackQuery.data == "ABOUT_BUTTON":
        await CallbackQuery.edit_message_text(ABOUT_CAPTION, reply_markup=InlineKeyboardMarkup(GOBACK_1_BUTTON))

    elif CallbackQuery.data == "START_BUTTON":
        await CallbackQuery.edit_message_text(START_CAPTION, reply_markup=InlineKeyboardMarkup(START_BUTTON))

    elif CallbackQuery.data == "COMMAND_BUTTON":
        await CallbackQuery.edit_message_text(COMMAND_TEXT, reply_markup=InlineKeyboardMarkup(GOBACK_1_BUTTON))
        

@Client.on_message(filters.command(["start", "help"]))
@ratelimiter
async def start(_, message: Message):
    return await message.reply_text(
        START_CAPTION,
        reply_markup=InlineKeyboardMarkup(START_BUTTON),
        quote=True)
       

@Client.on_message(filters.command(["log", "logs"]) & dev_cmd)
@ratelimiter
async def log(client: Client, message: Message):
    """
    upload log file of the bot in telegram.
    """
    try:
        await client.send_document(message.chat.id, "logs.txt", caption="logs.txt", reply_to_message_id=message.id)
    except Exception as error:
        await message.reply_text(f"{error}", quote=True)
       

@Client.on_message(filters.command(["ping", "alive"]))
@ratelimiter
async def ping(_, message: Message):
    """
   Give ping speed of Telegram API along with Bot Uptime.
   """

    pong_reply = await message.reply_text("pong!", quote=True)

    start = datetime.now()
    async with httpx.AsyncClient() as client:
        await client.get("http://api.telegram.org")
    end = datetime.now()

    botuptime = get_readable_time(time.time() - BotStartTime)
    pong = (end - start).microseconds / 1000

    return await pong_reply.edit(f"**Ping Time:** `{pong}`ms | **Bot is alive since:** `{botuptime}`")
        
                        
