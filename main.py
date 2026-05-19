import asyncio
import os
import re

from telethon import TelegramClient, events
from telethon.sessions import StringSession
from telethon.errors import SessionPasswordNeededError

from motor.motor_asyncio import AsyncIOMotorClient

# ================= IMPORT PLUGINS =================
from userbot_commands import load_userbot
from sticker import load_stickers

from plugins.replywatch import load_replywatch
from plugins.clone import load_clone
from plugins.quotly import load_quotly
from plugins.banall import load_banall
from plugins.broadcast import load_broadcast
from plugins.sangmata import load_sangmata
from plugins.reraid import load_reraid
# ================= CONFIG =================
API_ID = int(os.environ["API_ID"])
API_HASH = os.environ["API_HASH"]
BOT_TOKEN = os.environ["BOT_TOKEN"]
MONGO_URL = os.environ["MONGO_URL"]

# ================= MONGO =================
mongo = AsyncIOMotorClient(MONGO_URL)

db = mongo["userbot"]

users = db["users"]

# ================= BOT CLIENT =================
bot = TelegramClient(
    "bot",
    API_ID,
    API_HASH
)

# ================= STATES =================
user_state = {}

# ================= VALIDATION =================
def is_valid(phone):

    return bool(
        re.match(
            r"^\+[1-9]\d{7,14}$",
            phone
        )
    )

# ================= START =================
@bot.on(events.NewMessage(pattern="/start"))
async def start(event):

    await event.reply(
        "👋 Welcome To SNC USERBOT\n\n"
        "Commands:\n"
        "/login → Login Userbot\n"
        "/status → Check Login Status"
    )

# ================= LOGIN =================
@bot.on(events.NewMessage(pattern="/login"))
async def login(event):

    user_state[event.sender_id] = {
        "step": "phone"
    }

    await event.reply(
        "📱 Send Your Phone Number\n\n"
        "Example:\n"
        "+911234567890"
    )

# ================= STATUS =================
@bot.on(events.NewMessage(pattern="/status"))
async def status(event):

    uid = event.sender_id

    state = user_state.get(uid)

    if not state:

        return await event.reply(
            "❌ No Active Login"
        )

    await event.reply(
        f"📊 STATUS\n\n"
        f"Step: {state.get('step')}\n"
        f"Logged: {'Yes' if state.get('client') else 'No'}"
    )

# ================= MESSAGE HANDLER =================
@bot.on(events.NewMessage)
async def handler(event):

    uid = event.sender_id

    text = event.raw_text or ""

    # ignore commands
    if text.startswith("/"):
        return

    if uid not in user_state:
        return

    state = user_state[uid]

    # ================= PHONE STEP =================
    if state["step"] == "phone":

        if not is_valid(text):

            return await event.reply(
                "❌ Invalid Phone Number"
            )

        try:

            client = TelegramClient(
                StringSession(),
                API_ID,
                API_HASH
            )

            await client.connect()

            await client.send_code_request(text)

            state["phone"] = text
            state["client"] = client
            state["step"] = "otp"

            await event.reply(
                "📩 OTP Sent\n\n"
                "Send OTP Like:\n"
                "1 2 3 4 5"
            )

        except Exception as e:

            await event.reply(
                f"❌ Error:\n{e}"
            )

    # ================= OTP STEP =================
    elif state["step"] == "otp":

        client = state["client"]

        phone = state["phone"]

        try:

            otp = text.replace(" ", "")

            await client.sign_in(
                phone,
                otp
            )

        except SessionPasswordNeededError:

            state["step"] = "password"

            return await event.reply(
                "🔐 2FA Enabled\n\n"
                "Send Your Password"
            )

        except Exception as e:

            return await event.reply(
                f"❌ OTP Error:\n{e}"
            )

        # ================= SAVE SESSION =================
        session = client.session.save()

        await users.update_one(
            {"user_id": uid},
            {"$set": {"session": session}},
            upsert=True
        )

        # ================= LOAD PLUGINS =================
        await load_userbot(client)

        load_stickers(client)

        load_replywatch(client)

        load_clone(client)

        load_quotly(client)

        load_banall(client)

        load_broadcast(client)

        load_sangmata(client)

        load_reraid(client)
        
        await event.reply(
            "✅ LOGIN SUCCESS\n\n"
            "🚀 USERBOT ACTIVATED"
        )

        del user_state[uid]

    # ================= PASSWORD STEP =================
    elif state["step"] == "password":

        client = state["client"]

        try:

            await client.sign_in(
                password=text
            )

        except Exception as e:

            return await event.reply(
                f"❌ 2FA Error:\n{e}"
            )

        # ================= SAVE SESSION =================
        session = client.session.save()

        await users.update_one(
            {"user_id": uid},
            {"$set": {"session": session}},
            upsert=True
        )

        # ================= LOAD PLUGINS =================
        await load_userbot(client)

        load_stickers(client)

        load_replywatch(client)

        load_clone(client)

        load_quotly(client)

        load_banall(client)
        
        load_broadcast(client)

        load_sangmata(client)

        load_reraid(client)
        
        await event.reply(
            "✅ 2FA LOGIN SUCCESS\n\n"
            "🚀 USERBOT ACTIVATED"
        )

        del user_state[uid]

# ================= AUTO RESTORE =================
async def load_all():

    async for user in users.find():

        try:

            session = user.get("session")

            if not session:
                continue

            client = TelegramClient(
                StringSession(session),
                API_ID,
                API_HASH
            )

            await client.start()

            # ================= LOAD PLUGINS =================
            await load_userbot(client)

            load_stickers(client)

            load_replywatch(client)

            load_clone(client)

            load_quotly(client)

            load_banall(client)
            
            load_broadcast(client)

            load_sangmata(client)
            
            load_reraid(client)
            
            print(
                f"✅ Restored User: {user['user_id']}"
            )

        except Exception as e:

            print(
                "❌ Restore Error:",
                e
            )

# ================= MAIN =================
async def main():

    await bot.start(
        bot_token=BOT_TOKEN
    )

    print("🚀 BOT STARTED")

    # restore all userbots
    await load_all()

    print("✅ ALL USERBOTS RESTORED")

    await bot.run_until_disconnected()

# ================= RUN =================
if __name__ == "__main__":

    asyncio.run(main())
