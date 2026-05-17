import json
import asyncio
from pyrogram import filters
from pyrogram.enums import ChatAction
from main import app

DB_FILE = "db.json"

# ================= LOAD DB =================
def load_db():
    try:
        with open(DB_FILE, "r") as f:
            return json.load(f)
    except:
        return {"users": [], "count": 1}

def save_db(data):
    with open(DB_FILE, "w") as f:
        json.dump(data, f, indent=4)

db = load_db()

# ================= ADD USER =================
@app.on_message(filters.me & filters.command("rraid", prefixes="!"))
async def add_user(_, msg):

    if len(msg.command) < 2:
        return await msg.reply("Usage: !rraid @user")

    user = msg.command[1].replace("@", "")

    if user not in db["users"]:
        db["users"].append(user)
        save_db(db)
        await msg.reply(f"✅ Added: {user}")
    else:
        await msg.reply("Already exists")

# ================= REMOVE USER =================
@app.on_message(filters.me & filters.command("draid", prefixes="!"))
async def remove_user(_, msg):

    if len(msg.command) < 2:
        return await msg.reply("Usage: !draid @user")

    user = msg.command[1].replace("@", "")

    if user in db["users"]:
        db["users"].remove(user)
        save_db(db)
        await msg.reply(f"❌ Removed: {user}")
    else:
        await msg.reply("Not found")

# ================= COUNT =================
@app.on_message(filters.me & filters.command("count", prefixes="!"))
async def set_count(_, msg):

    if len(msg.command) < 2:
        return await msg.reply("Usage: !count 1-10")

    try:
        db["count"] = int(msg.command[1])
        save_db(db)
        await msg.reply(f"✅ Count set: {db['count']}")
    except:
        await msg.reply("Invalid number")

# ================= SAFE AUTO REPLY =================
@app.on_message(filters.group & ~filters.me)
async def auto_reply(client, msg):

    if not msg.from_user:
        return

    user_id = str(msg.from_user.id)
    username = msg.from_user.username or ""

    if user_id not in db["users"] and username not in db["users"]:
        return

    for _ in range(db["count"]):

        try:
            await client.send_chat_action(msg.chat.id, ChatAction.TYPING)
            await asyncio.sleep(2)

            await msg.reply("📢 Automated reply enabled")

        except:
            pass
