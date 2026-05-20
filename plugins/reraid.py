import asyncio
import json
import os

from telethon import events
from telethon.tl.types import User

# ================= DATABASE ================= #

DB_FILE = "reraid_db.json"


def load_db():

    if not os.path.exists(DB_FILE):

        data = {
            "enabled": True,
            "users": [],
            "count": 5,
            "reply": "RAID"
        }

        with open(DB_FILE, "w") as f:
            json.dump(data, f, indent=4)

        return data

    try:

        with open(DB_FILE, "r") as f:
            return json.load(f)

    except:

        return {
            "enabled": True,
            "users": [],
            "count": 5,
            "reply": "RAID"
        }


def save_db():

    with open(DB_FILE, "w") as f:
        json.dump(db, f, indent=4)


db = load_db()

# ================= LOAD FUNCTION ================= #

def load_reraid(client):

    print("✅ Reply Raid Plugin Loaded")

    # ================= ADD USER ================= #

    @client.on(events.NewMessage(pattern=r"^\.reraid (.+)"))
    async def add_reraid(event):

        try:

            user = event.pattern_match.group(1)

            user = user.replace("@", "").lower().strip()

            if user in db["users"]:

                return await event.reply(
                    "⚠ User already added"
                )

            db["users"].append(user)

            save_db()

            await event.reply(
                f"✅ Added @{user} to reply raid list"
            )

        except Exception as e:

            print("ADD RERAID ERROR:", e)

    # ================= REMOVE USER ================= #

    @client.on(events.NewMessage(pattern=r"^\.delreraid (.+)"))
    async def del_reraid(event):

        try:

            user = event.pattern_match.group(1)

            user = user.replace("@", "").lower().strip()

            if user not in db["users"]:

                return await event.reply(
                    "❌ User not found"
                )

            db["users"].remove(user)

            save_db()

            await event.reply(
                f"✅ Removed @{user}"
            )

        except Exception as e:

            print("DEL RERAID ERROR:", e)

    # ================= USER LIST ================= #

    @client.on(events.NewMessage(pattern=r"^\.rlist$"))
    async def rlist(event):

        try:

            if not db["users"]:

                return await event.reply(
                    "❌ No users added"
                )

            text = "🔥 Reply Raid Users\n\n"

            for user in db["users"]:

                text += f"• @{user}\n"

            await event.reply(text)

        except Exception as e:

            print("RLIST ERROR:", e)

    # ================= SET COUNT ================= #

    @client.on(events.NewMessage(pattern=r"^\.rcount (\\d+)$"))
    async def set_count(event):

        try:

            count = int(
                event.pattern_match.group(1)
            )

            if count > 50:

                return await event.reply(
                    "❌ Max limit is 50"
                )

            db["count"] = count

            save_db()

            await event.reply(
                f"✅ Reply count set to {count}"
            )

        except Exception as e:

            print("RCOUNT ERROR:", e)

    # ================= SET REPLY ================= #

    @client.on(events.NewMessage(pattern=r"^\.rreply (.+)"))
    async def set_reply(event):

        try:

            msg = event.pattern_match.group(1)

            db["reply"] = msg

            save_db()

            await event.reply(
                f"✅ Reply message updated:\n{msg}"
            )

        except Exception as e:

            print("RREPLY ERROR:", e)

    # ================= ENABLE / DISABLE ================= #

    @client.on(events.NewMessage(pattern=r"^\.rraid (on|off)$"))
    async def toggle_rraid(event):

        try:

            mode = event.pattern_match.group(1)

            if mode == "on":

                db["enabled"] = True

                save_db()

                return await event.reply(
                    "✅ Reply Raid Enabled"
                )

            db["enabled"] = False

            save_db()

            await event.reply(
                "❌ Reply Raid Disabled"
            )

        except Exception as e:

            print("TOGGLE ERROR:", e)

    # ================= AUTO REPLY RAID ================= #

    @client.on(events.NewMessage(incoming=True))
    async def auto_reply_raid(event):

        try:

            # ENABLE CHECK
            if not db["enabled"]:
                return

            # GROUP ONLY
            if not event.is_group:
                return

            # MUST BE REPLY
            if not event.is_reply:
                return

            # GET SENDER
            sender = await event.get_sender()

            if not sender:
                return

            # ONLY USERS
            if not isinstance(sender, User):
                return

            # USERNAME
            username = ""

            if sender.username:
                username = sender.username.lower().strip()

            # USER ID
            user_id = str(sender.id)

            # TARGETS
            targets = [
                str(x).lower().strip()
                for x in db["users"]
            ]

            print("USERNAME:", username)
            print("USER ID:", user_id)
            print("TARGETS:", targets)

            # MATCH CHECK
            matched = False

            if username in targets:
                matched = True

            if user_id in targets:
                matched = True

            if not matched:
                return

            print("🔥 TARGET DETECTED")

            # REPLY RAID
            for _ in range(
                int(db["count"])
            ):

                await event.reply(
                    db["reply"]
                )

                await asyncio.sleep(0.5)

        except Exception as e:

            print("AUTO REPLY ERROR:", e)
