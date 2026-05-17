import asyncio
import random
from telethon import events

# ================= STATES =================
tag_running = {}
tag_paused = {}

# =====================================================
# LOAD USERBOT COMMANDS
# =====================================================
async def load_userbot(client):

    print("✅ USERBOT COMMANDS LOADING")

    # =====================================================
    # PING
    # =====================================================
    @client.on(events.NewMessage(outgoing=True, pattern=r"\.ping"))
    async def ping(event):
        await event.reply("🏓 USERBOT WORKING")

    # =====================================================
    # HELP
    # =====================================================
    @client.on(events.NewMessage(outgoing=True, pattern=r"\.help"))
    async def help_cmd(event):

        text = (
            "🔥 USERBOT COMMANDS 🔥\n\n"
            ".ping\n"
            ".help\n"
            ".starttag\n"
            ".stop\n"
            ".pausetag\n"
            ".resumetag\n"
            ".tagall <text>\n"
            ".utag (reply message)\n"
        )

        await event.reply(text)

    # =====================================================
    # STOP
    # =====================================================
    @client.on(events.NewMessage(outgoing=True, pattern=r"\.stop"))
    async def stop_cmd(event):

        uid = event.sender_id
        tag_running[uid] = False

        await event.reply("🛑 STOPPED")

    # =====================================================
    # PAUSE TAG
    # =====================================================
    @client.on(events.NewMessage(outgoing=True, pattern=r"\.pausetag"))
    async def pause_cmd(event):

        tag_paused[event.sender_id] = True
        await event.reply("⏸ PAUSED")

    # =====================================================
    # RESUME TAG
    # =====================================================
    @client.on(events.NewMessage(outgoing=True, pattern=r"\.resumetag"))
    async def resume_cmd(event):

        tag_paused[event.sender_id] = False
        await event.reply("▶️ RESUMED")

    # =====================================================
    # STARTTAG
    # =====================================================
    @client.on(events.NewMessage(outgoing=True, pattern=r"\.starttag"))
    async def starttag(event):

        uid = event.sender_id

        if tag_running.get(uid):
            return await event.reply("⚠️ Already running")

        tag_running[uid] = True

        users = await client.get_participants(event.chat_id)

        await event.reply("🚀 STARTTAG STARTED")

        count = 0

        for user in users:

            if not tag_running.get(uid):
                break

            while tag_paused.get(uid):
                await asyncio.sleep(1)

            if user.bot:
                continue

            try:
                await client.send_message(
                    event.chat_id,
                    f"[{user.first_name}](tg://user?id={user.id}) hi",
                    parse_mode="md"
                )

                count += 1
                await asyncio.sleep(2)

            except:
                pass

        tag_running[uid] = False
        await event.reply(f"✅ FINISHED {count}")

    # =====================================================
    # TAGALL
    # =====================================================
    @client.on(events.NewMessage(outgoing=True, pattern=r"\.tagall (.+)"))
    async def tagall(event):

        text = event.pattern_match.group(1)

        users = await client.get_participants(event.chat_id)

        await event.reply("🚀 TAGALL STARTED")

        for user in users:

            if user.bot:
                continue

            try:
                await client.send_message(
                    event.chat_id,
                    f"[{user.first_name}](tg://user?id={user.id}) {text}",
                    parse_mode="md"
                )

                await asyncio.sleep(2)

            except:
                pass

        await event.reply("✅ TAGALL FINISHED")

    # =====================================================
    # UTAG
    # =====================================================
    @client.on(events.NewMessage(outgoing=True, pattern=r"\.utag"))
    async def utag(event):

        if not event.is_reply:
            return await event.reply("⚠️ Reply to message required")

        reply = await event.get_reply_message()

        users = await client.get_participants(event.chat_id)

        await event.reply("🚀 UTAG STARTED")

        for user in users:

            if user.bot:
                continue

            try:
                await client.send_message(
                    event.chat_id,
                    f"[{user.first_name}](tg://user?id={user.id}) {reply.text}",
                    parse_mode="md"
                )

                await asyncio.sleep(2)

            except:
                pass

        await event.reply("✅ UTAG FINISHED")

    print("✅ USERBOT COMMANDS LOADED SUCCESSFULLY")
