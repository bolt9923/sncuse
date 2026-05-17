import asyncio
import random
from telethon import events
from telethon.tl.functions.messages import GetStickerSetRequest
from telethon.tl.types import InputStickerSetID

sticker_on = {}
sticker_delay = {}
sticker_pack = {}

def load_stickers(client):

    print("🟢 STICKER SYSTEM LOADED")

    # ON
    @client.on(events.NewMessage(outgoing=True, pattern=r"\.sticker on"))
    async def on(event):
        sticker_on[event.sender_id] = True
        await event.reply("✅ STICKER ON")

    # OFF
    @client.on(events.NewMessage(outgoing=True, pattern=r"\.sticker off"))
    async def off(event):
        sticker_on[event.sender_id] = False
        await event.reply("❌ STICKER OFF")

    # DELAY
    @client.on(events.NewMessage(outgoing=True, pattern=r"\.setstickerdelay (\d+)"))
    async def delay(event):
        sticker_delay[event.sender_id] = int(event.pattern_match.group(1))
        await event.reply("⏱ DELAY SET")

    # SET PACK (reply sticker)
    @client.on(events.NewMessage(outgoing=True, pattern=r"\.setstickerpack"))
    async def pack(event):

        if not event.is_reply:
            return await event.reply("⚠️ Reply to sticker")

        reply = await event.get_reply_message()

        if not reply.sticker:
            return await event.reply("❌ Not a sticker")

        sticker_pack[event.sender_id] = reply.sticker.attributes[1].document_id

        await event.reply("📦 PACK SAVED")

    # AUTO STICKER
    @client.on(events.NewMessage)
    async def auto(event):

        uid = event.sender_id

        if not sticker_on.get(uid, False):
            return

        pack = sticker_pack.get(uid)

        if not pack:
            return

        try:
            await asyncio.sleep(sticker_delay.get(uid, 2))

            stickers = await client(GetStickerSetRequest(
                stickerset=InputStickerSetID(id=pack, access_hash=0)
            ))

            if not stickers.documents:
                return

            st = random.choice(stickers.documents)

            await client.send_file(event.chat_id, st)

        except Exception as e:
            print("ERROR:", e)

    print("🔥 STICKER READY")
