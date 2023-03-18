import re
import json
import time
import shlex
import httpx
import asyncio
import requests
import datetime
import subprocess

from urllib.parse import unquote
from requests_toolbelt import MultipartEncoder

from pyrogram.types import Message
from pyrogram import Client, filters
from pyrogram.errors import MessageNotModified

from TelegramBot.helpers.functions import *
from TelegramBot.logging import LOGGER
from TelegramBot.helpers.filters import check_auth
from TelegramBot.helpers.gdrivehelper import GoogleDriveHelper


async def slowpics_collection(message, file_name, path):
    """
    Uploads image(s) to https://slow.pics/ from a specified directory.
    """

    msg = await message.reply_text(
        "uploading generated screenshots to slow.pics.", quote=True)

    img_list = os.listdir(path)
    img_list = sorted(img_list)

    data = {
        "collectionName": f"{unquote(file_name)}",
        "hentai": "false",
        "optimizeImages": "false",
        "public": "false"}

    for i in range(0, len(img_list)):
        data[f"images[{i}].name"] = img_list[i].split(".")[0]
        data[f"images[{i}].file"] = (
            img_list[i],
            open(f"{path}/{img_list[i]}", "rb"),
            "image/png")

    with requests.Session() as client:
        client.get("https://slow.pics/api/collection")
        files = MultipartEncoder(data)
        length = str(files.len)

        headers = {
            "Content-Length": length,
            "Content-Type": files.content_type,
            "Origin": "https://slow.pics/",
            "Referer": "https://slow.pics/collection",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.88 Safari/537.36",
            "X-XSRF-TOKEN": client.cookies.get_dict()["XSRF-TOKEN"]}

        response = client.post(
            "https://slow.pics/api/collection", data=files, headers=headers)
        await msg.edit(
            f"File Name: `{unquote(file_name)}`\n\nFrames: https://slow.pics/c/{response.text}",
            disable_web_page_preview=True)


async def generate_ss_from_file(
    message, replymsg, file_name, frame_count, file_duration
):
    """
    Generates screenshots from partially/fully downloaded files using ffmpeg.
    """

    await replymsg.edit(
        f"Generating **{frame_count}** screnshots from `{unquote(file_name)}`, please wait...")

    rand_str = randstr()
    download_path = f"download/{rand_str}"
    makedir(download_path)

    loop_count = frame_count
    while loop_count != 0:
        random_timestamp = random.uniform(1, file_duration)
        timestamp = str(datetime.timedelta(seconds=int(random_timestamp)))
        outputpath = (
            f"{download_path}/{str((frame_count - loop_count) + 1).zfill(2)}.png")

        ffmpeg_command = f"ffmpeg -y -ss {timestamp} -i 'download/{file_name}' -vframes 1 {outputpath}"
        result = await async_subprocess(ffmpeg_command)
        if "File ended prematurely" in result:
            loop_count += 1
        loop_count -= 1

    await replymsg.delete()
    await slowpics_collection(message, file_name, path=f"{os.getcwd()}/{download_path}")

    shutil.rmtree(download_path)
    os.remove(f"download/{file_name}")


async def generate_ss_from_link(
    message,
    replymsg,
    file_url,
    headers,
    file_name,
    frame_count,
    fps,
    hdr,
    timestamp,
):
    """
    Generates screenshots from direct download links using ffmpeg.
    """

    await replymsg.edit(
        f"Generating **{frame_count}** screnshots from `{unquote(file_name)}`, please wait ...")
    rand_str = randstr()
    download_path = f"download/{rand_str}"
    makedir(download_path)

    vf_flags = (
        f"zscale=transfer=linear,tonemap=tonemap=hable:param=1.0:desat=0:peak=10,zscale=transfer=bt709,format=yuv420p,fps=1/{fps}"
        if hdr
        else f"fps=1/{fps}")

    ffmpeg_command = f"ffmpeg -headers '{headers}' -y -ss {timestamp} -i {file_url} -vf '{vf_flags}' -vframes {frame_count} {download_path}/%02d.png"
    shell_output = await async_subprocess(ffmpeg_command)

    await replymsg.delete()
    await slowpics_collection(message, file_name, path=f"{os.getcwd()}/{download_path}")
    shutil.rmtree(download_path)


