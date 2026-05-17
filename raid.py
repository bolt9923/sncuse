from core import app
from pyrogram import filters
import json

DB_FILE = "db.json"

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

# ================= TEST =================
@app.on_message(filters.me & filters.command("test", prefixes="!"))
async def test(_, msg):
    await msg.reply("✅ RAID MODULE WORKING")

# ================= ADD USER =================
@app.on_message(filters.me & filters.command("rraid", prefixes="!"))
async def rraid(_, msg):

    if len(msg.command) < 2:
        return await msg.reply("Usage: !rraid @user")

    user = msg.command[1].replace("@", "")

    if user not in db["users"]:
        db["users"].append(user)
        save_db(db)
        await msg.reply("✅ Added")
    else:
        await msg.reply("Already exists")

# ================= REPLY RAID =================
@app.on_message(filters.me & filters.command("replyraid", prefixes="!"))
async def replyraid(_, msg):

    if not msg.reply_to_message:
        return await msg.reply("⚠️ Reply to a message first")

    if len(msg.command) < 2:
        return await msg.reply("Usage: !replyraid text")

    text = msg.text.split(" ", 1)

    if len(text) < 2:
        return await msg.reply("⚠️ Text missing")

    text = text[1]

    for _ in range(db.get("count", 1)):

        try:
            await msg.reply_to_message.reply(text)
        except:
            pass

    await msg.reply("✅ Reply Raid Done")
