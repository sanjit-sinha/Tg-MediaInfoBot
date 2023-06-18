import re
import os
import json
import random
import datetime
import tempfile
import urllib.parse
from urllib.parse import unquote

from pyrogram.types import (
    Message,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    CallbackQuery,
    InputMediaPhoto,
    InputMediaDocument,
)

from pyrogram import enums
from pyrogram import Client, filters
from pyrogram.errors import MessageNotModified, PhotoSaveFileInvalid

from TelegramBot import bot
from TelegramBot.logging import LOGGER
from TelegramBot.helpers.filters import check_auth
from TelegramBot.helpers.gdrivehelper import GoogleDriveHelper
from TelegramBot.helpers.pasting_services import slowpics_paste
from TelegramBot.helpers.functions import async_subprocess, check_and_convert_time


async def upload_screenshots(
    upload_medium: str, message: Message, filename: str, file_path: str
) -> None:
    """Uploads Screenshots as Telegram photos/documents or in slowpics website."""

    if upload_medium == "slowpics":
        return await slowpics_paste(message, filename, path=file_path)

    await bot.send_chat_action(message.chat.id, action=enums.ChatAction.UPLOAD_PHOTO)
    uploading_msg = await message.reply_text(f"**Uploading {filename} screenshots ...**", quote=True)

    try:
        images = os.listdir(file_path)
        if len(images) == 1 or len(images) > 10:
            for i, image in enumerate(images):

                if upload_medium == "file":
                    await message.reply_document(f"{file_path}/{image}", quote=(i == 0))

                elif upload_medium == "photo":
                    await message.reply_photo(f"{file_path}/{image}", quote=(i == 0))
                    print(2)

            return await uploading_msg.delete()

        InputMedia = InputMediaDocument if upload_medium == "file" else InputMediaPhoto
        images_list = [InputMedia(f"{file_path}/{image}") for image in images]

        await message.reply_media_group(media=images_list, quote=True)

    except PhotoSaveFileInvalid:
        return await uploading_msg.edit("Something went wrong while uploading screenshots as photos. Try to upload screenshots as Telegram (file).")

    return await uploading_msg.delete()


async def generate_ss_from_link(
    message, replymsg, file_url, headers, filename, frame_count, fps, hdr, timestamp, upload_medium
) -> None:
    """Generates screenshots from direct download links using ffmpeg."""

    filename = unquote(filename)
    await replymsg.edit(f"Generating **{frame_count}** screenshots from `{filename}`, please wait ...")

    vf_flags = (
        f"zscale=transfer=linear,tonemap=tonemap=hable:param=1.0:desat=0:peak=10,zscale=transfer=bt709,format=yuv420p,fps=1/{fps}"
        if hdr
        else f"fps=1/{fps}")

    with tempfile.TemporaryDirectory(dir="download") as temp_dir:
        ffmpeg_command = f"ffmpeg -headers '{headers}' -y -ss {timestamp} -i {file_url} -vf '{vf_flags}' -vframes {frame_count} {temp_dir}/%02d.png"
        await async_subprocess(ffmpeg_command)

        await replymsg.delete()
        return await upload_screenshots(upload_medium, message, filename, temp_dir)


