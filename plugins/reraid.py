# Fixed `reraid.py` Full Code

```python
from telethon import events
from telethon.tl.types import User
import asyncio
import json
import os

DB_FILE = "reraid_db.json"

# ---------------- DATABASE ---------------- #

def load_db():
    if not os.path.exists(DB_FILE):
        return {
            "enabled": True,
            "users": [],
            "count": 5,
            "reply": "RAID"
        }

    with open(DB_FILE, "r") as f:
        return json.load(f)


def save_db(data):
    with open(DB_FILE, "w") as f:
        json.dump(data, f, indent=4)


# ---------------- DEFAULT DB ---------------- #

db = load_db()


# ---------------- COMMANDS ---------------- #

@client.on(events.NewMessage(pattern=r"^\.reraid (.+)"))
async def add_user(event):
    if not event.sender_id == OWNER_ID:
        return

    args = event.pattern_match.group(1).split()

    if not args:
        return await event.reply("Usage: .reraid username")

    user = args[0].replace("@", "").lower().strip()

    if user in db["users"]:
        return await event.reply("User already added")

    db["users"].append(user)
    save_db(db)

    await event.reply(f"Added user for reply raid: @{user}")


@client.on(events.NewMessage(pattern=r"^\.delreraid (.+)"))
async def del_user(event):
    if not event.sender_id == OWNER_ID:
        return

    args = event.pattern_match.group(1).split()

    if not args:
        return await event.reply("Usage: .delreraid username")

    user = args[0].replace("@", "").lower().strip()

    if user not in db["users"]:
        return await event.reply("User not found")

    db["users"].remove(user)
    save_db(db)

    await event.reply(f"Removed user: @{user}")


@client.on(events.NewMessage(pattern=r"^\.rlist$"))
async def list_users(event):
    if not db["users"]:
        return await event.reply("No users added")

    text = "**Reply Raid Users:**\n\n"

    for user in db["users"]:
        text += f"• @{user}\n"

    await event.reply(text)


@client.on(events.NewMessage(pattern=r"^\.rcount (\d+)"))
async def set_count(event):
    if not event.sender_id == OWNER_ID:
        return

    count = int(event.pattern_match.group(1))

    db["count"] = count
    save_db(db)

    await event.reply(f"Reply count set to {count}")


@client.on(events.NewMessage(pattern=r"^\.rreply (.+)"))
async def set_reply(event):
    if not event.sender_id == OWNER_ID:
        return

    reply_text = event.pattern_match.group(1)

    db["reply"] = reply_text
    save_db(db)

    await event.reply(f"Reply text updated to: {reply_text}")


@client.on(events.NewMessage(pattern=r"^\.rraid (on|off)$"))
async def toggle_raid(event):
    if not event.sender_id == OWNER_ID:
        return

    status = event.pattern_match.group(1)

    db["enabled"] = status == "on"
    save_db(db)

    await event.reply(f"Reply raid {'enabled' if db['enabled'] else 'disabled'}")


# ---------------- AUTO REPLY RAID ---------------- #

@client.on(events.NewMessage)
async def auto_reply_raid(event):
    try:
        if not db.get("enabled"):
            return

        if event.sender_id == OWNER_ID:
            return

        sender = await event.get_sender()

        if not isinstance(sender, User):
            return

        user_id = str(sender.id)
        username = (sender.username or "").lower().strip()

        targets = [str(x).lower().strip() for x in db["users"]]

        if user_id not in targets and username not in targets:
            return

        if not event.is_reply:
            return

        for _ in range(db["count"]):
            await event.reply(db["reply"])
            await asyncio.sleep(0.3)

    except Exception as e:
        print(f"Reply Raid Error: {e}")

```

## Commands

```bash
.reraid username
.delreraid username
.rlist
.rcount 5
.rreply hello
.rraid on
.rraid off
```

## Example

```bash
.reraid tguser
.rcount 10
.rreply RAID
```

Now when `@tguser` replies to someone in group, bot/userbot will automatically send `RAID` 10 times.
