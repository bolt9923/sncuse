import asyncio
import random
import time

from telethon import events

reply_watch = {}
last_reply_time = {}

def load_replywatch(client):

    print("✅ ReplyWatch Loaded")

    # =========================
    # ADD WATCH
    # =========================
    @client.on(events.NewMessage(pattern=r"\.replywatch (.+?) (\d+)"))
    async def add_watch(event):

        user = event.pattern_match.group(1)
        delay = int(event.pattern_match.group(2))

        user = user.replace("@", "").lower()

        messages = [
            "👀 Message detected",
            "🔥 SNC USERBOT ACTIVE",
            "⚡ Auto reply running",
            "😎 User triggered response",
            "💬 Hello there"
        ]

        reply_watch[user] = {
            "delay": delay,
            "messages": messages
        }

        print("WATCH ADDED:", user)

        await event.reply(
            f"✅ Reply watch enabled\n"
            f"👤 User: {user}\n"
            f"⏱ Delay: {delay} sec"
        )

    # =========================
    # AUTO REPLY
    # =========================
    @client.on(events.NewMessage)
    async def auto_reply(event):

        try:

            sender = await event.get_sender()

            if not sender:
                return

            username = ""

            if sender.username:
                username = sender.username.lower()

            user_id = str(sender.id)

            print("MESSAGE FROM:", username, user_id)

            matched = None

            if username in reply_watch:
                matched = username

            elif user_id in reply_watch:
                matched = user_id

            if not matched:
                return

            print("MATCH FOUND:", matched)

            now = time.time()

            if matched in last_reply_time:
                if now - last_reply_time[matched] < 5:
                    return

            last_reply_time[matched] = now

            data = reply_watch[matched]

            await asyncio.sleep(data["delay"])

            msg = random.choice(data["messages"])

            print("SENDING REPLY")

            await event.reply(msg)

        except Exception as e:

            print("AUTO REPLY ERROR:", e)
