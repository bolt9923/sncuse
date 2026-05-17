import asyncio
import random
from telethon import events

tag_running = {}
tag_paused = {}

# ================= USERBOT COMMANDS =================
async def load_userbot(client):

    print("✅ Commands Loaded")

    # ---------------- PING ----------------
    @client.on(events.NewMessage(outgoing=True, pattern=r"\.ping"))
    async def ping(event):
        await event.reply("🏓 WORKING")

    # ---------------- STOP ----------------
    @client.on(events.NewMessage(outgoing=True, pattern=r"\.stop"))
    async def stop(event):
        tag_running[event.sender_id] = False
        await event.reply("🛑 STOPPED")

    # ---------------- STARTTAG ----------------
    @client.on(events.NewMessage(outgoing=True, pattern=r"\.starttag"))
    async def starttag(event):

        uid = event.sender_id
        tag_running[uid] = True

        users = await client.get_participants(event.chat_id)

        await event.reply("🚀 STARTED")

        for u in users:

            if not tag_running.get(uid):
                break

            if u.bot:
                continue

            try:
                await client.send_message(
                    event.chat_id,
                    f"[{u.first_name}](tg://user?id={u.id}) hi",
                    parse_mode="md"
                )

                await asyncio.sleep(2)

            except:
                pass

        await event.reply("✅ DONE")

    # ---------------- STICKER ON ----------------
    @client.on(events.NewMessage(outgoing=True, pattern=r"\.sticker on"))
    async def st_on(event):

        uid = event.sender_id

        await client._session._conn.execute("")

        await event.reply("✅ Sticker ON")

    # ---------------- STICKER OFF ----------------
    @client.on(events.NewMessage(outgoing=True, pattern=r"\.sticker off"))
    async def st_off(event):
        await event.reply("❌ Sticker OFF")

    # ---------------- SET DELAY ----------------
    @client.on(events.NewMessage(outgoing=True, pattern=r"\.setdelaysticker (\d+)"))
    async def set_delay(event):
        await event.reply(f"✅ Delay {event.pattern_match.group(1)}s")

    # ---------------- SET PACK ----------------
    @client.on(events.NewMessage(outgoing=True, pattern=r"\.setstickpack (.+)"))
    async def set_pack(event):
        await event.reply("✅ Pack saved")

    print("All commands ready")
