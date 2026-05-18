import asyncio
import random
import time

from telethon import events

reply_watch = {}
last_reply_time = {}

def load_replywatch(client):

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
            "💬 Hello there",
            "🚀 Reply system enabled",
            "✨ Watching messages",
            "🎯 Target message detected",
            "🤖 Auto response sent",
            "💥 Reply completed"
        ]

        reply_watch[user] = {
            "delay": delay,
            "messages": messages
        }

        await event.reply(
            f"✅ Reply watch enabled\n"
            f"👤 User: {user}\n"
            f"⏱ Delay: {delay} sec"
        )

    # =========================
    # STOP WATCH
    # =========================
    @client.on(events.NewMessage(pattern=r"\.stopreply (.+)"))
    async def stop_watch(event):

        user = event.pattern_match.group(1)

        user = user.replace("@", "").lower()

        if user in reply_watch:

            del reply_watch[user]

            await event.reply(f"❌ Stopped watching {user}")

    # =========================
    # AUTO REPLY
    # =========================
    @client.on(events.NewMessage)
    async def auto_reply(event):

        try:

            if not event.sender_id:
                return

            sender = await event.get_sender()

            username = ""

            if sender.username:
                username = sender.username.lower()

            user_id = str(sender.id)

            matched = None

            # match username
            if username in reply_watch:
                matched = username

            # match id
            elif user_id in reply_watch:
                matched = user_id

            if not matched:
                return

            now = time.time()

            # anti flood
            if matched in last_reply_time:
                if now - last_reply_time[matched] < 15:
                    return

            last_reply_time[matched] = now

            data = reply_watch[matched]

            delay = data["delay"]

            await asyncio.sleep(delay)

            msg = random.choice(data["messages"])

            await event.reply(msg)

        except Exception as e:

            print("AUTO REPLY ERROR:", e)