async def gdrive_screenshot(message, url, time, frame_count, fps, hdr, upload_medium) -> None:
    """Generates Screenshots From Google Drive link."""

    replymsg = await message.reply_text("Checking your given gdrive link ...", quote=True)
    try:
        gdrive = GoogleDriveHelper()
        metadata = gdrive.get_metadata(url)
        filename = metadata["name"]

        if "video" not in metadata["mimeType"]:
            return await replymsg.edit("Can only generate screenshots from video files.")

        file_url = gdrive.get_ddl_link(url)
        bearer_token = gdrive.get_bearer_token()

        headers = f"Authorization: Bearer {bearer_token}"
        total_duration = await async_subprocess(f"ffprobe -headers '{headers}'  -v quiet -show_format -print_format json {file_url}")
        ffprobe_data = json.loads(total_duration)
        total_duration = float(ffprobe_data["format"]["duration"])

        # Generate a random timestamp between first 15-20% of the movie.
        timestamp = total_duration * (random.uniform(15, 20) / 100)

        # check if manual timestamp is valid or not.
        custom_timestamp = check_and_convert_time(time)
        if custom_timestamp:
            timestamp = (custom_timestamp if custom_timestamp < total_duration else timestamp)

        # converting final timestamp into HH:MM:SS format
        timestamp = str(datetime.timedelta(seconds=int(timestamp)))

        await generate_ss_from_link(
            message, replymsg, file_url, headers, filename, frame_count, fps, hdr, timestamp, upload_medium)

    except MessageNotModified: pass
    except Exception as error:
        LOGGER(__name__).error(f"{error}\n{url}")
        return await message.reply_text(
            "Something went wrong while processing gdrive link. Make sure that the gdrive link is public and not rate limited.", quote=True)


async def ddl_screenshot(message, url, time, frame_count, fps, hdr, upload_medium) -> None:
    """Generates Screenshots from Direct Download link."""

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

        # check if manual timestamp is valid or not.
        custom_timestamp = check_and_convert_time(time)
        if custom_timestamp:
            timestamp = (custom_timestamp if custom_timestamp <  total_duration else timestamp)

        # converting final timestamp into HH:MM:SS format
        timestamp = str(datetime.timedelta(seconds=int(timestamp)))

        await generate_ss_from_link(
            message, replymsg, file_url, headers, filename, frame_count, fps, hdr, timestamp, upload_medium)

    except MessageNotModified: pass
    except Exception as error:
        LOGGER(__name__).error(f"{error}\n{url}")
        return await message.reply_text(
            "Something went wrong! make sure that the url is direct download video url.", quote=True)


async def telegram_screenshot(message, frame_count, upload_medium):
    """Generates Screenshots from Telegram Video File."""

    replymsg = await message.reply_text("Generating screenshots from Telegram file, please wait...", quote=True)
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
            return await replymsg.edit("can only generate screenshots from video file.", quote=True)

        # limit of partial file to be downloaded for generating screenshots ( i.e, 150mb).
        download_limit: int = 150 * 1024 * 1024

        # Calculating downloaded percentage.
        if filesize < download_limit:
            downloaded_percentage = 100
        else:
            downloaded_percentage = (download_limit / filesize) * 100

        # Creating a temporary directory to store partial file.
        with tempfile.NamedTemporaryFile(suffix=f"_{filename}", dir="download") as download_path:
            async for chunk in bot.stream_media(message, limit=150):
                with open(download_path.name, "ab") as file:
                    file.write(chunk)

            # percentage of file that got downloaded.
            await replymsg.edit("Partial file downloaded...")

            # Generating mediainfo json to get total duration of the video file.
            mediainfo_json = json.loads(await async_subprocess(f"mediainfo '{download_path.name}' --Output=JSON"))
            total_duration = mediainfo_json["media"]["track"][0]["Duration"]

            # Calculating partial file duration with the help of downloaded percentage.
            partial_file_duration = (
                float(total_duration)
                if downloaded_percentage == 100
                else (downloaded_percentage * float(total_duration)) / 100)

            with tempfile.TemporaryDirectory(dir="download") as temp_dir:
                loop_count = frame_count
                while loop_count != 0:
                    random_timestamp = random.uniform(1, partial_file_duration)
                    timestamp = str(datetime.timedelta(
                        seconds=int(random_timestamp)))
                    outputpath = f"{temp_dir}/{str((frame_count - loop_count) + 1).zfill(2)}.png"

                    ffmpeg_command = f"ffmpeg -y -ss {timestamp} -i '{download_path.name}' -vframes 1 {outputpath}"
                    result = await async_subprocess(ffmpeg_command)
                    if "File ended prematurely" in result:
                        loop_count += 1
                    loop_count -= 1

                await replymsg.delete()
                await upload_screenshots(upload_medium, message, filename, temp_dir)

    except MessageNotModified: pass
    except Exception as error:
        LOGGER(__name__).error(error)
        return await replymsg.edit(
            "Something went wrong while generating screenshots from Telegram file.")


