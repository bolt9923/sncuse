import asyncio
import random
import re
from telethon import events
from telethon.tl.functions.messages import GetStickerSetRequest
from telethon.tl.types import InputStickerSetShortName

# ================= STATES =================
sticker_on = {}
sticker_delay = {}
sticker_pack = {}

# ================= EXTRACT PACK NAME =================
def extract_pack_name(text):
    """
    Extract pack name from Telegram link or direct input
    """
    if "t.me/addstickers/" in text:
        return text.split("t.me/addstickers/")[1].strip("/")
    return text.strip()

# ================= LOAD =================
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
        await event.reply(f"⏱ DELAY SET: {sticker_delay[event.sender_id]}s")

    # ================= SET PACK (LINK OR NAME) =================
    @client.on(events.NewMessage(outgoing=True, pattern=r"\.setstickerpack (.+)"))
    async def set_pack(event):

        raw_input = event.pattern_match.group(1)

        pack_name = extract_pack_name(raw_input)

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

    # ================= AUTO STICKER =================
    @client.on(events.NewMessage)
    async def auto_sticker(event):

        uid = event.sender_id

        # ignore commands
        if event.raw_text and event.raw_text.startswith("."):
            return

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

    print("🔥 STICKER SYSTEM READY (LINK SUPPORT ENABLED)")
