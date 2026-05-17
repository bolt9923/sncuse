from pyrogram import Client

import os
from pyrogram import Client

API_ID = int(os.environ.get("API_ID", 0))
API_HASH = os.environ.get("API_HASH", "")

app = Client(
    "raid_userbot",
    api_id=API_ID,
    api_hash=API_HASH
)

app = Client(
    "raid_userbot",
    api_id=API_ID,
    api_hash=API_HASH
)
