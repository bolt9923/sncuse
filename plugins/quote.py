import asyncio

from telethon import events

def load_quotly(client):

    print("✅ quotly plugin loaded")

    @client.on(events.NewMessage(pattern=r"\.(q|quotly)(?: |$)(.*)"))
    async def quotly(event):

        try:

            if not event.is_reply:

                return await event.reply(
                    "❌ Reply to a message"
                )

            color = event.pattern_match.group(2)

            bot = "@QuotLyBot"

            await event.reply("⚡ Creating Quote...")

            # unblock bot
            try:
                await client(functions.contacts.UnblockRequest(bot))
            except:
                pass

            # send color
            if color:

                await client.send_message(
                    bot,
                    f"/qcolor {color}"
                )

                await asyncio.sleep(1)

            # forward replied message
            reply = await event.get_reply_message()

            await reply.forward_to(bot)

            await asyncio.sleep(6)

            # get sticker
            async for msg in client.iter_messages(
                bot,
                limit=5
            ):

                if msg.sticker:

                    await event.reply(
                        file=msg.media,
                        reply_to=reply.id
                    )

                    break

        except Exception as e:

            print("QUOTLY ERROR:", e)

            await event.reply(
                f"❌ Error:\n{e}"
            )
