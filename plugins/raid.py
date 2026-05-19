"""
FULL WORKING RAID PLUGIN
Telethon Userbot Plugin
"""

from telethon import events
import asyncio
import random
import json
import logging
import os

logger = logging.getLogger(__name__)

DB_FILE = "raid_db.json"

# ====================== RAID MESSAGES ======================

RAID_MESSAGES = [
    "spam message 1",
    "spam message 2",
    "spam message 3",
    "spam message 4",
    "spam message 5",
]

# ====================== DATABASE ======================

def load_db():

    default = {
        "users": [],
        "count": 1
    }

    try:

        if not os.path.exists(DB_FILE):
            with open(DB_FILE, "w") as f:
                json.dump(default, f, indent=4)

            return default

        with open(DB_FILE, "r") as f:
            return json.load(f)

    except Exception as e:
        logger.error(f"DB LOAD ERROR: {e}")
        return default


def save_db(data):

    try:

        with open(DB_FILE, "w") as f:
            json.dump(data, f, indent=4)

    except Exception as e:
        logger.error(f"DB SAVE ERROR: {e}")


# ====================== MAIN ======================

def load(client):

    logger.info("RAID PLUGIN LOADED")

    # ====================== .raid ======================

    @client.on(events.NewMessage(
        outgoing=True,
        pattern=r'^\.raid(?:\s|$)'
    ))
    async def raid_cmd(event):

        try:

            db = load_db()

            args = event.raw_text.split()

            if len(args) < 2:
                return await event.edit(
                    "Usage:\n.raid username"
                )

            username = (
                args[1]
                .replace("@", "")
                .lower()
            )

            if username not in db["users"]:

                db["users"].append(username)

                save_db(db)

                await event.edit(
                    f"✅ Started raid on @{username}"
                )

            else:

                await event.edit(
                    f"⚠️ @{username} already added"
                )

            await asyncio.sleep(2)
            await event.delete()

        except Exception as e:
            logger.error(f"RAID CMD ERROR: {e}")

    # ====================== .draid ======================

    @client.on(events.NewMessage(
        outgoing=True,
        pattern=r'^\.draid(?:\s|$)'
    ))
    async def draid_cmd(event):

        try:

            db = load_db()

            args = event.raw_text.split()

            if len(args) < 2:
                return await event.edit(
                    "Usage:\n.draid username"
                )

            username = (
                args[1]
                .replace("@", "")
                .lower()
            )

            if username in db["users"]:

                db["users"].remove(username)

                save_db(db)

                await event.edit(
                    f"✅ Removed @{username}"
                )

            else:

                await event.edit(
                    f"❌ @{username} not found"
                )

            await asyncio.sleep(2)
            await event.delete()

        except Exception as e:
            logger.error(f"DRAID ERROR: {e}")

    # ====================== .count ======================

    @client.on(events.NewMessage(
        outgoing=True,
        pattern=r'^\.count(?:\s|$)'
    ))
    async def count_cmd(event):

        try:

            db = load_db()

            args = event.raw_text.split()

            if len(args) < 2:
                return await event.edit(
                    "Usage:\n.count 5"
                )

            count = int(args[1])

            if count < 1:
                count = 1

            if count > 50:
                count = 50

            db["count"] = count

            save_db(db)

            await event.edit(
                f"✅ Count set to {count}"
            )

            await asyncio.sleep(2)
            await event.delete()

        except:
            await event.edit("Invalid number")

    # ====================== .raidlist ======================

    @client.on(events.NewMessage(
        outgoing=True,
        pattern=r'^\.raidlist$'
    ))
    async def raidlist_cmd(event):

        db = load_db()

        text = "⚔ RAID LIST ⚔\n\n"

        if not db["users"]:
            text += "No users added"

        else:

            for user in db["users"]:
                text += f"• @{user}\n"

        text += f"\nCount: {db['count']}"

        await event.edit(text)

    # ====================== AUTO RAID ======================

    @client.on(events.NewMessage(incoming=True))
    async def auto_raid(event):

        try:

            if not event.is_group:
                return

            sender = await event.get_sender()

            if not sender:
                return

            if sender.bot:
                return

            db = load_db()

            username = (
                sender.username.lower()
                if sender.username
                else ""
            )

            user_id = str(sender.id)

            targets = [
                str(x).lower()
                for x in db["users"]
            ]

            print(f"CHECKING: {username}")

            # MATCH USER
            if (
                username not in targets
                and user_id not in targets
            ):
                return

            print("RAID TRIGGERED")

            # SEND REPLIES
            for i in range(db["count"]):

                try:

                    text = random.choice(
                        RAID_MESSAGES
                    )

                    await asyncio.sleep(
                        random.randint(1, 2)
                    )

                    # IMPORTANT FIX
                    await client.send_message(
                        entity=event.chat_id,
                        message=text,
                        reply_to=event.id
                    )

                    print(
                        f"SENT {i+1}/{db['count']}"
                    )

                except Exception as e:
                    logger.error(
                        f"SEND ERROR: {e}"
                    )
                    break

        except Exception as e:
            logger.error(
                f"AUTO RAID ERROR: {e}"
            )


# ====================== ALIASES ======================

init = load
