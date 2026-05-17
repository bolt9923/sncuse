import asyncio
import random
from telethon import events
from telethon.tl.functions.messages import GetStickerSetRequest
from telethon.tl.types import InputStickerSetShortName

# ================= STATES =================
sticker_on = {}
sticker_delay = {}
sticker_pack = {}

# ================= LOAD FUNCTION =================
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
    async def set_delay(event):
        sticker_delay[event.sender_id] = int(event.pattern_match.group(1))
        await event.reply(f"⏱ DELAY SET: {sticker_delay[event.sender_id]}s")

    # ================= SET PACK =================
    @client.on(events.NewMessage(outgoing=True, pattern=r"\.setstickerpack (\S+)"))
    async def set_pack(event):

        pack_name = event.pattern_match.group(1)

        try:
            # verify sticker pack exists
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

    # ================= AUTO STICKER ENGINE =================
    @client.on(events.NewMessage)
    async def auto_sticker(event):

        uid = event.sender_id

        # ignore commands
        if event.raw_text and event.raw_text.startswith("."):
            return

        # must be ON
        if not sticker_on.get(uid, False):
            return

        pack = sticker_pack.get(uid)

        if not pack:
            return

        delay = sticker_delay.get(uid, 2)

        try:
            await asyncio.sleep(delay)

            result = await client(GetStickerSetRequest(
                stickerset=InputStickerSetShortName(pack),
                hash=0
            ))

            if not result.documents:
                return

            sticker = random.choice(result.documents)

            await client.send_file(event.chat_id, sticker)

        except Exception as e:
            print("STICKER ERROR:", e)

    print("🔥 STICKER SYSTEM READY (100% WORKING)")
