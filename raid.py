import json
import random
import asyncio
from pyrogram import filters
from pyrogram.enums import ChatAction
from main import app

DB_FILE = "db.json"

# ================= DATA =================
XYZ = [
    "reply 1",
    "reply 2",
    "reply 3"
]

# ================= DB =================
def load_db():
    try:
        with open(DB_FILE, "r") as f:
            return json.load(f)
    except:
        return {
            "users": [],
            "count": 1,
            "scores": {x: 0 for x in XYZ}
        }

def save_db(data):
    with open(DB_FILE, "w") as f:
        json.dump(data, f, indent=4)

db = load_db()

# ================= SMART REPLY =================
def get_next_reply():
    scores = db["scores"]
    min_score = min(scores.values())

    lowest = [k for k, v in scores.items() if v == min_score]

    choice = random.choice(lowest)
    db["scores"][choice] += 1
    save_db(db)

    return choice

# ================= ADD USER =================
@app.on_message(filters.me & filters.command("rraid", prefixes="!"))
async def add_user(_, msg):

    user = msg.command[1].replace("@", "")

    if user not in db["users"]:
        db["users"].append(user)
        save_db(db)
        await msg.reply(f"Added {user}")
    else:
        await msg.reply("Already added")

# ================= REMOVE USER =================
@app.on_message(filters.me & filters.command("draid", prefixes="!"))
async def remove_user(_, msg):

    user = msg.command[1].replace("@", "")

    if user in db["users"]:
        db["users"].remove(user)
        save_db(db)
        await msg.reply("Removed")
    else:
        await msg.reply("Not found")

# ================= COUNT =================
@app.on_message(filters.me & filters.command("count", prefixes="!"))
async def set_count(_, msg):

    try:
        db["count"] = int(msg.command[1])
        save_db(db)
        await msg.reply(f"Count set {db['count']}")
    except:
        await msg.reply("Invalid number")

# ================= GROUP RAID =================
@app.on_message(filters.group & ~filters.me)
async def auto_reply(client, msg):

    if not msg.from_user:
        return

    user_id = str(msg.from_user.id)
    username = msg.from_user.username or ""

    if user_id not in db["users"] and username not in db["users"]:
        return

    for _ in range(db["count"]):

        text = get_next_reply()

        await client.send_chat_action(msg.chat.id, ChatAction.TYPING)

        await asyncio.sleep(random.randint(2, 5))

        await msg.reply(text)

print("🔥 RAID MODULE LOADED")
