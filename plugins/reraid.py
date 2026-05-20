import json
import random
import asyncio
import os

from pyrogram import filters
from pyrogram.enums import ChatAction

from SNC import app

# ================= DATABASE ================= #

DB_FILE = "reraid_db.json"

# ================= REPLIES ================= #

REPLIES = [
    "Hello 👋",
    "Reply detected 🔥",
    "Auto reply working ⚡",
    "Testing successful ✅",
    "Bot online 🚀",
    "Nice message 😄",
    "Reply sent 🤖"
]

# ================= LOAD DB ================= #

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

# ================= ADD USER ================= #

@app.on_message(filters.me & filters.command("reraid", prefixes="."))
async def add_user(_, msg):

    try:

        if len(msg.command) < 2:

            return await msg.reply(
                "Usage:\n.reraid username"
            )

        user = msg.command[1]

        user = user.replace("@", "").lower()

        if user in db["users"]:

            return await msg.reply(
                "User already added"
            )

        db["users"].append(user)

        save_db()

        await msg.reply(
            f"✅ Added @{user}"
        )

    except Exception as e:

        print("ADD USER ERROR:", e)

# ================= REMOVE USER ================= #

@app.on_message(filters.me & filters.command("delreraid", prefixes="."))
async def del_user(_, msg):

    try:

        if len(msg.command) < 2:

            return await msg.reply(
                "Usage:\n.delreraid username"
            )

        user = msg.command[1]

        user = user.replace("@", "").lower()

        if user not in db["users"]:

            return await msg.reply(
                "User not found"
            )

        db["users"].remove(user)

        save_db()

        await msg.reply(
            f"✅ Removed @{user}"
        )

    except Exception as e:

        print("DEL USER ERROR:", e)

# ================= USER LIST ================= #

@app.on_message(filters.me & filters.command("rlist", prefixes="."))
async def rlist(_, msg):

    try:

        if not db["users"]:

            return await msg.reply(
                "No users added"
            )

        text = "🔥 Reply Raid Users\n\n"

        for user in db["users"]:

            text += f"• @{user}\n"

        await msg.reply(text)

    except Exception as e:

        print("RLIST ERROR:", e)

# ================= SET COUNT ================= #

@app.on_message(filters.me & filters.command("rcount", prefixes="."))
async def set_count(_, msg):

    try:

        if len(msg.command) < 2:

            return await msg.reply(
                "Usage:\n.rcount number"
            )

        count = int(msg.command[1])

        if count > 20:

            return await msg.reply(
                "Max limit is 20"
            )

        db["count"] = count

        save_db()

        await msg.reply(
            f"✅ Count set to {count}"
        )

    except Exception as e:

        print("COUNT ERROR:", e)

# ================= ENABLE / DISABLE ================= #

@app.on_message(filters.me & filters.command("rraid", prefixes="."))
async def toggle_reply(_, msg):

    try:

        if len(msg.command) < 2:

            return await msg.reply(
                "Usage:\n.rraid on/off"
            )

        mode = msg.command[1].lower()

        if mode == "on":

            db["enabled"] = True

            save_db()

            return await msg.reply(
                "✅ Reply raid enabled"
            )

        elif mode == "off":

            db["enabled"] = False

            save_db()

            return await msg.reply(
                "❌ Reply raid disabled"
            )

    except Exception as e:

        print("TOGGLE ERROR:", e)

# ================= AUTO REPLY ================= #

@app.on_message(
    filters.group &
    ~filters.me &
    filters.reply
)
async def auto_reply(client, msg):

    try:

        if not db["enabled"]:
            return

        if not msg.from_user:
            return

        username = ""

        if msg.from_user.username:

            username = (
                msg.from_user.username
                .lower()
                .strip()
            )

        user_id = str(msg.from_user.id)

        targets = [
            str(x).lower().strip()
            for x in db["users"]
        ]

        print("USERNAME:", username)
        print("USER ID:", user_id)
        print("TARGETS:", targets)

        if (
            username not in targets
            and
            user_id not in targets
        ):
            return

        print("🔥 TARGET DETECTED")

        for _ in range(db["count"]):

            text = get_reply()

            await client.send_chat_action(
                msg.chat.id,
                ChatAction.TYPING
            )

            await asyncio.sleep(
                random.randint(1, 3)
            )

            await msg.reply(text)

    except Exception as e:

        print("AUTO REPLY ERROR:", e)

# ================= LOADED ================= #

print("✅ reraid plugin loaded")
