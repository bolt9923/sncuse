import asyncio
import os
import re

from telethon import TelegramClient, events
from telethon.sessions import StringSession
from telethon.errors import SessionPasswordNeededError

from motor.motor_asyncio import AsyncIOMotorClient

from userbot_commands import load_userbot
from sticker import load_stickers

# ================= CONFIG =================
API_ID = int(os.environ.get("API_ID", "0"))
API_HASH = os.environ.get("API_HASH", "")
BOT_TOKEN = os.environ.get("BOT_TOKEN", "")
MONGO_URL = os.environ.get("MONGO_URL")

# ================= MONGO =================
mongo = AsyncIOMotorClient(MONGO_URL)
db = mongo["userbot"]
users = db["users"]

# ================= BOT CLIENT =================
bot = TelegramClient("bot", API_ID, API_HASH)

# ================= STATE =================
user_state = {}

# ================= VALID PHONE =================
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
    await event.reply("📱 Phone number bhejo (+91...)")

# ================= STATUS =================
@bot.on(events.NewMessage(pattern="/status"))
async def status(event):

    uid = event.sender_id
    state = user_state.get(uid)

    if not state:
        return await event.reply("❌ Not logged in")

    await event.reply(f"""
📊 STATUS

Step: {state.get("step")}
Logged: {'Yes' if state.get("client") else 'No'}
""")

# ================= CORE HANDLER =================
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
            return await event.reply("❌ Invalid number (+91...)")

        client = TelegramClient(StringSession(), API_ID, API_HASH)
        await client.connect()

        try:
            await client.send_code_request(text)

            state["phone"] = text
            state["client"] = client
            state["step"] = "otp"

            await event.reply("📩 OTP bhejo")

        except Exception as e:
            await event.reply(f"❌ Error:\n{e}")

    # ---------------- OTP ----------------
    elif state["step"] == "otp":

        client = state["client"]
        phone = state["phone"]

        try:
            await client.sign_in(phone, text)

        except SessionPasswordNeededError:
            state["step"] = "password"
            return await event.reply("🔐 2FA password bhejo")

        except Exception as e:
            return await event.reply(f"❌ OTP Error:\n{e}")

        session = client.session.save()

        await users.update_one(
            {"user_id": uid},
            {"$set": {
                "session": session,
                "sticker_on": False
            }},
            upsert=True
        )

        await event.reply("✅ LOGIN SUCCESS")

        # ================= SAFE LOAD =================
        await load_userbot(client)
        load_stickers(client)

        del user_state[uid]

    # ---------------- PASSWORD ----------------
    elif state["step"] == "password":

        client = state["client"]

        try:
            await client.sign_in(password=text)

        except Exception as e:
            return await event.reply(f"❌ 2FA Error:\n{e}")

        session = client.session.save()

        await users.update_one(
            {"user_id": uid},
            {"$set": {"session": session}},
            upsert=True
        )

        await event.reply("✅ 2FA LOGIN SUCCESS")

        # ================= SAFE LOAD =================
        await load_userbot(client)
        load_stickers(client)

        del user_state[uid]

# ================= AUTO RESTORE =================
async def load_all():

    async for user in users.find():

        try:
            session = user["session"]

            client = TelegramClient(StringSession(session), API_ID, API_HASH)

            await client.start()

            # load modules
            await load_userbot(client)
            load_stickers(client)

            print("✅ Restored:", user["user_id"])

        except Exception as e:
            print("❌ Restore error:", e)

# ================= MAIN =================
async def main():

    await bot.start(bot_token=BOT_TOKEN)

    print("🚀 Bot Running...")

    await load_all()

    await bot.run_until_disconnected()

if __name__ == "__main__":
    asyncio.run(main())
