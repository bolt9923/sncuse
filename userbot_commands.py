import asyncio
import random
from telethon import events

# ================= STATES =================
tag_running = {}
tag_paused = {}
auto_react = {}
auto_clone = {}

tag_delay = {}
utag_delay = {}
tagall_delay = {}

# ================= LOAD USERBOT =================
async def load_userbot(client):

    print("🔥 SHINU USERBOT LOADED")

    # ================= PING =================
    @client.on(events.NewMessage(outgoing=True, pattern=r"\.ping"))
    async def ping(event):
        await event.reply("🏓 PONG")

    # ================= HELP =================
    @client.on(events.NewMessage(outgoing=True, pattern=r"\.help"))
    async def help_cmd(event):

        await event.reply("""
text = """
 SHINU USERBOT 

.ping
.help

.starttag
.stop
.pausetag
.resumetag

.tagall text
.utag (reply)

.reaction on
.reaction off

.clone on
.clone off

.settagdelay 2
.setutagdelay 2
.settagalldelay 2

 STICKER SYSTEM 
.sticker on
.sticker off
.setstickerdelay 2
.setstickerpack (reply sticker)

    # ================= STOP =================
    @client.on(events.NewMessage(outgoing=True, pattern=r"\.stop"))
    async def stop(event):
        tag_running[event.sender_id] = False
        await event.reply("🛑 STOPPED")

    # ================= PAUSE =================
    @client.on(events.NewMessage(outgoing=True, pattern=r"\.pausetag"))
    async def pause(event):
        tag_paused[event.sender_id] = True
        await event.reply("⏸ PAUSED")

    # ================= RESUME =================
    @client.on(events.NewMessage(outgoing=True, pattern=r"\.resumetag"))
    async def resume(event):
        tag_paused[event.sender_id] = False
        await event.reply("▶️ RESUMED")

    # ================= DELAYS =================
    @client.on(events.NewMessage(outgoing=True, pattern=r"\.settagdelay (\d+)"))
    async def set_tag_delay(event):
        tag_delay[event.sender_id] = int(event.pattern_match.group(1))
        await event.reply("✅ TAG DELAY SET")

    @client.on(events.NewMessage(outgoing=True, pattern=r"\.setutagdelay (\d+)"))
    async def set_utag_delay(event):
        utag_delay[event.sender_id] = int(event.pattern_match.group(1))
        await event.reply("✅ UTAG DELAY SET")

    @client.on(events.NewMessage(outgoing=True, pattern=r"\.settagalldelay (\d+)"))
    async def set_tagall_delay(event):
        tagall_delay[event.sender_id] = int(event.pattern_match.group(1))
        await event.reply("✅ TAGALL DELAY SET")

    # ================= STARTTAG =================
    @client.on(events.NewMessage(outgoing=True, pattern=r"\.starttag"))
    async def starttag(event):

        uid = event.sender_id

        if tag_running.get(uid):
            return await event.reply("⚠️ Already running")

        tag_running[uid] = True

        delay = tag_delay.get(uid, 2)

        users = await client.get_participants(event.chat_id)

        await event.reply("🚀 STARTTAG")

        count = 0

        for u in users:

            if not tag_running.get(uid):
                break

            while tag_paused.get(uid):
                await asyncio.sleep(1)

            if u.bot:
                continue

            try:
                await client.send_message(
                    event.chat_id,
                    f"[{u.first_name}](tg://user?id={u.id}) hi",
                    parse_mode="md"
                )

                count += 1
                await asyncio.sleep(delay)

            except:
                pass

        tag_running[uid] = False
        await event.reply(f"✅ DONE {count}")

    # ================= TAGALL =================
    @client.on(events.NewMessage(outgoing=True, pattern=r"\.tagall (.+)"))
    async def tagall(event):

        text = event.pattern_match.group(1)
        delay = tagall_delay.get(event.sender_id, 2)

        users = await client.get_participants(event.chat_id)

        await event.reply("🚀 TAGALL STARTED")

        for u in users:

            if u.bot:
                continue

            try:
                await client.send_message(
                    event.chat_id,
                    f"[{u.first_name}](tg://user?id={u.id}) {text}",
                    parse_mode="md"
                )

                await asyncio.sleep(delay)

            except:
                pass

        await event.reply("✅ TAGALL DONE")

    # ================= UTAG =================
    @client.on(events.NewMessage(outgoing=True, pattern=r"\.utag"))
    async def utag(event):

        if not event.is_reply:
            return await event.reply("⚠️ Reply required")

        reply = await event.get_reply_message()

        delay = utag_delay.get(event.sender_id, 2)

        users = await client.get_participants(event.chat_id)

        await event.reply("🚀 UTAG STARTED")

        for u in users:

            if u.bot:
                continue

            try:
                await client.send_message(
                    event.chat_id,
                    f"[{u.first_name}](tg://user?id={u.id}) {reply.text}",
                    parse_mode="md"
                )

                await asyncio.sleep(delay)

            except:
                pass

        await event.reply("✅ UTAG DONE")

    # ================= REACTION =================
    @client.on(events.NewMessage(outgoing=True, pattern=r"\.reaction on"))
    async def react_on(event):
        auto_react[event.sender_id] = True
        await event.reply("✅ REACTION ON")

    @client.on(events.NewMessage(outgoing=True, pattern=r"\.reaction off"))
    async def react_off(event):
        auto_react[event.sender_id] = False
        await event.reply("❌ REACTION OFF")

    @client.on(events.NewMessage)
    async def reaction_handler(event):

        uid = event.sender_id

        if not auto_react.get(uid):
            return

        try:
            await event.react(random.choice(["🔥", "👍", "❤️"]))
        except:
            pass

    # ================= CLONE =================
    @client.on(events.NewMessage(outgoing=True, pattern=r"\.clone on"))
    async def clone_on(event):
        auto_clone[event.sender_id] = True
        await event.reply("✅ CLONE ON")

    @client.on(events.NewMessage(outgoing=True, pattern=r"\.clone off"))
    async def clone_off(event):
        auto_clone[event.sender_id] = False
        await event.reply("❌ CLONE OFF")

    print("🔥 ALL COMMANDS LOADED")
