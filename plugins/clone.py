import os

from telethon import events
from telethon.tl.functions.account import UpdateProfileRequest
from telethon.tl.functions.photos import UploadProfilePhotoRequest

OWNER = os.environ.get("OWNER", "SNC USER")
BIO = os.environ.get("BIO", "SNC USERBOT")

def load_clone(client):

    print("✅ CLONE PLUGIN LOADED")

    # =========================
    # CLONE
    # =========================
    @client.on(events.NewMessage(pattern=r"\.clone(?: |$)(.*)"))
    async def clone(event):

        print("CLONE COMMAND DETECTED")

        try:

            user = None

            # reply clone
            if event.is_reply:

                reply = await event.get_reply_message()

                user = await reply.get_sender()

            else:

                text = event.pattern_match.group(1)

                if not text:

                    return await event.reply(
                        "❌ Reply or give username"
                    )

                user = await client.get_entity(text)

            print("TARGET:", user.id)

            # download profile photo
            path = await client.download_profile_photo(
                user.id,
                file="clone.jpg"
            )

            print("PHOTO DOWNLOADED")

            # upload photo
            if path:

                file = await client.upload_file(path)

                await client(
                    UploadProfilePhotoRequest(file)
                )

                print("PHOTO UPLOADED")

            # update profile
            await client(
                UpdateProfileRequest(
                    first_name=user.first_name or "",
                    last_name=user.last_name or "",
                    about="SNC USERBOT"
                )
            )

            print("PROFILE UPDATED")

            await event.reply(
                f"✅ Cloned {user.first_name}"
            )

        except Exception as e:

            print("CLONE ERROR:", e)

            await event.reply(
                f"❌ Error:\n{e}"
            )

    # =========================
    # REVERT
    # =========================
    @client.on(events.NewMessage(pattern=r"\.revert"))
    async def revert(event):

        try:

            await client(
                UpdateProfileRequest(
                    first_name=OWNER,
                    about=BIO
                )
            )

            await event.reply(
                "✅ Reverted"
            )

        except Exception as e:

            print("REVERT ERROR:", e)
