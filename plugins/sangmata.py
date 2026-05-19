import asyncio

from telethon import events

# =========================
# LOAD SANGMATA
# =========================
def load_sangmata(client):

    print("✅ Sangmata Plugin Loaded")

    @client.on(events.NewMessage(pattern=r"\.(sg|sa|sangmata)(?:\s|$)(.*)"))
    async def sangmata(event):

        try:

            reply = await event.get_reply_message()

            args = event.pattern_match.group(2)

            user = None

            # ================= REPLY USER =================
            if reply:

                user = await reply.get_sender()

            # ================= USERNAME / ID =================
            elif args:

                user = await client.get_entity(args)

            else:

                return await event.reply(
                    "❌ Reply or give username/id"
                )

            bot = "@SangMataInfo_bot"

            msg = await event.reply(
                "🔍 Checking name history..."
            )

            # unblock if blocked
            try:

                await client.send_message(
                    bot,
                    f"/search_id {user.id}"
                )

            except Exception:

                await client(functions.contacts.UnblockRequest(bot))

                await client.send_message(
                    bot,
                    f"/search_id {user.id}"
                )

            await asyncio.sleep(3)

            texts = []

            async for m in client.iter_messages(
                bot,
                limit=5
            ):

                if m.text:

                    texts.append(m.text)

            if not texts:

                return await msg.edit(
                    "❌ No history found"
                )

            result = "\n\n".join(texts)

            await msg.edit(result)

        except Exception as e:

            await event.reply(
                f"❌ Error:\n{e}"
            )