async def gdrive_screenshot(message, url, time, frame_count, fps, hdr, dv):
    """
    Generates Screenshots From Google Drive link.
    """

    replymsg = await message.reply_text(
        "Checking your given gdrive link...", quote=True)
    try:
        drive = GoogleDriveHelper()
        metadata = drive.get_metadata(url)
        file_name = metadata["name"]

        if "video" not in metadata["mimeType"]:
            return await replymsg.edit(
                "Can only generate screenshots from video file.**")

        file_url = drive.get_ddl_link(url)
        bearer_token = drive.get_bearer_token()
        headers = f"Authorization: Bearer {bearer_token}"

        total_duration = await async_subprocess(f"ffprobe -headers '{headers}'  -v quiet -show_format -print_format json {file_url}")  
        ffprobe_data = json.loads(total_duration)
        total_duration = float(ffprobe_data["format"]["duration"])

        # Generate a random timestamp between first 15-20% of the movie.
        timestamp = total_duration * (random.uniform(15, 20) / 100)

        # check if manual timestamp is valid or not.
        custom_timestamp = check_and_convert_time(time)
        if custom_timestamp:
            timestamp = (
                custom_timestamp if custom_timestamp < total_duration else timestamp)

        # convering final timestamp into HH:MM:SS format
        timestamp = str(datetime.timedelta(seconds=int(timestamp)))

        await generate_ss_from_link(
            message,
            replymsg,
            file_url,
            headers,
            file_name,
            frame_count,
            fps,
            hdr,
            timestamp)

    except MessageNotModified:
        pass
    except Exception as error:
        LOGGER(__name__).error(f"{error}{url}")
        return await replymsg.edit(
            "Something went wrong while processing gdrive link. Make sure that the gdrive link is public and not rate limited. ")


async def ddl_screenshot(message, url, time, frame_count, fps, hdr, dv):
    """
    Generates Screenshots from Direct Download link.
    """

    replymsg = await message.reply_text(
        "Checking direct download url....**", quote=True)
    try:
        file_url = f"'{url}'"
        file_name = re.search(".+/(.+)", url).group(1)
        if len(file_name) > 60:
            file_name = file_name[-60:]

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
            timestamp = (custom_timestamp if custom_timestamp < total_duration else timestamp)

        # convering final timestamp into HH:MM:SS format
        timestamp = str(datetime.timedelta(seconds=int(timestamp)))

        await generate_ss_from_link(
            message,
            replymsg,
            file_url,
            headers,
            file_name,
            frame_count,
            fps,
            hdr,
            timestamp)

    except MessageNotModified:
        pass
    except Exception as error:
        LOGGER(__name__).error(f"{error}{url}")
        return await replymsg.edit(
            "Something went wrong! make sure that the url is direct download video url.")


