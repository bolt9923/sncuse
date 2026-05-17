import json
from pyrogram import filters
from core import app

DB_FILE = "db.json"

# ================= DB =================
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

# ================= RRAID (ADD USER) =================
@app.on_message(filters.me & filters.command("rraid", prefixes="!"))
async def rraid(_, msg):

    if len(msg.command) < 2:
        return await msg.reply("Usage: !rraid @username or user_id")

    user = msg.command[1].replace("@", "")

    if user not in db["users"]:
        db["users"].append(user)
        save_db(db)
        await msg.reply(f"✅ Added: {user}")
    else:
        await msg.reply("⚠️ Already exists")

# ================= DRAID (REMOVE USER) =================
@app.on_message(filters.me & filters.command("draid", prefixes="!"))
async def draid(_, msg):

    if len(msg.command) < 2:
        return await msg.reply("Usage: !draid @username")

    user = msg.command[1].replace("@", "")

    if user in db["users"]:
        db["users"].remove(user)
        save_db(db)
        await msg.reply(f"❌ Removed: {user}")
    else:
        await msg.reply("Not found")

# ================= COUNT SET =================
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

# ================= SHOW USERS =================
@app.on_message(filters.me & filters.command("list", prefixes="!"))
async def list_users(_, msg):

    users = db.get("users", [])

    if not users:
        return await msg.reply("No users added")

    text = "📌 RAID USERS:\n\n"
    text += "\n".join([f"- {u}" for u in users])

    await msg.reply(text)
