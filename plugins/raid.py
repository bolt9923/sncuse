"""
Raid Plugin - Fixed version
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
            data = json.load(f)
            if "users" not in data:
                data["users"] = []
            if "count" not in data:
                data["count"] = 1
            if "scores" not in data:
                data["scores"] = {x: 0 for x in XYZ}
            return data
    except:
        return {"users": [], "count": 1, "scores": {x: 0 for x in XYZ}}


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
    """Load raid plugin with FIXED handlers"""
    
    db = load_db()
    save_db(db)
    
    # Command: .raid
    @client.on(events.NewMessage(pattern=r'^\.raid(?:\s|$)', outgoing=True))
    async def cmd_raid(event):
        db = load_db()
        args = event.pattern_match.string.split()
        
        if len(args) < 2:
            return await event.edit("Usage: `.raid @username`")
        
        user = args[1].replace("@", "").strip()
        
        if user not in db["users"]:
            db["users"].append(user)
            save_db(db)
            msg = await event.edit(f"✅ Raid started on `{user}`")
        else:
            msg = await event.edit(f"⚠️ Already raiding `{user}`")
        
        await asyncio.sleep(3)
        try:
            await event.delete()
        except:
            pass
    
    
    # Command: .draid
    @client.on(events.NewMessage(pattern=r'^\.draid(?:\s|$)', outgoing=True))
    async def cmd_draid(event):
        db = load_db()
        args = event.pattern_match.string.split()
        
        if len(args) < 2:
            return await event.edit("Usage: `.draid @username`")
        
        user = args[1].replace("@", "").strip()
        
        if user in db["users"]:
            db["users"].remove(user)
            save_db(db)
            await event.edit(f"✅ Stopped raiding `{user}`")
        else:
            await event.edit(f"⚠️ `{user}` not in list")
        
        await asyncio.sleep(3)
        try:
            await event.delete()
        except:
            pass
    
    
    # Command: .count
    @client.on(events.NewMessage(pattern=r'^\.count(?:\s|$)', outgoing=True))
    async def cmd_count(event):
        db = load_db()
        args = event.pattern_match.string.split()
        
        if len(args) < 2:
            return await event.edit("Usage: `.count 5`")
        
        try:
            count = int(args[1])
            if count < 1 or count > 50:
                return await event.edit("❌ Range: 1-50")
            
            db["count"] = count
            save_db(db)
            await event.edit(f"✅ Count: `{count}`")