async def telegram_screenshot(client, message, frame_count):
    """
    Generates Screenshots from Telegram Video File.
    """

    replymsg = await message.reply_text(
        "Generating screenshots from Telegram file, please wait...", quote=True)
    try:
        message = message.reply_to_message
        if message.text:
            return await replymsg.edit("Reply to a proper video file to generate screenshots.")

        if message.media.value == "video":
            media = message.video

        elif message.media.value == "document":
            media = message.document

        else:
            return await replymsg.edit(
                "can only generate screenshots from video file....")

        file_name = str(media.file_name)
        mime = media.mime_type
        file_size = media.file_size

        if message.media.value == "document" and "video" not in mime:
            return await replymsg.edit(
                "can only generate screenshots from video file.", quote=True)

        # limit of partial file to be downloaded for generating screenshots ( i.e, 150mb).
        download_limit: int = 150 * 1024 * 1024

        async for chunk in client.stream_media(message, limit=150):
            with open(f"download/{file_name}", "ab") as file:
                file.write(chunk)

        # percentage of file that got downloaded.
        await replymsg.edit("Partial file downloaded...")

        if file_size < download_limit:
            downloaded_percentage = 100
        else:
            downloaded_percentage = (download_limit / file_size) * 100

        mediainfo_json = await async_subprocess(
            f"mediainfo 'download/{file_name}' --Output=JSON")
        mediainfo_json = json.loads(mediainfo_json)
        total_duration = mediainfo_json["media"]["track"][0]["Duration"]

        partial_file_duration = (
            float(total_duration)
            if downloaded_percentage == 100
            else (downloaded_percentage * float(total_duration)) / 100)

        await generate_ss_from_file(
            message,
            replymsg,
            file_name,
            frame_count,
            file_duration=partial_file_duration)

    except MessageNotModified:
        pass
    except Exception as error:
        LOGGER(__name__).error(error)
        return await replymsg.edit(
            "Something went wrong while generating screenshots from Telegram file.")


screenshot_help = """Generates screenshots from Google Drive links, Telegram files, or direct download links.

**--➜ Command - --**

/ss or /screenshot [GDrive Link] or [DDL Link] or [Reply to Telegram file]

**--➜ Additional Flags - --**

`--count=10`  __[Number of screenshots. Default 10, Max 20]__
`--fps=10`  __[Difference between two consecutive screenshots in seconds. Default 5, Max 15]__
`--time=01:20:10`  __[Time from where the screenshots should be taken in HH:MM:SS format]__
`--hdr`  __[For HDR Videos]__

[ **Only** `--count` **flag will work for Telegram Files** ]

`/ss https://videolink.mkv --count=10 --fps=1 --hdr --time=00:20:00`"""


@Client.on_message(filters.command(["screenshot", "ss"]) & check_auth)
async def screenshot(client: Client, message: Message):
    """
    Generates Screenshots from ddl, gdrive or Telegram files.
    """

    if message.reply_to_message:
        frame_count = 10
        if len(message.command) > 1:
            user_input = message.text.split(None, 1)[1]
            match = re.search(r"(-|--)count=(\d+)", user_input)
            frame_count = int(match[2]) if match and match[2].isdigit() else 10
            frame_count = min(frame_count, 20)
        return await telegram_screenshot(client, message, frame_count)

    if len(message.command) < 2:
        return await message.reply_text(screenshot_help, quote=True)

    user_input = message.text.split(None, 1)[1]
    match = re.search(r"(-|--)fps=(\d+)", user_input)
    fps = int(match[2]) if match and match[2].isdigit() else 5
    fps = min(fps, 15)

    match = re.search(r"(-|--)count=(\d+)", user_input)
    frame_count = int(match[2]) if match and match[2].isdigit() else 10
    frame_count = min(frame_count, 20)

    match = re.search("--time=(\d{2}:\d{2}:\d{2})", user_input)
    time = match.group(1) if match else None

    hdr: bool = bool(re.search(r"(-|--)(hdr|HDR)", user_input))
    dv: bool = bool(re.search(r"(-|--)(dv|DV)", user_input))

    if url_match := re.search(r"https://drive\.google\.com/\S+", user_input):
        url = url_match.group(0)
        return await gdrive_screenshot(message, url, time, frame_count, fps, hdr, dv)

    if url_match := re.search(
        r"https?://([\w_-]+(?:(?:\.[\w_-]+)+))([\w.,@?^=%&:\/~+#-]*[\w@?^=%&\/~+#-])",
        user_input,
    ):
        url = url_match.group(0)
        return await ddl_screenshot(message, url, time, frame_count, fps, hdr, dv)
    return await message.reply_text(
        "This type of link is not supported.", quote=True)
