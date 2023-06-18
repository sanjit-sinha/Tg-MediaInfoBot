import re
import json
import httpx
import asyncio
import requests
import tempfile
import urllib.parse
from urllib.parse import unquote
from async_timeout import timeout

from pyrogram import filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton

from TelegramBot import bot
from TelegramBot.logging import LOGGER
from TelegramBot.helpers.filters import check_auth
from TelegramBot.helpers.pasting_services import katbin_paste
from TelegramBot.helpers.gdrivehelper import GoogleDriveHelper
from TelegramBot.helpers.mediainfo_paste import mediainfo_paste
from TelegramBot.helpers.functions import async_subprocess, get_readable_bytes, get_readable_bitrate, remove_N


async def send_mediainfo(reply_msg: Message, mediainfo: str, filename: str, isRaw: bool) -> None:
    """Send Mediainfo to the user in telegram."""

    if isRaw:
        output = await katbin_paste(mediainfo)
        button = InlineKeyboardMarkup(
            [[InlineKeyboardButton("📂 MediaInfo", url=f"{output}.txt")]])
    else:
        output = mediainfo_paste(text=mediainfo, title=filename)
        button = InlineKeyboardMarkup(
            [[InlineKeyboardButton("📂 MediaInfo", url=output)]])

    return await reply_msg.edit(f"**{filename}**", reply_markup=button)


async def gdrive_mediainfo(message: Message, url: str, isRaw: bool) -> None:
    """Generates Mediainfo from a Google Drive file."""

    reply_msg = await message.reply_text("Generating Mediainfo, Please wait ...", quote=True)
    try:
        gdrive = GoogleDriveHelper()
        metadata = gdrive.get_metadata(url)
        filename = metadata["name"]
        mimetype = metadata["mimeType"]

        if mimetype == "application/vnd.google-apps.folder":
            return await reply_msg.edit(
                "Gdrive Folders are not supported for generating Mediainfo.")

        file_id = gdrive.get_id(url)
        file_ddl = gdrive.get_ddl_link(url)
        bearer_token = gdrive.get_bearer_token()

        headers = f"--file_curl=HttpHeader,Authorization: Bearer {bearer_token}"
        mediainfo = await async_subprocess(f"mediainfo '{headers}' {file_ddl}")
        mediainfo = mediainfo.replace(
            f"https://www.googleapis.com/drive/v3/files/{file_id}", filename)

        return await send_mediainfo(reply_msg, mediainfo, filename, isRaw)

    except Exception as error:
        LOGGER(__name__).error(error)
        return await reply_msg.edit(
            "Something went wrong while processing the Gdrive link.\n\n (Make sure that the gdrive link is not rate-limited, is a public link, and not a folder)")


async def ddl_mediainfo(message: Message, url: str, isRaw: bool) -> None:
    """Generates Mediainfo from a Direct Download Link."""

    reply_msg = await message.reply_text("Generating Mediainfo, Please wait ...", quote=True)
    try:
        # Fixing url encoding issues.
        parsed = urllib.parse.unquote(url)
        url = urllib.parse.quote(parsed.encode("utf8"), safe=":/=?&")

        # Getting filename from url and shortening it to >250 characters.
        filename = re.search(".+/(.+)", url).group(1)
        filename = unquote(filename)
        if len(filename) > 250:
            filename = filename[-250:]

        # initiating Httpx client
        client = httpx.AsyncClient()
        headers = {"user-agent": "Mozilla/5.0 (Linux; Android 12; 2201116PI) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Mobile Safari/537.36"}

        # Temporary file to store downloaded chunk.
        with tempfile.NamedTemporaryFile(suffix=f"_{filename}", dir="download") as download_path:

            # Trigger TimeoutError after 15 seconds if download is slow / unsuccessful.
            async with timeout(15):
                async with client.stream("GET", url, headers=headers) as response:

                    # Download 10mb Chunk
                    async for chunk in response.aiter_bytes(10_000_000):
                        with open(download_path.name, "wb") as file:
                            file.write(chunk)
                            break

            # mediainfo from chunk.
            mediainfo = await async_subprocess(f"mediainfo '{download_path.name}' ")
            mediainfo_json = json.loads(await async_subprocess(f"mediainfo '{download_path.name}' --Output=JSON"))

        # Modify mediainfo output for correct filename, filesize, bitrate, etc.
        filesize = requests.head(url).headers.get("content-length")
        lines = mediainfo.splitlines()
        for i in range(len(lines)):
            if "Complete name" in lines[i]:
                lines[i] = re.sub(r": .+", ": " + filename, lines[i])

            elif "File size" in lines[i]:
                lines[i] = re.sub(
                    r": .+", ": " + get_readable_bytes(float(filesize)), lines[i])

            elif ("Overall bit rate" in lines[i] and "Overall bit rate mode" not in lines[i]):
                duration = float(
                    mediainfo_json["media"]["track"][0]["Duration"])
                bitrate = get_readable_bitrate(
                    float(filesize) * 8 / (duration * 1000))
                lines[i] = re.sub(r": .+", ": " + bitrate, lines[i])

            elif "IsTruncated" in lines[i] or "FileExtension_Invalid" in lines[i]:
                lines[i] = ""

            remove_N(lines)

        mediainfo = "\n".join(lines)
        return await send_mediainfo(reply_msg, mediainfo, filename, isRaw)

    except asyncio.TimeoutError:
        return await reply_msg.edit(
            "Sorry! process failed due to timeout. Your process was taking too long to complete, hence it was cancelled.")

    except Exception as error:
        LOGGER(__name__).error(error)
        return await reply_msg.edit(
            "Something went wrong while generating Mediainfo from the given url.")


