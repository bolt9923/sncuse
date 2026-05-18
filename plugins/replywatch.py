import asyncio
import random
import time

from telethon import events

# =========================
# STORAGE
# =========================
reply_watch = {}
last_reply_time = {}

# =========================
# LOAD FUNCTION
# =========================
def load_replywatch(client):

    # =========================
    # ADD WATCH
    # =========================
    @client.on(events.NewMessage(pattern=r"\.replywatch (.+?) (\d+)"))
    async def add_watch(event):

        username = event.pattern_match.group(1)
        delay = int(event.pattern_match.group(2))

        username = username.replace("@", "").lower()

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

        reply_watch[username] = {
            "delay": delay,
            "messages": messages
        }

        await event.reply(
            f"✅ Reply watch enabled\n"
            f"👤 User: @{username}\n"
            f"⏱ Delay: {delay} sec"
        )

    # =========================
    # STOP WATCH
    # =========================
    @client.on(events.NewMessage(pattern=r"\.stopreply (.+)"))
    async def stop_watch(event):

        username = event.pattern_match.group(1)
        username = username.replace("@", "").lower()

        if username in reply_watch:
            del reply_watch[username]
            await event.reply(f"❌ Stopped watching @{username}")
        else:
            await event.reply("⚠ User not found")

    # =========================
    # AUTO REPLY
    # =========================
    @client.on(events.NewMessage)
    async def auto_reply(event):

        if not event.sender:
            return

        if not event.sender.username:
            return

        username = event.sender.username.lower()

        if username not in reply_watch:
            return

        now = time.time()

        # cooldown
        if username in last_reply_time:
            if now - last_reply_time[username] < 15:
                return

        last_reply_time[username] = now

        data = reply_watch[username]

        delay = data["delay"]
        messages = data["messages"]

        await asyncio.sleep(delay)

        msg = random.choice(messages)

        try:
            await event.reply(msg)

        except Exception as e:
            print(e)
