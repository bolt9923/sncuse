import asyncio
import random
from telethon import events
from telethon.tl.functions.messages import GetStickerSetRequest
from telethon.tl.types import InputStickerSetShortName

sticker_on = {}
sticker_delay = {}
sticker_pack = {}

def load_stickers(client):

    print("🟢 STICKER SYSTEM LOADED")

    # ================= ON =================
    @client.on(events.NewMessage(outgoing=True, pattern=r"\.sticker on"))
    async def on(event):
        sticker_on[event.sender_id] = True
        await event.reply("✅ STICKER ON")

    # ================= OFF =================
    @client.on(events.NewMessage(outgoing=True, pattern=r"\.sticker off"))
    async def off(event):
        sticker_on[event.sender_id] = False
        await event.reply("❌ STICKER OFF")

    # ================= DELAY =================
    @client.on(events.NewMessage(outgoing=True, pattern=r"\.setstickerdelay (\d+)"))
    async def delay(event):
        sticker_delay[event.sender_id] = int(event.pattern_match.group(1))
        await event.reply("⏱ DELAY SET")

    # ================= SET PACK (NO REPLY NEEDED) =================
    @client.on(events.NewMessage(outgoing=True, pattern=r"\.setstickerpack (\S+)"))
    async def set_pack(event):

        pack_name = event.pattern_match.group(1)

        sticker_pack[event.sender_id] = pack_name

        await event.reply(f"📦 PACK SAVED:\n{pack_name}")

    # ================= AUTO STICKER =================
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

            result = await client(GetStickerSetRequest(
                stickerset=InputStickerSetShortName(pack)
            ))

            if not result.documents:
                return

            sticker = random.choice(result.documents)

            await client.send_file(event.chat_id, sticker)

        except Exception as e:
            print("STICKER ERROR:", e)

    print("🔥 STICKER READY")
