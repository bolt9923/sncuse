"""
Raid Plugin - Fully Fixed Version
"""

from telethon import events
import json
import random
import asyncio
import logging
import os

logger = logging.getLogger(__name__)

DB_FILE = "raid_db.json"

XYZ = [
    "criminal ki maa ke chut mai mera loda 🤣🤣",
    "TERI VAHEEN NHI HAI KYA? 9 MAHINE RUK SAGI VAHEEN DETA HU PHIR TU AUR VOHA DONO ROYAL PAPA BOLNA🤣🤣🤩",
    "TERI MAA K BHOSDE ME AEROPLANE PARK KARKE UDAAN BHAR DUGA criminal beta ✈️🛫",
    "tera cuta hua lula se tu baap bana ka sapna deakh yaha teri maa mai chod diya💣",
    "TERI MAA aur behan ka show karwa diya ss ke liye dm aa jao👅",
    "TERI MAIYA CHOD RAHE HU criminal ab baghna nhi randi ka pilla",
    "TERE BEHEN K CHUT ME CHAKU DAAL KAR CHUT KA KHOON KAR DUGA",
    "TERI MAA KI CHUT KAKTE 🤱 GALI KE KUTTO 🦮 ME BAAT DUNGA PHIR 🍞 BREAD KI TARH KHAYENGE WO TERI MAA KI CHUT",
    "subrat aur shinchan papa se panga lega ab badh mtt",
    "TERI MAA KI CHUT ME ✋ HATTH DALKE 👶 BACCHE NIKAL DUNGA AUR BACHA BOLEGA DRAGON PAPA😍",
    "TERI BEHN KI CHUT ME KELE KE CHILKE 🍌🍌😍AUR DRAGON KA LUND HILA KE",
    "TERI BHEN KI CHUT ME tera hawarbriz ka pula ghusa ke pelunga",
    "TERI mausi ka chod ke bacha paida karu criminal randi wala😋😛",
]


# ========================= DATABASE =========================

def load_db():
    try:
        if not os.path.exists(DB_FILE):
            return {
                "users": [],
                "count": 1,
                "scores": {x: 0 for x in XYZ}
            }

        with open(DB_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)

        if "users" not in data:
            data["users"] = []

        if "count" not in data:
            data["count"] = 1

        if "scores" not in data:
            data["scores"] = {x: 0 for x in XYZ}

        return data

    except Exception as e:
        logger.error(f"DB Load Error: {e}")

        return {
            "users": [],
            "count": 1,
            "scores": {x: 0 for x in XYZ}
        }


def save_db(data):
    try:
        with open(DB_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)

    except Exception as e:
        logger.error(f"DB Save Error: {e}")


def get_next_reply(db):
    scores = db["scores"]

    min_score = min(scores.values())

    lowest = [
        msg for msg, score in scores.items()
        if score == min_score
    ]

    choice = random.choice(lowest)

    db["scores"][choice] += 1

    save_db(db)

    return choice


# ========================= MAIN =========================

def load_raid(client):

    db = load_db()
    save_db(db)

    logger.info("✅ Raid plugin loaded")

    # ========================= .raid =========================

    @client.on(events.NewMessage(
        pattern=r'^\.raid(?:\s|$)',
        outgoing=True
    ))
    async def cmd_raid(event):

        db = load_db()

        args = event.raw_text.split()

        if len(args) < 2:
            return await event.edit(
                "Usage:\n`.raid @username`"
            )

        user = args[1].replace("@", "").lower().strip()

        if user not in db["users"]:

            db["users"].append(user)

            save_db(db)

            await event.edit(
                f"✅ Raid started on `{user}`"
            )

        else:
            await event.edit(
                f"⚠️ Already raiding `{user}`"
            )

        await asyncio.sleep(3)

        try:
            await event.delete()
        except:
            pass

    # ========================= .draid =========================

    @client.on(events.NewMessage(
        pattern=r'^\.draid(?:\s|$)',
        outgoing=True
    ))
    async def cmd_draid(event):

        db = load_db()

        args = event.raw_text.split()

        if len(args) < 2:
            return await event.edit(
                "Usage:\n`.draid @username`"
            )

        user = args[1].replace("@", "").lower().strip()

        if user in db["users"]:

            db["users"].remove(user)

            save_db(db)

            await event.edit(
                f"✅ Removed `{user}`"
            )

        else:
            await event.edit(
                f"⚠️ `{user}` not found"
            )

        await asyncio.sleep(3)

        try:
            await event.delete()
        except:
            pass

    # ========================= .count =========================

    @client.on(events.NewMessage(
        pattern=r'^\.count(?:\s|$)',
        outgoing=True
    ))
    async def cmd_count(event):

        db = load_db()

        args = event.raw_text.split()

        if len(args) < 2:
            return await event.edit(
                "Usage:\n`.count 5`"
            )

        try:
            count = int(args[1])

            if count < 1 or count > 50:
                return await event.edit(
                    "❌ Range: 1-50"
                )

            db["count"] = count

            save_db(db)

            await event.edit(
                f"✅ Count set to `{count}`"
            )

        except:
            await event.edit(
                "❌ Invalid number"
            )

        await asyncio.sleep(3)

        try:
            await event.delete()
        except:
            pass

    # ========================= .raidlist =========================

    @client.on(events.NewMessage(
        pattern=r'^\.raidlist(?:\s|$)',
        outgoing=True
    ))
    async def cmd_raidlist(event):

        db = load_db()

        users = db["users"]

        if not users:
            return await event.edit(
                "❌ No users in raid list"
            )

        text = "⚔️ RAID LIST ⚔️\n\n"

        for x in users:
            text += f"• `{x}`\n"

        text += f"\nCount: `{db['count']}`"

        await event.edit(text)

    # ========================= AUTO RAID =========================

    @client.on(events.NewMessage(incoming=True))
    async def auto_raid(event):

        try:

            # Only groups
            if not event.is_group:
                return

            # Ignore own messages
            if event.out:
                return

            sender = await event.get_sender()

            if not sender:
                return

            db = load_db()

            user_id = str(sender.id)

            username = (
                sender.username.lower()
                if sender.username
                else ""
            )

            targets = [
                str(x).lower()
                for x in db["users"]
            ]

            logger.info(
                f"[CHECK] {username} | {user_id}"
            )

            # Check target
            if (
                username not in targets
                and user_id not in targets
            ):
                return

            logger.info(
                f"[RAID STARTED] {username or user_id}"
            )

            # Send replies
            for i in range(db["count"]):

                try:

                    text = get_next_reply(db)

                    # Typing
                    await client.send_chat_action(
                        event.chat_id,
                        "typing"
                    )

                    await asyncio.sleep(
                        random.randint(1, 3)
                    )

                    # Reply
                    await event.reply(text)

                    logger.info(
                        f"[SENT] {i+1}/{db['count']}"
                    )

                except Exception as e:
                    logger.error(
                        f"[SEND ERROR] {e}"
                    )
                    break

        except Exception as e:
            logger.error(
                f"[AUTO RAID ERROR] {e}"
            )


# ========================= ALIASES =========================

load = load_raid
init = load_raid
