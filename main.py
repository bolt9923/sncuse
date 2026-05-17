import asyncio
from telethon import TelegramClient, events
from telethon.sessions import StringSession
from config import API_ID, API_HASH, BOT_TOKEN

bot = TelegramClient("bot", API_ID, API_HASH)

sessions = {}

@bot.on(events.NewMessage(pattern="/start"))
async def start(event):
    await event.reply("👋 Welcome!\nUse /login to start userbot")

@bot.on(events.NewMessage(pattern="/login"))
async def login(event):
    user_id = event.sender_id

    await event.reply("📱 Send your phone number:")

    @bot.on(events.NewMessage(from_users=user_id))
    async def get_phone(msg):
        phone = msg.text

        client = TelegramClient(StringSession(), API_ID, API_HASH)
        await client.connect()

        try:
            await client.send_code_request(phone)
            await msg.reply("📩 OTP sent. Send OTP now")

            @bot.on(events.NewMessage(from_users=user_id))
            async def get_code(code_msg):
                try:
                    await client.sign_in(phone, code_msg.text)

                except Exception as e:
                    await code_msg.reply(f"❌ Error: {e}")
                    return

                session = client.session.save()
                sessions[user_id] = session

                await code_msg.reply("✅ Userbot login successful!")

                await client.disconnect()

        except Exception as e:
            await msg.reply(f"❌ Failed: {e}")

async def main():
    await bot.start(bot_token=BOT_TOKEN)
    print("Bot is running...")
    await bot.run_until_disconnected()

if __name__ == "__main__":
    asyncio.run(main())
