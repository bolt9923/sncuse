import os

from telethon import events
from telethon.tl.functions.photos import DeletePhotosRequest
from telethon.tl.functions.account import UpdateProfileRequest
from telethon.tl.functions.photos import UploadProfilePhotoRequest

OWNER = os.environ.get("OWNER", "SNC USER")
BIO = os.environ.get("BIO", "SNC USERBOT")

# backup
original_data = {}

def load_clone(client):

    # =========================
    # CLONE
    # =========================
    @client.on(events.NewMessage(pattern=r"\.clone ?(.*)"))
    async def clone(event):

        try:

            user = None

            # reply clone
            if event.is_reply:
                reply = await event.get_reply_message()
                user = await reply.get_sender()

            # username clone
            else:

                text = event.pattern_match.group(1)

                if not text:
                    return await event.reply(
                        "❌ Reply or give username"
                    )

                user = await client.get_entity(text)

            # save original profile
            me = await client.get_me()

            if "first_name" not in original_data:

                original_data["first_name"] = me.first_name
                original_data["last_name"] = me.last_name
                original_data["bio"] = ""

            # get target full info
            full = await client.get_entity(user.id)

            # download photo
            path = await client.download_profile_photo(
                user.id,
                file="clone.jpg"
            )

            # upload photo
            file = await client.upload_file(path)

            await client(
                UploadProfilePhotoRequest(file)
            )

            # update profile
            await client(
                UpdateProfileRequest(
                    first_name=full.first_name or "",
                    last_name=full.last_name or "",
                    about="Cloned By SNC USERBOT"
                )
            )

            await event.reply(
                f"✅ Cloned {full.first_name}"
            )

        except Exception as e:

            await event.reply(f"❌ Error:\n{e}")

    # =========================
    # REVERT
    # =========================
    @client.on(events.NewMessage(pattern=r"\.revert"))
    async def revert(event):

        try:

            photos = []

            async for photo in client.iter_profile_photos("me"):
                photos.append(photo)

            if photos:
                await client(
                    DeletePhotosRequest(
                        id=[photos[0]]
                    )
                )

            await client(
                UpdateProfileRequest(
                    first_name=OWNER,
                    about=BIO
                )
            )

            await event.reply("✅ Profile Reverted")

        except Exception as e:

            await event.reply(f"❌ Error:\n{e}")
