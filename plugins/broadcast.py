import asyncio

from telethon import events

# =========================
# LOAD BROADCAST
# =========================
def load_broadcast(client):

    print("✅ Broadcast Plugin Loaded")

    # =========================
    # GROUP GCAST
    # =========================
    @client.on(events.NewMessage(pattern=r"\.gcast(?:\s|$)(.*)"))
    async def gcast(event):

        text = event.pattern_match.group(1)

        reply = await event.get_reply_message()

        if not text and not reply:

            return await event.reply(
                "❌ Give message or reply"
            )

        msg = await event.reply(
            "📢 Starting Group Broadcast..."
        )

        done = 0
        failed = 0

        async for dialog in client.iter_dialogs():

            try:

                if not dialog.is_group:
                    continue

                chat_id = dialog.id

                if reply:

                    await reply.forward_to(chat_id)

                else:

                    await client.send_message(
                        chat_id,
                        text
                    )

                done += 1

                await asyncio.sleep(1)

            except Exception:

                failed += 1

        await msg.edit(
            f"✅ GCAST DONE\n\n"
            f"✔️ Success: {done}\n"
            f"❌ Failed: {failed}"
        )

    # =========================
    # PRIVATE GUCAST
    # =========================
    @client.on(events.NewMessage(pattern=r"\.gucast(?:\s|$)(.*)"))
    async def gucast(event):

        text = event.pattern_match.group(1)

        reply = await event.get_reply_message()

        if not text and not reply:

            return await event.reply(
                "❌ Give message or reply"
            )

        msg = await event.reply(
            "📨 Starting User Broadcast..."
        )

        done = 0
        failed = 0

        async for dialog in client.iter_dialogs():

            try:

                if not dialog.is_user:
                    continue

                chat_id = dialog.id

                if reply:

                    await reply.forward_to(chat_id)

                else:

                    await client.send_message(
                        chat_id,
                        text
                    )

                done += 1

                await asyncio.sleep(1)

            except Exception:

                failed += 1

        await msg.edit(
            f"✅ GUCAST DONE\n\n"
            f"✔️ Success: {done}\n"
            f"❌ Failed: {failed}"
        )
