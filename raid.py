from core import app
from pyrogram import filters
import json
import asyncio
import random

DB_FILE = "db.json"

# ================= DB =================
def load_db():
    try:
        with open(DB_FILE, "r") as f:
            return json.load(f)
    except:
        return {
            "users": [],
            "count": 3
        }

def save_db(data):
    with open(DB_FILE, "w") as f:
        json.dump(data, f, indent=4)

db = load_db()

# ================= DEBUG =================
print("🔥 RAID MODULE LOADED")

# ================= ADD USER =================
@app.on_message(filters.me & filters.command("rraid", prefixes="!"))
async def rraid(client, msg):

    if len(msg.command) < 2:
        return await msg.reply("Usage: !rraid @username")

    user = msg.command[1].replace("@", "")

    if user not in db["users"]:
        db["users"].append(user)
        save_db(db)
        await msg.reply(f"✅ Added {user}")
    else:
        await msg.reply("⚠️ Already exists")

# ================= REMOVE USER =================
@app.on_message(filters.me & filters.command("draid", prefixes="!"))
async def draid(client, msg):

    if len(msg.command) < 2:
        return await msg.reply("Usage: !draid @username")

    user = msg.command[1].replace("@", "")

    if user in db["users"]:
        db["users"].remove(user)
        save_db(db)
        await msg.reply(f"❌ Removed {user}")
    else:
        await msg.reply("Not found")

# ================= SET COUNT =================
@app.on_message(filters.me & filters.command("count", prefixes="!"))
async def set_count(client, msg):

    if len(msg.command) < 2:
        return await msg.reply("Usage: !count 5")

    try:
        db["count"] = int(msg.command[1])
        save_db(db)
        await msg.reply(f"✅ Count set to {db['count']}")
    except:
        await msg.reply("❌ Invalid number")

# ================= REPLY RAID =================
@app.on_message(filters.me & filters.command("replyraid", prefixes="!"))
async def replyraid(client, msg):

    print("🔥 replyraid triggered")

    if not msg.reply_to_message:
        return await msg.reply("⚠️ Reply to a message first")

    if len(msg.command) < 2:
        return await msg.reply("Usage: !replyraid text")

    text = msg.text.split(" ", 1)

    if len(text) < 2:
        return await msg.reply("⚠️ No text provided")

    text = text[1]

    count = db.get("count", 3)

    for i in range(count):
        try:
            await msg.reply_to_message.reply(text)
            await asyncio.sleep(random.uniform(0.5, 1.5))
        except:
            pass

    await msg.reply("✅ Reply Raid Done")

# ================= AUTO RAID =================
@app.on_message(filters.group & ~filters.me)
async def auto_raid(client, msg):

    if not msg.from_user:
        return

    user_id = str(msg.from_user.id)
    username = msg.from_user.username or ""

    if user_id not in db["users"] and username not in db["users"]:
        return

    text = random.choice([
        "🔥 spam message 1",
        "😂 spam message 2",
        "⚡ spam message 3"
    ])

    try:
        await msg.reply(text)
    except:
        pass
