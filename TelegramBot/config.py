import json
from os import getenv
from dotenv import load_dotenv
load_dotenv("config.env") 

API_ID = int(getenv("API_ID"))
API_HASH = getenv("API_HASH")
BOT_TOKEN = getenv("BOT_TOKEN")

COMMAND_PREFIXES = prefixes = dict(prefixes=json.loads(getenv("COMMAND_PREFIXES")))
OWNER_USERID = json.loads(getenv("OWNER_USERID"))
