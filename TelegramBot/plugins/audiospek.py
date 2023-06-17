import os

from pyrogram import filters
from pyrogram.types import Message

from TelegramBot import bot
from TelegramBot.helpers.filters import check_auth
from TelegramBot.helpers.functions import async_subprocess
from TelegramBot.helpers.pasting_services import telegraph_image_paste


@bot.on_message(filters.command(["spek", "sox"]) & check_auth)
async def generate_spek(_, message: Message):
    """Generate spectrogram of telegram music file using sox tool."""

    replymsg = await message.reply_text("Generating Spectrogram of the audio. Please wait ...", quote=True)

    # Filtering only valid audio files.
    message = message.reply_to_message
    if not message or message.text:
        return await replymsg.edit("Reply to a proper audio file to Generate audio spectrum.")

    if message.media.value in ["audio", "document"]:
        media = getattr(message, message.media.value)

    else:
        return await replymsg.edit("Can only generate spectrum from audio file...")

    filename = str(media.file_name)
    mime = (media.mime_type).lower()

    if message.media.value == "document" and "audio" not in mime:
        return await replymsg.edit("Can only generate spectrum from audio file...")

    # Downloading the audio file in download folder.
    filepath = f"download/{filename}"
    await message.download(os.path.join(os.getcwd(), "download", filename))

    # Creating spectrogram of audio file.
    if "m4a" in mime or "audio/mp4" in mime:
        await async_subprocess(f"ffmpeg -i '{filepath}' -f flac '{filepath}.flac'")
        await async_subprocess(f"sox '{filepath}.flac' -n remix 1 spectrogram -x 1000  -y 513 -z 120 -w Kaiser -o '{filepath}.png'")

        os.remove(f"{filepath}.flac")

    else:
        await async_subprocess(f"sox '{filepath}' -n remix 1 spectrogram -x 1000 -y 513 -z 120 -w Kaiser -o '{filepath}.png'")

    if not os.path.exists(f"{filepath}.png"):
        return await replymsg.edit("Can not able to generate spectograph of given audio.")

    # Pasting the spectrogram image to telegraph.
    image_url = await telegraph_image_paste(f"{filepath}.png")
    await message.reply_text(f"[{filename}]({image_url})", quote=True)
    await replymsg.delete()

    # Removing the downloaded files from the server.
    os.remove(filepath)
    os.remove(f"{filepath}.png")
