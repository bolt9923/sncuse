import asyncio
import random
from telethon import events
from telethon.tl.functions.messages import GetStickerSetRequest
from telethon.tl.types import InputStickerSetShortName

# ================= STATE =================
sticker_on = {}
sticker_delay = {}
sticker_pack = {}
sticker_task = {}

# ================= LOAD =================
def load_stickers(client):

    print("🟢 STICKER SYSTEM LOADED")

    # ================= ON =================
    @client.on(events.NewMessage(outgoing=True, pattern=r"\.sticker on"))
    async def on(event):

        uid = event.sender_id
        sticker_on[uid] = True

        await event.reply("✅ STICKER ON")

        # start loop only once
        if uid not in sticker_task or sticker_task[uid].done():
            sticker_task[uid] = asyncio.create_task(
                sticker_loop(client, event.chat_id, uid)
            )

    # ================= OFF =================
    @client.on(events.NewMessage(outgoing=True, pattern=r"\.sticker off"))
    async def off(event):

        uid = event.sender_id
        sticker_on[uid] = False

        task = sticker_task.get(uid)
        if task:
            task.cancel()

        await event.reply("❌ STICKER OFF")

    # ================= DELAY =================
    @client.on(events.NewMessage(outgoing=True, pattern=r"\.setstickerdelay (\d+)"))
    async def delay(event):

        sticker_delay[event.sender_id] = int(event.pattern_match.group(1))
        await event.reply(f"⏱ DELAY SET: {sticker_delay[event.sender_id]}s")

    # ================= PACK =================
    @client.on(events.NewMessage(outgoing=True, pattern=r"\.setstickerpack (.+)"))
    async def pack(event):

        raw = event.pattern_match.group(1)

        pack_name = raw.split("/")[-1].strip()

        try:
            result = await client(GetStickerSetRequest(
                stickerset=InputStickerSetShortName(pack_name),
                hash=0
            ))

            if not result or not result.documents:
                return await event.reply("❌ Invalid Sticker Pack")

            sticker_pack[event.sender_id] = pack_name

            await event.reply(f"📦 PACK SAVED:\n{pack_name}")

        except Exception as e:
            await event.reply(f"❌ ERROR:\n{e}")

    print("🔥 STICKER SYSTEM READY")


# ================= LOOP ENGINE =================
async def sticker_loop(client, chat_id, uid):

    while True:

        if not sticker_on.get(uid, False):
            break

        pack = sticker_pack.get(uid)
        if not pack:
            await asyncio.sleep(2)
            continue

        delay = sticker_delay.get(uid, 2)

        try:
            result = await client(GetStickerSetRequest(
                stickerset=InputStickerSetShortName(pack),
                hash=0
            ))

            if result and result.documents:
                sticker = random.choice(result.documents)
                await client.send_file(chat_id, sticker)

        except Exception as e:
            print("STICKER LOOP ERROR:", e)

        await asyncio.sleep(delay)
