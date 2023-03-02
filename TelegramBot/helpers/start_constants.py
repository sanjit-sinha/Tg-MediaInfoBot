from TelegramBot.version import (__python_version__, __version__, __pyro_version__)


COMMAND_TEXT = """🗒️ Documentation for commands available to user's 

• /start: To Get start message and help guide. 

• /alive: To check if bot is alive or not.

• /paste: paste text in katb.in website.

• /screenshot or /ss: Generates Screenshot from video file

• /mediainfo or /m: Generates Mediainfo of file. 

• /sample or /trim: Generates Video sample file from a video.

• /spek or /sox: Generates audio Spectogram from Telegram audio files.

"""

ABOUT_CAPTION = f"""• Python version : {__python_version__}
• Bot version : {__version__}
• pyrogram  version : {__pyro_version__}

**Github Repo**: https://github.com/sanjit-sinha/Tg-MediaInfoBot"""

START_ANIMATION = "https://telegra.ph/file/c0857672b427bec8542f6.mp4"

START_CAPTION = """Hey there! I am a simple Telegram Bot which is made for the purpose of generating video files' frames and mediainfo from Telegram files and Google Drive links."""



