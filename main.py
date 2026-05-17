import asyncio
import os
import re

from telethon import TelegramClient, events
from telethon.sessions import StringSession
from telethon.errors import SessionPasswordNeededError

# ================= CONFIG =================
API_ID = int(os.environ.get("API_ID", "0"))
API_HASH = os.environ.get("API_HASH", "")
BOT_TOKEN = os.environ.get("BOT_TOKEN", "")

# ================= CLIENT =================
bot = TelegramClient("bot", API_ID, API_HASH)

# ================= STATES =================
user_state = {}

# ================= LOAD USERBOT IMPORT =================
from userbot_commands import load_userbot   # 👈 your commands file

# ================= PHONE VALIDATION =================
def is_valid_phone(phone: str) -> bool:
    return bool(re.match(r"^\+[1-9]\d{7,14}$", phone))

# ================= START =================
@bot.on(events.NewMessage(pattern="/start"))
async def start(event):
    await event.reply(
        "👋 Welcome!\n\n"
        "👉 /login - Start login\n"
        "👉 /status - Check status"
    )

# ================= LOGIN START =================
@bot.on(events.NewMessage(pattern="/login"))
async def login(event):
    user_id = event.sender_id

    user_state[user_id] = {
        "step": "phone"
    }

    await event.reply("📱 Send your phone number (+91xxxxxxxxxx)")

# ================= STATUS =================
@bot.on(events.NewMessage(pattern="/status"))
async def status(event):

    user_id = event.sender_id
    state = user_state.get(user_id)

    if not state:
        return await event.reply("❌ Not logged in")

    client = state.get("client")
    step = state.get("step")

    alive = False
    if client:
        try:
            alive = client.is_connected()
        except:
            alive = False

    await event.reply(f"""
📊 USERBOT STATUS

🔹 Step: {step}
🔹 Logged In: {'Yes' if client else 'No'}
🔹 Connection: {'🟢 Live' if alive else '🔴 Offline'}
""")

# ================= MAIN HANDLER =================
@bot.on(events.NewMessage)
async def handler(event):

    user_id = event.sender_id
    text = event.raw_text or ""

    if user_id not in user_state:
        return

    state = user_state[user_id]
    step = state.get("step")

    # ================= PHONE =================
    if step == "phone":

        phone = text.strip()

        if not is_valid_phone(phone):
            return await event.reply("❌ Invalid number! Example: +91xxxxxxxxxx")

        client = TelegramClient(StringSession(), API_ID, API_HASH)
        await client.connect()

        try:
            await client.send_code_request(phone)

            state["phone"] = phone
            state["client"] = client
            state["step"] = "otp"

            await event.reply("📩 OTP sent. Send OTP now.")

        except Exception as e:
            await event.reply(f"❌ Error sending OTP:\n{e}")

    # ================= OTP =================
    elif step == "otp":

        otp = text.strip()
        client = state.get("client")
        phone = state.get("phone")

        if not otp or not client:
            return await event.reply("❌ Session expired")

        try:
            await client.sign_in(phone, otp)

        except SessionPasswordNeededError:
            state["step"] = "password"
            return await event.reply("🔐 2FA password send karo:")

        except Exception as e:
            return await event.reply(f"❌ OTP Error:\n{e}")

        # LOGIN SUCCESS
        session = client.session.save()

        await event.reply("✅ Login successful!")

        print(f"\nSESSION:\n{session}\n")

        # 🔥 LOAD USERBOT COMMANDS HERE
        await load_userbot(client)

        await client.run_until_disconnected()

        del user_state[user_id]

    # ================= PASSWORD =================
    elif step == "password":

        password = text.strip()
        client = state.get("client")

        if not password or not client:
            return await event.reply("❌ Invalid password")

        try:
            await client.sign_in(password=password)

        except Exception as e:
            return await event.reply(f"❌ Wrong password:\n{e}")

        session = client.session.save()

        await event.reply("✅ 2FA Login successful!")

        print(f"\nSESSION (2FA):\n{session}\n")

        # 🔥 LOAD USERBOT COMMANDS HERE
        await load_userbot(client)

        await client.run_until_disconnected()

        del user_state[user_id]

# ================= RUN BOT =================
async def main():
    await bot.start(bot_token=BOT_TOKEN)
    print("🚀 Bot is running...")
    await bot.run_until_disconnected()

if __name__ == "__main__":
    asyncio.run(main())
