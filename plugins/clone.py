import os

from telethon import events
from telethon.tl.functions.account import UpdateProfileRequest
from telethon.tl.functions.photos import UploadProfilePhotoRequest
from telethon.tl.functions.photos import DeletePhotosRequest

# =========================
# DEFAULT PROFILE
# =========================
OWNER = os.environ.get("OWNER", "SNC USER")
BIO = os.environ.get("BIO", "SNC USERBOT")

# =========================
# STORAGE
# =========================
original_profile = {}

# =========================
# LOAD PLUGIN
# =========================
def load_clone(client):

    print("✅ clone plugin loaded")

    # =========================
    # CLONE COMMAND
    # =========================
    @client.on(events.NewMessage(pattern=r"\.clone(?: |$)(.*)"))
    async def clone(event):

        try:

            target = None

            # ---------------- REPLY MODE ----------------
            if event.is_reply:

                reply = await event.get_reply_message()

                target = await reply.get_sender()

            # ---------------- USERNAME MODE ----------------
            else:

                text = event.pattern_match.group(1)

                if not text:

                    return await event.reply(
                        "❌ Reply to user or give username\n\nExample:\n.clone @username"
                    )

                target = await client.get_entity(text)

            # ---------------- SAVE ORIGINAL PROFILE ----------------
            me = await client.get_me()

            if not original_profile:

                original_profile["first_name"] = me.first_name or OWNER
                original_profile["last_name"] = me.last_name or ""
                original_profile["bio"] = BIO

            # ---------------- UPDATE NAME/BIO ----------------
            await client(
                UpdateProfileRequest(
                    first_name=target.first_name or "",
                    last_name=target.last_name or "",
                    about="SNC USERBOT CLONE"
                )
            )

            # ---------------- DELETE OLD PROFILE PHOTO ----------------
            photos = []

            async for photo in client.iter_profile_photos("me"):
                photos.append(photo)

            if photos:

                try:
                    await client(
                        DeletePhotosRequest(
                            id=[photos[0]]
                        )
                    )
                except:
                    pass

            # ---------------- DOWNLOAD TARGET PHOTO ----------------
            path = await client.download_profile_photo(target.id)

            # ---------------- UPLOAD TARGET PHOTO ----------------
            if path and os.path.exists(path):

                file = await client.upload_file(path)

                await client(
                    UploadProfilePhotoRequest(
                        file=file
                    )
                )

            # ---------------- SUCCESS ----------------
            await event.reply(
                f"✅ Successfully cloned:\n{target.first_name}"
            )

        except Exception as e:

            print("CLONE ERROR:", e)

            await event.reply(
                f"❌ Clone Failed:\n{e}"
            )

    # =========================
    # REVERT COMMAND
    # =========================
    @client.on(events.NewMessage(pattern=r"\.revert"))
    async def revert(event):

        try:

            # ---------------- RESTORE PROFILE ----------------
            await client(
                UpdateProfileRequest(
                    first_name=original_profile.get(
                        "first_name",
                        OWNER
                    ),
                    last_name=original_profile.get(
                        "last_name",
                        ""
                    ),
                    about=original_profile.get(
                        "bio",
                        BIO
                    )
                )
            )

            # ---------------- DELETE CLONED PHOTO ----------------
            photos = []

            async for photo in client.iter_profile_photos("me"):
                photos.append(photo)

            if photos:

                try:
                    await client(
                        DeletePhotosRequest(
                            id=[photos[0]]
                        )
                    )
                except:
                    pass

            await event.reply(
                "✅ Profile reverted successfully"
            )

        except Exception as e:

            print("REVERT ERROR:", e)

            await event.reply(
                f"❌ Revert Failed:\n{e}"
            )

    # =========================
    # TEST COMMAND
    # =========================
    @client.on(events.NewMessage(pattern=r"\.testclone"))
    async def testclone(event):

        await event.reply(
            "✅ Clone Plugin Working"
        )
