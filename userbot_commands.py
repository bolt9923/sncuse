import asyncio
from telethon import events

# ================= GLOBAL STATES =================
tag_running = {}
tag_paused = {}
auto_react = {}
auto_clone = {}

tag_delay = {}
utag_delay = {}
tagall_delay = {}

# =====================================================
# LOAD USERBOT
# =====================================================
async def load_userbot(client):

    print("✅ Loading Commands")

    # ================= PING =================
    @client.on(events.NewMessage(outgoing=True, pattern=r"\.ping"))
    async def ping(event):
        await event.reply("🏓 SHINU USERBOT WORKING")

    # ================= HELP =================
    @client.on(events.NewMessage(outgoing=True, pattern=r"\.help"))
    async def help_cmd(event):

        text = """
🔥 SHINU USERBOT 🔥

.ping
.help

.starttag
.stop
.pausetag
.resumetag

.utag
.tagall text

.reaction on/off
.clone on/off

.settagdelay 2
.setutagdelay 2
.settagalldelay 2
"""
        await event.reply(text)

    # ================= STOP =================
    @client.on(events.NewMessage(outgoing=True, pattern=r"\.stop"))
    async def stop_cmd(event):

        uid = event.sender_id
        tag_running[uid] = False

        await event.reply("🛑 STOPPED")

    # ================= PAUSE =================
    @client.on(events.NewMessage(outgoing=True, pattern=r"\.pausetag"))
    async def pause_cmd(event):

        tag_paused[event.sender_id] = True
        await event.reply("⏸ PAUSED")

    # ================= RESUME =================
    @client.on(events.NewMessage(outgoing=True, pattern=r"\.resumetag"))
    async def resume_cmd(event):

        tag_paused[event.sender_id] = False
        await event.reply("▶️ RESUMED")

    # ================= STARTTAG =================
    @client.on(events.NewMessage(outgoing=True, pattern=r"\.starttag"))
    async def starttag(event):

        uid = event.sender_id
        tag_running[uid] = True

        delay = tag_delay.get(uid, 2)
        users = await client.get_participants(event.chat_id)

        await event.reply("🚀 STARTTAG STARTED")

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
                    f"[{user.first_name}](tg://user?id={user.id}) Hello",
                    parse_mode="md"
                )

                await asyncio.sleep(delay)

            except:
                pass

        tag_running[uid] = False
        await event.reply("✅ FINISHED")

    # ================= TAGALL =================
    @client.on(events.NewMessage(outgoing=True, pattern=r"\.tagall (.+)"))
    async def tagall(event):

        uid = event.sender_id
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

    # ================= UTAG =================
    @client.on(events.NewMessage(outgoing=True, pattern=r"\.utag"))
    async def utag(event):

        if not event.is_reply:
            return await event.reply("⚠️ REPLY REQUIRED")

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

    print("✅ ALL COMMANDS LOADED")
