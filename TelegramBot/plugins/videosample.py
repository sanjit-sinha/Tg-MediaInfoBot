import re
import os
import json
import random
import tempfile
import datetime
import requests
import urllib.parse
from urllib.parse import unquote

from pyrogram import Client, filters
from TelegramBot.logging import LOGGER
from pyrogram.errors import MessageNotModified
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message

from TelegramBot import bot
from TelegramBot.helpers.filters import check_auth
from TelegramBot.helpers.functions import async_subprocess
from TelegramBot.helpers.gdrivehelper import GoogleDriveHelper


# thumbnail of the video file.
thumb_path = "thumb.jpg"
thumb = requests.get("https://graph.org/file/4fabb3dc172082738cc5c.jpg", allow_redirects=True)
open(thumb_path, "wb").write(thumb.content)


async def generate_videosample_from_link(
    message, replymsg, file_url, duration, headers, filename, timestamp
):
    """Generates video sample from Direct Download link using ffmpeg."""

    await replymsg.edit(f"Generating {duration} min video sample from `{filename}`, please wait ...")
    original_name = filename
    filename = filename.replace(" ", ".")

    with tempfile.NamedTemporaryFile(suffix=f"_{filename}", dir="download") as output_path:

        ffmpeg_command = f"ffmpeg -headers '{headers}' -y -i {file_url} -ss {timestamp} -t 00:0{int(duration)}:00  -c:v copy -c:a copy {output_path.name}"
        await async_subprocess(ffmpeg_command)

        if os.path.getsize(output_path.name) > 1900000000:
            os.remove(output_path.name)
            return await replymsg.edit("Sample file is larger than 2GB. Can not upload large sample files which exceed Telegram Limits.")

        await replymsg.edit("Uploading the video file, Please wait ...")
        await message.reply_video(
            video=output_path.name,
            caption=f"[**{duration}min Sample**] {original_name}",
            thumb=thumb_path,
            quote=True)

        await replymsg.delete()


async def gdrive_videosample(message, url, duration):
    """Generates video sample From Google Drive link."""

    replymsg = await message.reply_text("Checking your Gdrive link ...", quote=True)
    try:
        drive = GoogleDriveHelper()
        metadata = drive.get_metadata(url)
        filename = unquote(metadata["name"])

        if "video" not in metadata["mimeType"]:
            return await replymsg.edit("Can only generate sample from video file.**")

        file_url = drive.get_ddl_link(url)
        bearer_token = drive.get_bearer_token()
        headers = f"Authorization: Bearer {bearer_token}"

        total_duration = await async_subprocess(f"ffprobe -headers '{headers}'  -v quiet -show_format -print_format json {file_url}")
        ffprobe_data = json.loads(total_duration)
        total_duration = float(ffprobe_data["format"]["duration"])

        # Generate a random timestamp between first 15-20% of the movie.
        timestamp = total_duration * (random.uniform(15, 20) / 100)

        # converting final timestamp into HH:MM:SS format
        timestamp = str(datetime.timedelta(seconds=int(timestamp)))

        await generate_videosample_from_link(message, replymsg, file_url, duration, headers, filename, timestamp)

    except MessageNotModified:
        pass
    except Exception as error:
        LOGGER(__name__).error(error)
        return await replymsg.edit(
            "Something went wrong while processing Gdrive link. Make sure that the link is public, not rate limited and is a proper video file.")


async def ddl_videosample(message, url, duration):
    """Generates video sample from Direct Download link."""

    replymsg = await message.reply_text("Checking direct download url ...**", quote=True)
    try:
        parsed = urllib.parse.unquote(url)
        url = urllib.parse.quote(parsed.encode("utf8"), safe=":/=?&")

        file_url = f"'{url}'"
        filename = re.search(".+/(.+)", url).group(1)
        if len(filename) > 250:
            filename = filename[-250:]
        filename = unquote(filename)

        headers = "user-agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4136.7 Safari/537.36"

        # calculate total duration of the video file.
        total_duration = await async_subprocess(f"ffprobe -headers '{headers}' -v quiet -show_format -print_format json {file_url} ")
        ffprobe_data = json.loads(total_duration)
        total_duration = float(ffprobe_data["format"]["duration"])

        # Generate a random timestamp between first 15-20% of the movie.
        timestamp = total_duration * (random.uniform(15, 20) / 100)

        # converting final timestamp into HH:MM:SS format.
        timestamp = str(datetime.timedelta(seconds=int(timestamp)))
        await generate_videosample_from_link(message, replymsg, file_url, duration, headers, filename, timestamp)

    except MessageNotModified:
        pass
    except Exception as error:
        LOGGER(__name__).error(error)
        return await replymsg.edit(
            "Something went wrong! make sure that the url is direct download video url.")


