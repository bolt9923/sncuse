from telethon import events
from telethon.tl.types import User
import asyncio
import json
import os

# ================= IMPORT YOUR CLIENT ================= #

from SNC import bot

# ================= CONFIG ================= #

OWNER_ID = 123456789
DB_FILE = "reraid_db.json"

# ================= DATABASE ================= #

def load_reraid():

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


def save_reraid():
    with open(DB_FILE, "w") as f:
        json.dump(db, f, indent=4)


db = load_reraid()

# ================= ADD USER ================= #

@bot.on(events.NewMessage(pattern=r"^\.reraid(?: |$)(.*)"))
async def add_reraid(event):

    if event.sender_id != OWNER_ID:
        return

    user = event.pattern_match.group(1).strip()

    if not user:
        return await event.reply(
            "Usage:\n.reraid username"
        )

    user = user.replace("@", "").lower()

    if user in db["users"]:
        return await event.reply("User already added.")

    db["users"].append(user)

    save_reraid()

    await event.reply(f"Added @{user} to reply raid list.")

# ================= REMOVE USER ================= #

@bot.on(events.NewMessage(pattern=r"^\.delreraid(?: |$)(.*)"))
async def del_reraid(event):

    if event.sender_id != OWNER_ID:
        return

    user = event.pattern_match.group(1).strip()

    if not user:
        return await event.reply(
            "Usage:\n.delreraid username"
        )

    user = user.replace("@", "").lower()

    if user not in db["users"]:
        return await event.reply("User not found.")

    db["users"].remove(user)

    save_reraid()

    await event.reply(f"Removed @{user}")

# ================= LIST USERS ================= #

@bot.on(events.NewMessage(pattern=r"^\.rlist$"))
async def list_reraid(event):

    if event.sender_id != OWNER_ID:
        return

    if not db["users"]:
        return await event.reply("No users added.")

    text = "**Reply Raid Users:**\n\n"

    for user in db["users"]:
        text += f"• @{user}\n"

    await event.reply(text)

# ================= SET COUNT ================= #

@bot.on(events.NewMessage(pattern=r"^\.rcount (\\d+)$"))
async def set_rcount(event):

    if event.sender_id != OWNER_ID:
        return

    count = int(event.pattern_match.group(1))

    if count > 50:
        return await event.reply("Maximum limit is 50.")

    db["count"] = count

    save_reraid()

    await event.reply(f"Reply count set to {count}")

# ================= SET REPLY ================= #

@bot.on(events.NewMessage(pattern=r"^\.rreply(?: |$)(.*)"))
async def set_rreply(event):

    if event.sender_id != OWNER_ID:
        return

    text = event.pattern_match.group(1).strip()

    if not text:
        return await event.reply(
            "Usage:\n.rreply message"
        )

    db["reply"] = text

    save_reraid()

    await event.reply(f"Reply message updated:\n{text}")

# ================= ENABLE / DISABLE ================= #

@bot.on(events.NewMessage(pattern=r"^\.rraid (on|off)$"))
async def toggle_rraid(event):

    if event.sender_id != OWNER_ID:
        return

    mode = event.pattern_match.group(1)

    if mode == "on":
        db["enabled"] = True
        save_reraid()

        return await event.reply("Reply raid enabled.")

    db["enabled"] = False

    save_reraid()

    await event.reply("Reply raid disabled.")

# ================= AUTO REPLY RAID ================= #

@bot.on(events.NewMessage(incoming=True))
async def auto_reply_raid(event):

    try:

        if not db["enabled"]:
            return

        if not event.is_group:
            return

        if not event.is_reply:
            return

        if event.sender_id == OWNER_ID:
            return

        sender = await event.get_sender()

        if not sender:
            return

        if not isinstance(sender, User):
            return

        username = (sender.username or "").lower().strip()

        user_id = str(sender.id)

        targets = [str(x).lower().strip() for x in db["users"]]

        if username not in targets and user_id not in targets:
            return

        for _ in range(db["count"]):

            await event.reply(db["reply"])

            await asyncio.sleep(0.4)

    except Exception as e:
        print(f"Reply Raid Error: {e}")