screenshot_help = """Generates screenshots from Google Drive links, Telegram files, or direct download links.

**--➜ Command - --**

/ss or /screenshot [ GDrive Link ] or [ DDL Link ] or [ Reply to Telegram file ]

**--➜ Additional Flags - --**

`--count=10` [ Number of screenshots. Default 10, Max 20 ]
`--fps=10`  [ Difference between two consecutive screenshots in seconds. Default 10, Max 20 ]
`--time=01:20:10`  [ Time from where the screenshots should be taken in HH:MM:SS format ]
`--hdr`  [ For HDR Videos ]

[ **For Telegram Files Only `--count` flag will work** ]

`/ss https://videolink.mkv --count=10 --fps=1 --hdr --time=00:20:00`"""


@bot.on_callback_query(filters.regex("screenshot_"))
async def callback_screenshot(client: Client, callbackquery: CallbackQuery):
    """Generates Screenshots from ddl, gdrive or Telegram files."""

    upload_medium = callbackquery.data.split("_")[1]
    await callbackquery.message.delete()

    message = await client.get_messages(
        callbackquery.message.chat.id, callbackquery.message.reply_to_message.id)

    command = message.text.split(" ")
    if message.reply_to_message:
        frame_count = 5
        if len(command) > 1:
            user_input = message.text.split(None, 1)[1]
            match = re.search(r"(-|--)count=(\d+)", user_input)
            frame_count = int(match[2]) if match and match[2].isdigit() else 5
            frame_count = min(frame_count, 20)
        return await telegram_screenshot(message, frame_count, upload_medium)

    if len(command) < 2:
        return await message.reply_text(screenshot_help, quote=True)

    user_input = message.text.split(None, 1)[1]
    match = re.search(r"(-|--)fps=(\d+)", user_input)
    fps = int(match[2]) if match and match[2].isdigit() else 10
    fps = min(fps, 20)

    match = re.search(r"(-|--)count=(\d+)", user_input)
    frame_count = int(match[2]) if match and match[2].isdigit() else 5
    frame_count = min(frame_count, 20)

    match = re.search("--time=(\d{2}:\d{2}:\d{2})", user_input)
    time = match.group(1) if match else None

    hdr = bool(re.search(r"(-|--)(hdr|HDR)", user_input))

    if url_match := re.search(r"https://drive\.google\.com/\S+", user_input):
        url = url_match.group(0)
        return await gdrive_screenshot(message, url, time, frame_count, fps, hdr, upload_medium)

    if url_match := re.search(r"https?:\/\/[\w-]+(\.[\w-]+)+(:\d+)?(\/[^\s]*)?", user_input,):
        url = url_match.group(0)
        return await ddl_screenshot(message, url, time, frame_count, fps, hdr, upload_medium)

    return await message.reply_text("This type of link is not supported.", quote=True)


@Client.on_message(filters.command(["screenshots", "ss"]) & check_auth)
async def screenshot(client: Client, message: Message):
    upload_choose_button = [
        [
            InlineKeyboardButton("Telegram (Photo)",callback_data="screenshot_photo"),
            InlineKeyboardButton("Telegram (File)", callback_data="screenshot_file"),
        ],
        [
            InlineKeyboardButton("slow.pics", callback_data="screenshot_slowpics"),
        ],
    ]

    if not message.reply_to_message and len(message.command) < 2:
        return await message.reply_text(screenshot_help, quote=True)

    return await message.reply_text(
        "Choose where you want to upload the screenshot file.",
        reply_markup=InlineKeyboardMarkup(upload_choose_button),
        quote=True)
