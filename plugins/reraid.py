from telethon import events
from telethon.tl.types import User
import asyncio
import json
import os

# ================= CONFIG ================= #

DB_FILE = "reraid_db.json"

# Your owner ID
OWNER_ID = 123456789

# ================= DATABASE ================= #

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

# ================= ADD USER ================= #

@client.on(events.NewMessage(pattern=r"^\.reraid(?: |$)(.*)"))
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
    save_db()

    await event.reply(f"Added @{user} to reply raid list.")

# ================= REMOVE USER ================= #

@client.on(events.NewMessage(pattern=r"^\.delreraid(?: |$)(.*)"))
async def remove_reraid(event):

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
    save_db()

    await event.reply(f"Removed @{user}")

# ================= LIST USERS ================= #

@client.on(events.NewMessage(pattern=r"^\.rlist$"))
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

@client.on(events.NewMessage(pattern=r"^\.rcount(?: |$)(\\d+)"))
async def set_count(event):

    if event.sender_id != OWNER_ID:
        return

    count = int(event.pattern_match.group(1))

    if count > 50:
        return await event.reply("Max limit is 50.")

    db["count"] = count
    save_db()

    await event.reply(f"Reply count set to {count}")

# ================= SET REPLY ================= #

@client.on(events.NewMessage(pattern=r"^\.rreply(?: |$)(.*)"))
async def set_reply(event):

    if event.sender_id != OWNER_ID:
        return

    text = event.pattern_match.group(1)

    if not text:
        return await event.reply(
            "Usage:\n.rreply text"
        )

    db["reply"] = text
    save_db()

    await event.reply(f"Reply message updated:\n{text}")

# ================= ENABLE / DISABLE ================= #

@client.on(events.NewMessage(pattern=r"^\.rraid(?: |$)(on|off)$"))
async def toggle_reraid(event):

    if event.sender_id != OWNER_ID:
        return

    mode = event.pattern_match.group(1)

    if mode == "on":
        db["enabled"] = True
        save_db()
        return await event.reply("Reply raid enabled.")

    db["enabled"] = False
    save_db()

    await event.reply("Reply raid disabled.")

# ================= AUTO REPLY RAID ================= #

@client.on(events.NewMessage(incoming=True))
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
        print("Reply Raid Error:", e)

# ================= END ================= #
