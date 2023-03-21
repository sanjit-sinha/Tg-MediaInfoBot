import os

from pyrogram.types import Message
from pyrogram import filters, Client

from TelegramBot.helpers.filters import check_auth
from TelegramBot.helpers.functions import async_subprocess
from TelegramBot.helpers.pasting_services import telegraph_image_paste


@Client.on_message(filters.command(["spek", "sox"]) & check_auth)
async def generate_spek(_, message: Message):
    """Generate spectrogram of music file using sox tool."""

    if not message.reply_to_message:
        return await message.reply_text(
            "Reply to a proper audio file to Generate audio spectrum.", quote=True)

    message = message.reply_to_message
    if message.text:
        return await message.reply_text(
            "Reply to a proper audio file to Generate audio spectrum.", quote=True)

    if message.media.value == "audio":
        media = message.audio

    elif message.media.value == "document":
        media = message.document

    else:
        return await message.reply_text(
            "Can only generate spectrum from audio file....", quote=True)

    file_name = str(media.file_name)
    mime = media.mime_type
    if message.media.value == "document" and "audio" not in mime:
        return await message.reply_text(
            "Can only generate spectrum from audio file....", quote=True)

    replymsg = await message.reply_text(
        "Generating Spectrogram of the audio. Please wait...", quote=True)
    await message.download(os.path.join(os.getcwd(), "download", file_name))

    if "m4a" in mime.lower() or "audio/mp4" in mime.lower():
        await async_subprocess(
            f"ffmpeg -i 'download/{file_name}' -f flac 'download/{file_name}.flac'")
        await async_subprocess(
            f"sox 'download/{file_name}.flac' -n remix 1 spectrogram -x 1000  -y 513 -z 120 -w Kaiser -o 'download/{file_name}.png'")
        os.remove(f"download/{file_name}.flac")

    else:
        await async_subprocess(
            f"sox 'download/{file_name}' -n remix 1 spectrogram -x 1000 -y 513 -z 120 -w Kaiser -o 'download/{file_name}.png'")

    if not os.path.exists(f"download/{file_name}.png"):
        return await replymsg.edit(
            "Can not able to generate spectograph of given audio.")

    image_url = await telegraph_image_paste(f"download/{file_name}.png")
    await message.reply_text(f"[{file_name}]({image_url})", quote=True)

    await replymsg.delete()
    os.remove(f"download/{file_name}")
    os.remove(f"download/{file_name}.png")