async def telegram_mediainfo(message: Message, isRaw: bool) -> None:
    """Generates Mediainfo from a Telegram File."""

    reply_msg = await message.reply_text("Generating Mediainfo, Please wait ...", quote=True)
    try:
        message = message.reply_to_message
        if message.text:
            return await message.reply_text(
                "Reply to a proper media file for generating Mediainfo.**", quote=True)

        if message.media.value in ["video", "audio", "document", "voice"]:
            media = getattr(message, message.media.value)

        else:
            return await reply_msg.edit(
                "This type of media is not supported for generating Mediainfo.")

        filename = str(media.file_name)
        filesize = media.file_size

        # Creating Temporary file to store downloaded chunk.
        with tempfile.NamedTemporaryFile(suffix=f"_{filename}", dir="download") as download_path:
            async for chunk in bot.stream_media(message, limit=5):
                with open(download_path.name, "ab") as file:
                    file.write(chunk)

            # mediainfo from chunk.
            mediainfo = await async_subprocess(f"mediainfo '{download_path.name}'")
            mediainfo_json = json.loads(await async_subprocess(f"mediainfo '{download_path.name}' --Output=JSON"))

        # Modify mediainfo output for correct filename, filesize, bitrate, etc.
        readable_size = get_readable_bytes(filesize)
        lines = mediainfo.splitlines()
        for i in range(len(lines)):
            if "Complete name" in lines[i]:
                lines[i] = re.sub(r": .+", ": " + unquote(filename), lines[i])

            if "File size" in lines[i]:
                lines[i] = re.sub(r": .+", ": " + readable_size, lines[i])

            elif ("Overall bit rate" in lines[i] and "Overall bit rate mode" not in lines[i]):
                duration = float(
                    mediainfo_json["media"]["track"][0]["Duration"])
                bitrate_kbps = (filesize * 8) / (duration * 1000)
                bitrate = get_readable_bitrate(bitrate_kbps)
                lines[i] = re.sub(r": .+", ": " + bitrate, lines[i])

            elif "IsTruncated" in lines[i] or "FileExtension_Invalid" in lines[i]:
                lines[i] = ""

        remove_N(lines)
        mediainfo = "\n".join(lines)

        return await send_mediainfo(reply_msg, mediainfo, filename, isRaw)

    except Exception as error:
        LOGGER(__name__).error(error)
        return await reply_msg.edit(
            "Something went wrong while generating Mediainfo from replied Telegram file.")


@bot.on_message(filters.command(["mediainfo", "m"]) & check_auth)
async def mediainfo(_, message: Message):
    mediainfo_usage = "**Generates mediainfo from Google Drive Links, Telegram files\
    or direct download links. \n\nReply to any telegram file or just pass the link\
    after the command.\n\nUse `--r` flag for raw Mediainfo in document format."

    if message.reply_to_message:
        isRaw = False
        if len(message.command) > 1:
            user_input = message.text.split(None, 1)[1]
            isRaw = bool(re.search(r"(-|--)r", user_input))
        return await telegram_mediainfo(message, isRaw)

    if len(message.command) < 2:
        return await message.reply_text(mediainfo_usage, quote=True)

    user_input = message.text.split(None, 1)[1]
    isRaw = bool(re.search(r"(-|--)r", user_input))

    if url_match := re.search(r"https://drive\.google\.com/\S+", user_input):
        url = url_match.group(0)
        return await gdrive_mediainfo(message, url, isRaw)

    if url_match := re.search(r"https?:\/\/[\w-]+(\.[\w-]+)+(:\d+)?(\/[^\s]*)?", user_input,):
        url = url_match.group(0)
        return await ddl_mediainfo(message, url, isRaw)

    return await message.reply_text("This type of link is not supported.", quote=True)
