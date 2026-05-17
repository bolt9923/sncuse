import asyncio
import os
import re

from telethon import TelegramClient, events
from telethon.sessions import StringSession
from telethon.errors import SessionPasswordNeededError

from motor.motor_asyncio import AsyncIOMotorClient
from userbot_commands import load_userbot

# ================= CONFIG =================
API_ID = int(os.environ.get("API_ID", "0"))
API_HASH = os.environ.get("API_HASH", "")
BOT_TOKEN = os.environ.get("BOT_TOKEN", "")
MONGO_URL = os.environ.get("MONGO_URL")

# ================= MONGO =================
mongo = AsyncIOMotorClient(MONGO_URL)
db = mongo["userbot"]
users = db["users"]

# ================= BOT =================
bot = TelegramClient("bot", API_ID, API_HASH)

user_state = {}

# ================= PHONE CHECK =================
def is_valid(phone):
    return bool(re.match(r"^\+[1-9]\d{7,14}$", phone))

# ================= START =================
@bot.on(events.NewMessage(pattern="/start"))
async def start(event):
    await event.reply("👋 /login start karo\n/status check karo")

# ================= LOGIN =================
@bot.on(events.NewMessage(pattern="/login"))
async def login(event):
    user_state[event.sender_id] = {"step": "phone"}
    await event.reply("📱 Phone number send karo")

# ================= STATUS =================
@bot.on(events.NewMessage(pattern="/status"))
async def status(event):

    uid = event.sender_id
    data = user_state.get(uid)

    if not data:
        return await event.reply("❌ Not logged in")

    client = data.get("client")

    await event.reply(f"""
📊 STATUS

Step: {data.get("step")}
Logged: {'Yes' if client else 'No'}
""")

# ================= HANDLER =================
@bot.on(events.NewMessage)
async def handler(event):

    uid = event.sender_id
    text = event.raw_text or ""

    if uid not in user_state:
        return

    state = user_state[uid]

    # ---------------- PHONE ----------------
    if state["step"] == "phone":

        if not is_valid(text):
            return await event.reply("❌ Invalid number")

        client = TelegramClient(StringSession(), API_ID, API_HASH)
        await client.connect()

        try:
            await client.send_code_request(text)

            state["phone"] = text
            state["client"] = client
            state["step"] = "otp"

            await event.reply("📩 OTP send karo")

        except Exception as e:
            await event.reply(str(e))

    # ---------------- OTP ----------------
    elif state["step"] == "otp":

        client = state["client"]

        try:
            await client.sign_in(state["phone"], text)

        except SessionPasswordNeededError:
            state["step"] = "password"
            return await event.reply("🔐 2FA password bhejo")

        except Exception as e:
            return await event.reply(str(e))

        session = client.session.save()

        await users.update_one(
            {"user_id": uid},
            {"$set": {
                "session": session,
                "sticker_on": False,
                "sticker_delay": 0,
                "sticker_pack": None
            }},
            upsert=True
        )

        await event.reply("✅ LOGIN SUCCESS")

        await load_userbot(client)

        await client.run_until_disconnected()

        del user_state[uid]

    # ---------------- PASSWORD ----------------
    elif state["step"] == "password":

        client = state["client"]

        try:
            await client.sign_in(password=text)

        except Exception as e:
            return await event.reply(str(e))

        session = client.session.save()

        await users.update_one(
            {"user_id": uid},
            {"$set": {
                "session": session,
                "sticker_on": False
            }},
            upsert=True
        )

        await event.reply("✅ 2FA LOGIN SUCCESS")

        await load_userbot(client)

        await client.run_until_disconnected()

        del user_state[uid]

# ================= RESTORE SESSIONS =================
async def load_all():

    async for user in users.find():

        session = user["session"]

        client = TelegramClient(StringSession(session), API_ID, API_HASH)

        await client.start()

        await load_userbot(client)

        print("Restored:", user["user_id"])

# ================= RUN =================
async def main():

    await bot.start(bot_token=BOT_TOKEN)

    print("Bot running...")

    await load_all()

    await bot.run_until_disconnected()

asyncio.run(main())
