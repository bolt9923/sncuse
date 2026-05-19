"""
BanAll Plugin for SNC UserBot
Command: .banall
Description: Bans all non-admin members from current group
"""

from telethon import events
from telethon.errors import FloodWaitError, ChatAdminRequiredError, UserAdminInvalidError
import asyncio
import logging

logger = logging.getLogger(__name__)


async def safe_ban(client, chat_id, user_id, name=None):
    """Ban user with flood wait retry"""
    target = name or user_id
    try:
        await client.edit_permissions(chat_id, user_id, view_messages=False)
        logger.info(f"[BanAll] Banned {target}")
        return True
    except FloodWaitError as e:
        logger.warning(f"[BanAll] FloodWait {e.seconds}s for {target}")
        await asyncio.sleep(e.seconds)
        return await safe_ban(client, chat_id, user_id, name)
    except UserAdminInvalidError:
        logger.warning(f"[BanAll] Skip admin {target}")
    except Exception as e:
        logger.error(f"[BanAll] Failed {target}: {e}")
    return False


def load_banall(client):
    """
    Load banall plugin.
    Called by main.py after successful login.
    """
    
    @client.on(events.NewMessage(pattern=r'^\.banall$', outgoing=True))
    async def banall_handler(event):
        """Handle .banall command"""
        chat_id = event.chat_id
        
        # Check permissions
        try:
            perms = await client.get_permissions(chat_id, 'me')
            if not perms.is_admin:
                return await event.reply("❌ Not admin!")
            if not perms.ban_users:
                return await event.reply("❌ No ban permission!")
        except Exception as e:
            return await event.reply(f"⚠️ Error: {e}")
        
        status = await event.reply("📋 Fetching users...")
        banned = failed = skipped = 0
        
        try:
            me = await client.get_me()
            to_ban = []
            
            # Collect targets
            async for user in client.iter_participants(chat_id):
                if user.id == me.id or user.bot:
                    skipped += 1
                    continue
                to_ban.append(user)
            
            total = len(to_ban)
            if not total:
                return await status.edit("✅ No users to ban.")
            
            await status.edit(f"🔍 Found {total} users. Banning...")
            
            # Ban loop
            for i, user in enumerate(to_ban, 1):
                name = user.username or user.first_name or str(user.id)
                
                if await safe_ban(client, chat_id, user.id, name):
                    banned += 1
                else:
                    failed += 1
                
                # Progress update every 10
                if i % 10 == 0 or i == total:
                    try:
                        await status.edit(
                            f"⏳ {i}/{total}\n"
                            f"✅ Banned: {banned}\n"
                            f"❌ Failed: {failed}\n"
                            f"⏭️ Skipped: {skipped}"
                        )
                    except:
                        pass
                
                await asyncio.sleep(1.5)  # Rate limit
            
        except ChatAdminRequiredError:
            await status.edit("❌ Admin rights required!")
        except Exception as e:
            logger.error(f"[BanAll] Error: {e}")
            await status.edit(f"💥 Error: {e}")
        
        # Final report
        await status.edit(
            f"✅ **BanAll Done**\n\n"
            f"📊 Total: {banned + failed}\n"
            f"✔️ Banned: {banned}\n"
            f"✖️ Failed: {failed}\n"
            f"⏭️ Skipped: {skipped}"
        )
    
    logger.info("✅ BanAll plugin loaded")


# Compatibility aliases
load = load_banall
init = load_banall
