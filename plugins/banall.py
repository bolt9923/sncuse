from telethon import TelegramClient, events
from telethon.errors import FloodWaitError, ChatAdminRequiredError, UserAdminInvalidError
import asyncio
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# CONFIGURATION - Fill these in with your credentials
API_ID = 12345678  # Get from https://my.telegram.org/apps
API_HASH = 'your_api_hash_here'  # Get from https://my.telegram.org/apps
# BOT_TOKEN = 'your_bot_token_here'  # Uncomment this line if using as bot account instead of user

# Initialize the client
client = TelegramClient('banall_session', API_ID, API_HASH)

async def safe_ban(chat_id, user_id, username=None):
    """
    Ban a user with automatic flood wait handling.
    Retries after flood wait expires.
    """
    target = username or user_id
    try:
        # view_messages=False bans the user from the chat
        await client.edit_permissions(chat_id, user_id, view_messages=False)
        logger.info(f"Successfully banned {target}")
        return True
    except FloodWaitError as e:
        logger.warning(f"FloodWait encountered: {e.seconds} seconds. Waiting...")
        await asyncio.sleep(e.seconds)
        # Retry after flood wait
        return await safe_ban(chat_id, user_id, username)
    except UserAdminInvalidError:
        logger.warning(f"Cannot ban {target}: User is an admin")
    except Exception as e:
        logger.error(f"Failed to ban {target}: {e}")
    return False

@client.on(events.NewMessage(pattern=r'^\.banall$', outgoing=True))
async def banall_handler(event):
    """
    Handle the .banall command.
    Bans all non-bot members from the current chat.
    """
    chat_id = event.chat_id
    
    # Check if we have ban permissions
    try:
        perms = await client.get_permissions(chat_id, 'me')
        if not perms.is_admin:
            await event.reply("❌ Error: I am not an admin in this chat!")
            return
        if not perms.ban_users:
            await event.reply("❌ Error: I don't have permission to ban users!")
            return
    except Exception as e:
        await event.reply(f"⚠️ Failed to check permissions: {e}")
        return
    
    # Send initial status message
    status_msg = await event.reply("📋 Fetching participant list...")
    
    banned_count = 0
    failed_count = 0
    
    try:
        # Get list of participants to ban
        me = await client.get_me()
        participants = []
        
        async for user in client.iter_participants(chat_id):
            # Skip bots and yourself
            if user.bot or user.id == me.id:
                continue
            participants.append(user)
        
        total = len(participants)
        if total == 0:
            await status_msg.edit("No users to ban.")
            return
            
        await status_msg.edit(f"🔍 Found {total} users. Starting ban process...")
        
        # Process each user
        for idx, user in enumerate(participants, 1):
            name = user.username or user.first_name or str(user.id)
            
            success = await safe_ban(chat_id, user.id, name)
            if success:
                banned_count += 1
            else:
                failed_count += 1
            
            # Update status every 10 users
            if idx % 10 == 0:
                try:
                    await status_msg.edit(
                        f"⏳ Banning users...\n"
                        f"Progress: {idx}/{total}\n"
                        f"✅ Banned: {banned_count}\n"
                        f"❌ Failed: {failed_count}"
                    )
                except:
                    pass
            
            # Sleep to avoid flood waits (1.5 seconds between bans)
            await asyncio.sleep(1.5)
            
    except ChatAdminRequiredError:
        await status_msg.edit("❌ Error: Admin rights are required!")
        return
    except Exception as e:
        logger.error(f"Critical error in banall: {e}")
        await status_msg.edit(f"💥 Critical Error: {e}")
        return
    
    # Final report
    await status_msg.edit(
        f"✅ **Ban All Complete**\n\n"
        f"📊 Total processed: {banned_count + failed_count}\n"
        f"✔️ Successfully banned: {banned_count}\n"
        f"✖️ Failed: {failed_count}"
    )

def main():
    """Start the client"""
    print("Starting Telethon client...")
    print("Note: If using a user account, you'll need to enter your phone number and verification code.")
    
    # Start the client
    # For bot accounts only, uncomment the next line and comment the one after:
    # client.start(bot_token=BOT_TOKEN)
    client.start()
    
    print("Client started successfully!")
    print("Send '.banall' in any group where you have admin rights.")
    print("Press Ctrl+C to stop.")
    
    # Keep the client running
    client.run_until_disconnected()

if __name__ == "__main__":
    main()
