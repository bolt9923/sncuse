from telethon import events
import json
import random
import asyncio
import os

DB_FILE = "reraid_db.json"

# ================= REPLIES ================= #

REPLIES = [
    "🔥 Auto reply active",
    "⚡ SNC USERBOT",
    "👀 Message detected",
    "😎 Reply triggered",
    "🚀 User detected"
]

# ================= DATABASE ================= #

def load_db():

    if not os.path.exists(DB_FILE):

        data = {
            "enabled": True,
            "users": [],
            "count": 1
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
            "count": 1
        }


def save_db():

    with open(DB_FILE, "w") as f:
        json.dump(db, f, indent=4)


db = load_db()

# ================= RANDOM REPLY ================= #

def get_reply():

    return random.choice(REPLIES)

# ================= LOAD FUNCTION ================= #

def load_reraid(client):

    print("✅ ReRaid Plugin Loaded")

    # ================= ADD USER ================= #

    @client.on(events.NewMessage(pattern=r"\.reraid (.+)"))
    async def add_user(event):

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
                f"✅ Added @{user}"
            )

        except Exception as e:

            print("ADD USER ERROR:", e)

    # ================= DELETE USER ================= #

    @client.on(events.NewMessage(pattern=r"\.delreraid (.+)"))
    async def del_user(event):

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

            print("DELETE USER ERROR:", e)

    # ================= LIST USERS ================= #

    @client.on(events.NewMessage(pattern=r"\.rlist$"))
    async def list_users(event):

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

            print("LIST ERROR:", e)

    # ================= COUNT ================= #

    @client.on(events.NewMessage(pattern=r"\.rcount (\d+)"))
    async def set_count(event):

        try:

            count = int(
                event.pattern_match.group(1)
            )

            db["count"] = count

            save_db()

            await event.reply(
                f"✅ Count set to {count}"
            )

        except Exception as e:

            print("COUNT ERROR:", e)

    # ================= ENABLE / DISABLE ================= #

    @client.on(events.NewMessage(pattern=r"\.rraid (on|off)"))
    async def toggle(event):

        try:

            mode = event.pattern_match.group(1)

            if mode == "on":

                db["enabled"] = True

                save_db()

                return await event.reply(
                    "✅ Reply raid enabled"
                )

            db["enabled"] = False

            save_db()

            await event.reply(
                "❌ Reply raid disabled"
            )

        except Exception as e:

            print("TOGGLE ERROR:", e)

    # ================= AUTO REPLY ================= #

    @client.on(events.NewMessage)
    async def auto_reply(event):

        try:

            if not db["enabled"]:
                return

            if not event.is_group:
                return

            if not event.is_reply:
                return

            sender = await event.get_sender()

            if not sender:
                return

            username = ""

            if sender.username:

                username = (
                    sender.username
                    .lower()
                    .strip()
                )

            user_id = str(sender.id)

            targets = [
                str(x).lower().strip()
                for x in db["users"]
            ]

            print("USERNAME:", username)
            print("USER_ID:", user_id)
            print("TARGETS:", targets)

            if (
                username not in targets
                and
                user_id not in targets
            ):
                return

            print("🔥 TARGET DETECTED")

            for _ in range(db["count"]):

                await event.reply(
                    get_reply()
                )

                await asyncio.sleep(0.5)

        except Exception as e:

            print("AUTO REPLY ERROR:", e)
