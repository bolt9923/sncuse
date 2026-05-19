"""
Raid Plugin - Auto-raid on any message from target
Commands:
  .raid <user> - Add user to raid list
  .draid <user> - Remove user from raid list
  .count <num> - Set raid message count
"""

from telethon import events
from telethon.tl.types import SendMessageTypingAction
import json
import random
import asyncio
import logging

logger = logging.getLogger(__name__)

DB_FILE = "raid_db.json"

XYZ = [
    "criminal ki maa ke chut mai mera loda 🤣🤣",
    "crminal aapni maa ke chut dilwao paisa dunga",
    "TERI VAHEEN NHI HAI KYA? 9 MAHINE RUK SAGI VAHEEN DETA HU PHIR TU AUR VOHA DONO ROYAL PAPA BOLNA🤣🤣🤩",
    "TERI MAA K BHOSDE ME AEROPLANEPARK KARKE UDAAN BHAR DUGA criminal beta ✈️🛫",
    "tera cuta hua lula se tu baap bana ka sapna deakh yaha teri maa mai chod diya💣",
    "TERI MAA aur behan ka show karwa diya ss ke liye dm aa jao👅",
    "TERI MAIYA CHOD RAHE HU criminal ab baghna nhi randi ka pilla",
    "TERE BEHEN K CHUT ME CHAKU DAAL KAR CHUT KA KHOON KAR DUGA",
    "TERI MAA KI CHUT KAKTE 🤱 GALI KE KUTTO 🦮 ME BAAT DUNGA PHIR 🍞 BREAD KI TARH KHAYENGE WO TERI MAA KI CHUT",
    "subrat aur shinchan papa se panga lega  ab badh mtt",
    "TERI MAA KI CHUT ME ✋ HATTH DALKE 👶 BACCHE NIKAL DUNGA AUR BACHA BOLEGA DRAGON PAPA😍",
    "TERI BEHN KI CHUT ME KELE KE CHILKE 🍌🍌😍AUR DRAGON KA LUND HILA KE",
    "TERI BHEN KI CHUT ME tera hawarbriz ka pula ghusa ke pelunga",
    "TERI mausi ka chod ke bacha paida karu criminal randi wala😋😛",
]


def load_db():
    try:
        with open(DB_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {
            "users": [],
            "count": 1,
            "scores": {x: 0 for x in XYZ}
        }


def save_db(data):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)


def get_next_reply(db):
    scores = db["scores"]
    min_score = min(scores.values())
    lowest = [k for k, v in scores.items() if v == min_score]
    choice = random.choice(lowest)
    db["scores"][choice] += 1
    save_db(db)
    return choice


def load_raid(client):
    """Load raid plugin"""
    
    db = load_db()
    save_db(db)
    
    # ------------------ .raid Command ------------------
    @client.on(events.NewMessage(pattern=r'^\.raid(?:\s|$)', outgoing=True))
    async def add_raid(event):
        db = load_db()
        
        args = event.pattern_match.string.split()
        if len(args) < 2:
            await event.edit("Usage: `.raid @username/user_id`")
            return
        
        user = args[1].replace("@", "").strip()
        
        if user not in db["users"]:
            db["users"].append(user)
            save_db(db)
            await event.edit(f"✅ Raid enabled on `{user}`")
        else:
            await event.edit(f"⚠️ `{user}` already in raid list")
        
        await asyncio.sleep(3)
        try:
            await event.delete()
        except:
            pass
    
    
    # ------------------ .draid Command ------------------
    @client.on(events.NewMessage(pattern=r'^\.draid(?:\s|$)', outgoing=True))
    async def remove_raid(event):
        db = load_db()
        
        args = event.pattern_match.string.split()
        if len(args) < 2:
            await event.edit("Usage: `.draid @username/user_id`")
            return
        
        user = args[1].replace("@", "").strip()
        
        if user in db["users"]:
            db["users"].remove(user)
            save_db(db)
            await event.edit(f"✅ Removed `{user}` from raid")
        else:
            await event.edit(f"⚠️ `{user}` not found")
        
        await asyncio.sleep(3)
        try:
            await event.delete()
        except:
            pass
    
    
    # ------------------ .count Command ------------------
    @client.on(events.NewMessage(pattern=r'^\.count(?:\s|$)', outgoing=True))
    async def set_count(event):
        db = load_db()
        
        args = event.pattern_match.string.split()
        if len(args) < 2:
            await event.edit("Usage: `.count number`")
            return
        
        try:
            count = int(args[1])
            if count < 1:
                await event.edit("❌ Minimum 1")
                return
            if count > 50:
                await event.edit("❌ Maximum 50")
                return
            
            db["count"] = count
            save_db(db)
            await event.edit(f"✅ Raid count: `{count}`")
        except ValueError:
            await event.edit("❌ Invalid number")
        
        await asyncio.sleep(3)
        try:
            await event.delete()
        except:
            pass
    
    
    # ------------------ Auto Raid Handler ------------------
    @client.on(events.NewMessage(incoming=True))
    async def auto_raid(event):
        """Raid when target sends ANY message"""
        if not event.is_group and not event.is_channel:
            return
        if event.out:
            return
        if not event.sender:
            return
        
        db = load_db()
        
        user_id = str(event.sender_id)
        username = event.sender.username or ""
        
        if user_id not in db["users"] and username not in db["users"]:
            return
        
        for i in range(db["count"]):
            try:
                text = get_next_reply(db)
                await client.send_action(event.chat_id, SendMessageTypingAction())
                await asyncio.sleep(random.randint(2, 5))
                await event.reply(text)
            except Exception as e:
                logger.error(f"Raid error: {e}")
                break
    
    
    logger.info("✅ Raid plugin loaded (commands: .raid, .draid, .count)")


load = load_raid
init = load_raid
