"""
ReRaid Plugin - Reply-based Raid for Telethon
Commands:
  .reraid <user> - Enable reply-raid on user
  .dreraid <user> - Disable reply-raid on user
  .rcount <num> - Set reply-raid message count
Auto-spams when targeted user replies to any message
"""

from telethon import events
from telethon.tl.types import SendMessageTypingAction
import json
import random
import asyncio
import logging

logger = logging.getLogger(__name__)

DB_FILE = "reraid_db.json"

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
    """Load reraid database"""
    try:
        with open(DB_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            # Ensure all keys exist
            if "users" not in data:
                data["users"] = []
            if "count" not in data:
                data["count"] = 5
            if "scores" not in data:
                data["scores"] = {x: 0 for x in XYZ}
            return data
    except (FileNotFoundError, json.JSONDecodeError):
        return {
            "users": [],
            "count": 5,
            "scores": {x: 0 for x in XYZ}
        }


def save_db(data):
    """Save reraid database"""
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)


def get_next_reply(db):
    """Get weighted random reply"""
    scores = db["scores"]
    min_score = min(scores.values())
    lowest = [k for k, v in scores.items() if v == min_score]
    choice = random.choice(lowest)
    db["scores"][choice] += 1
    save_db(db)
    return choice


def load_reraid(client):
    """Load reraid plugin"""
    
    # Initialize DB
    db = load_db()
    save_db(db)
    
    # ------------------ .reraid Command ------------------
    @client.on(events.NewMessage(pattern=r'^\.reraid(?:\s|$)', outgoing=True))
    async def add_reraid(event):
        """Enable reply-raid on user"""
        db = load_db()
        
        args = event.pattern_match.string.split()
        if len(args) < 2:
            await event.edit("Usage: `.reraid @username/user_id`")
            return
        
        user = args[1].replace("@", "").strip()
        
        if user not in db["users"]:
            db["users"].append(user)
            save_db(db)
            msg = await event.edit(f"✅ Reply-raid enabled on `{user}`\nThey will be spammed when they reply to any message")
        else:
            msg = await event.edit(f"⚠️ `{user}` already has reply-raid enabled")
        
        await asyncio.sleep(3)
        try:
            await event.delete()
        except:
            pass
    
    
    # ------------------ .dreraid Command ------------------
    @client.on(events.NewMessage(pattern=r'^\.dreraid(?:\s|$)', outgoing=True))
    async def remove_reraid(event):
        """Disable reply-raid on user"""
        db = load_db()
        
        args = event.pattern_match.string.split()
        if len(args) < 2:
            await event.edit("Usage: `.dreraid @username/user_id`")
            return
        
        user = args[1].replace("@", "").strip()
        
        if user in db["users"]:
            db["users"].remove(user)
            save_db(db)
            msg = await event.edit(f"✅ Reply-raid disabled for `{user}`")
        else:
            msg = await event.edit(f"⚠️ `{user}` not in reply-raid list")
        
        await asyncio.sleep(3)
        try:
            await event.delete()
        except:
            pass
    
    
    # ------------------ .rcount Command ------------------
    @client.on(events.NewMessage(pattern=r'^\.rcount(?:\s|$)', outgoing=True))
    async def set_rcount(event):
        """Set reply-raid message count"""
        db = load_db()
        
        args = event.pattern_match.string.split()
        if len(args) < 2:
            await event.edit("Usage: `.rcount number`")
            return
        
        try:
            count = int(args[1])
            if count < 1:
                await event.edit("❌ Minimum count is 1")
                return
            if count > 100:
                await event.edit("❌ Maximum count is 100")
                return
            
            db["count"] = count
            save_db(db)
            msg = await event.edit(f"✅ Reply-raid count set to `{count}`")
        except ValueError:
            msg = await event.edit("❌ Invalid number")
        
        await asyncio.sleep(3)
        try:
            await event.delete()
        except:
            pass
    
    
    # ------------------ .rlist Command ------------------
    @client.on(events.NewMessage(pattern=r'^\.rlist$', outgoing=True))
    async def list_reraid(event):
        """Show reply-raid targets"""
        db = load_db()
        
        if not db["users"]:
            await event.edit("📋 No users in reply-raid list")
            return
        
        text = "📋 **Reply-Raid Targets:**\n\n"
        for i, user in enumerate(db["users"], 1):
            text += f"{i}. `{user}`\n"
        text += f"\nCount: `{db['count']}` messages per reply"
        
        await event.edit(text)
    
    
    # ------------------ Reply Raid Handler ------------------
    @client.on(events.NewMessage(incoming=True))
    async def reply_raid_trigger(event):
        """Trigger raid when target replies to any message"""
        # Must be reply
        if not event.is_reply:
            return
        
        # Must be group
        if not event.is_group and not event.is_channel:
            return
        
        # Not from self
        if event.out:
            return
        
        if not event.sender:
            return
        
        db = load_db()
        
        user_id = str(event.sender_id)
        username = event.sender.username or ""
        
        # Check if user is targeted
        if user_id not in db["users"] and username not in db["users"]:
            return
        
        # Get the message they're replying to
        try:
            replied_msg = await event.get_reply_message()
            if not replied_msg:
                return
        except:
            return
        
        # Spam them
        logger.info(f"[ReRaid] {username or user_id} replied, raiding...")
        
        for i in range(db["count"]):
            try:
                text = get_next_reply(db)
                
                # Typing action
                await client.send_action(event.chat_id, SendMessageTypingAction())
                
                # Delay
                await asyncio.sleep(random.randint(1, 3))
                
                # Reply to their reply
                await event.reply(text)
                
            except Exception as e:
                logger.error(f"[ReRaid] Error: {e}")
                break
    
    
    logger.info("✅ ReRaid plugin loaded (commands: .reraid, .dreraid, .rcount, .rlist)")


# Aliases
load = load_reraid
init = load_reraid


# Standalone
if __name__ == "__main__":
    from telethon import TelegramClient
    
    print("🚀 ReRaid Plugin - Standalone Mode")
    print("Triggers when target replies to any message")
    print("=" * 40)
    
    API_ID = int(input("API ID: "))
    API_HASH = input("API Hash: ")
    
    client = TelegramClient("reraid_session", API_ID, API_HASH)
    load_reraid(client)
    
    client.start()
    print("✅ Started!")
    print("Commands: .reraid @user, .dreraid @user, .rcount 10, .rlist")
    client.run_until_disconnected()
