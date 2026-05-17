import asyncio
import random
from telethon import events

sticker_on = {}
sticker_delay = {}
sticker_pack = {}

# ================= LOAD STICKER SYSTEM =================
def load_stickers(client):

    print("🟢 STICKER SYSTEM LOADED")

    # ================= ON =================
    @client.on(events.NewMessage(outgoing=True, pattern=r"\.sticker on"))
    async def sticker_on_cmd(event):
        sticker_on[event.sender_id] = True
        await event.reply("✅ STICKER ON")

    # ================= OFF =================
    @client.on(events.NewMessage(outgoing=True, pattern=r"\.sticker off"))
    async def sticker_off_cmd(event):
        sticker_on[event.sender_id] = False
        await event.reply("❌ STICKER OFF")

    # ================= SET DELAY =================
    @client.on(events.NewMessage(outgoing=True, pattern=r"\.setstickerdelay (\d+)"))
    async def set_delay(event):

        sticker_delay[event.sender_id] = int(event.pattern_match.group(1))
        await event.reply("⏱ STICKER DELAY SET")

    # ================= SET PACK =================
    @client.on(events.NewMessage(outgoing=True, pattern=r"\.setstickerpack"))
    async def set_pack(event):

        if not event.is_reply:
            return await event.reply("⚠️ Reply to sticker")

        reply = await event.get_reply_message()

        if not reply.sticker:
            return await event.reply("❌ Not a sticker")

        sticker_pack[event.sender_id] = reply.sticker.set_id

        await event.reply("📦 STICKER PACK SAVED")

    # ================= AUTO STICKER HANDLER =================
    @client.on(events.NewMessage)
    async def auto_sticker(event):

        uid = event.sender_id

        if not sticker_on.get(uid, False):
            return

        if not event.text:
            return

        try:
            delay = sticker_delay.get(uid, 2)
            pack = sticker_pack.get(uid)

            if not pack:
                return

            await asyncio.sleep(delay)

            stickers = await client.get_messages(event.chat_id, limit=50)

            sticker_list = [s for s in stickers if s.sticker]

            if not sticker_list:
                return

            random_sticker = random.choice(sticker_list)

            await client.send_file(event.chat_id, random_sticker.media)

        except:
            pass

    print("🔥 STICKER SYSTEM READY")