async def telegram_videosample(message, duration):
    """Generate video sample from Telegram Video File."""

    replymsg = await message.reply_text(f"Generating {duration} minute video sample please wait ...", quote=True,)
    try:
        message = message.reply_to_message
        if message.text:
            return await replymsg.edit("Reply to a proper video file to generate screenshots.")

        if message.media.value in ["video", "document",]:
            media = getattr(message, message.media.value)

        else:
            return await replymsg.edit("can only generate screenshots from video file....")

        filename = unquote(str(media.file_name))
        mime = media.mime_type
        filesize = media.file_size

        if message.media.value == "document" and "video" not in mime:
            return await message.reply_text("Can only generate sample from a video file. Please wait...", quote=True)

        with tempfile.TemporaryDirectory(dir="download") as temp_dir:
            filepath = os.path.join(temp_dir, filename)
            async for chunk in bot.stream_media(message, limit=5):
                with open(filepath, "ab") as f:
                    f.write(chunk)

            mediainfo_json = json.loads(await async_subprocess(f"mediainfo '{filepath}' --Output=JSON"))
            total_duration = mediainfo_json["media"]["track"][0]["Duration"]
            bitrate = float(filesize) / float(total_duration)
            os.remove(filepath)

            # limit of partial file to be downloaded from given time duration
            download_limit = ((bitrate) * (duration * 60)) * 0.000001
            async for chunk in bot.stream_media(message, limit=int(download_limit)):
                with open(filepath, "ab") as file:
                    file.write(chunk)

            # output_path = f"/{temp_dir}/output_{filename}"
            output_path = os.path.join(temp_dir, "output_" + filename)
            ffmpeg_command = f"ffmpeg -i '{filepath}' -c copy -metadata duration=10000 '{output_path}' "
            await async_subprocess(ffmpeg_command)
            await replymsg.edit("Uploading the video file, Please wait...")

            await message.reply_video(
                video=output_path,
                caption=f"[**{duration}min Sample**] {filename}",
                thumb=thumb_path,
                quote=True)

            await replymsg.delete()

    except Exception as error:
        LOGGER(__name__).error(error)
        return await replymsg.edit(
            "Something went wrong while generating sample video from Telegram file.")


@bot.on_callback_query(filters.regex("videosample_"))
async def videosample_duration(client, callbackquery):
    duration = int(callbackquery.data.split("_")[-1])
    await callbackquery.message.delete()

    message = await client.get_messages(
        callbackquery.message.chat.id, callbackquery.message.reply_to_message.id)

    if message.reply_to_message:
        return await telegram_videosample(message, duration)

    user_input = message.text.split(None, 1)[1]
    if url_match := re.search(r"https://drive\.google\.com/\S+", user_input):
        url = url_match.group(0)
        return await gdrive_videosample(message, url, duration)

    if url_match := re.search(r"https?:\/\/[\w-]+(\.[\w-]+)+(:\d+)?(\/[^\s]*)?", user_input,):
        url = url_match.group(0)
        return await ddl_videosample(message, url, duration)

    return await message.reply_text("This type of link is not supported.", quote=True)


@bot.on_message(filters.command(["sample", "trim"]) & check_auth)
async def video_sample(client: Client, message: Message):
    """Generates video sample from Google Drive links, Telegram files or direct download links."""

    sample_duration_button = [
        [
            InlineKeyboardButton("1min", callback_data="videosample_1"),
            InlineKeyboardButton("3min", callback_data="videosample_3"),
            InlineKeyboardButton("5min", callback_data="videosample_5"),
        ]
    ]

    if not message.reply_to_message and len(message.command) < 2:
        return await message.reply_text(
            "Generates video sample from Google Drive links, Telegram files or direct download links.",
            quote=True)

    return await message.reply_text(
        "Choose where you want to upload the screenshot file.",
        reply_markup=InlineKeyboardMarkup(sample_duration_button),
        quote=True)
