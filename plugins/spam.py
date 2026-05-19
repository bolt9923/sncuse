"""
Spam Plugin - Manual message spamming
Commands:
  .spam <count> <message> - Spam message X times
  .delspam <count> <message> - Spam and delete after
  .fspam <message> - Fast spam (50x)
"""

from telethon import events
import asyncio
import logging

logger = logging.getLogger(__name__)


def load_spam(client):
    """Load spam plugin"""
    
    # ------------------ .spam Command ------------------
    @client.on(events.NewMessage(pattern=r'^\.spam(?:\s|$)', outgoing=True))
    async def spam_handler(event):
        """Spam message specified times"""
        args = event.pattern_match.string.split(maxsplit=2)
        
        if len(args) < 3:
            await event.edit("Usage: `.spam 10 message here`")
            return
        
        try:
            count = int(args[1])
            if count < 1:
                await event.edit("❌ Minimum 1")
                return
            if count > 100:
                await event.edit("❌ Maximum 100")
                return
        except ValueError:
            await event.edit("❌ Invalid number")
            return
        
        message = args[2]
        
        # Delete command
        try:
            await event.delete()
        except:
            pass
        
        # Spam
        for i in range(count):
            try:
                await client.send_message(event.chat_id, message)
                await asyncio.sleep(0.5)  # Small delay to avoid flood
            except Exception as e:
                logger.error(f"Spam error: {e}")
                break
    
    
    # ------------------ .delspam Command ------------------
    @client.on(events.NewMessage(pattern=r'^\.delspam(?:\s|$)', outgoing=True))
    async def delspam_handler(event):
        """Spam then delete all"""
        args = event.pattern_match.string.split(maxsplit=2)
        
        if len(args) < 3:
            await event.edit("Usage: `.delspam 10 message`")
            return
        
        try:
            count = int(args[1])
            if count < 1 or count > 50:
                await event.edit("❌ Range: 1-50")
                return
        except ValueError:
            await event.edit("❌ Invalid number")
            return
        
        message = args[2]
        sent_msgs = []
        
        try:
            await event.delete()
        except:
            pass
        
        # Spam and store IDs
        for i in range(count):
            try:
                msg = await client.send_message(event.chat_id, message)
                sent_msgs.append(msg.id)
                await asyncio.sleep(0.3)
            except Exception as e:
                logger.error(f"Delspam error: {e}")
                break
        
        # Wait then delete all
        await asyncio.sleep(5)
        for msg_id in sent_msgs:
            try:
                await client.delete_messages(event.chat_id, msg_id)
            except:
                pass
    
    
    # ------------------ .fspam Command ------------------
    @client.on(events.NewMessage(pattern=r'^\.fspam(?:\s|$)', outgoing=True))
    async def fspam_handler(event):
        """Fast spam 50x"""
        args = event.pattern_match.string.split(maxsplit=1)
        
        if len(args) < 2:
            await event.edit("Usage: `.fspam message`")
            return
        
        message = args[1]
        
        try:
            await event.delete()
        except:
            pass
        
        # Fast spam 50 times
        for i in range(50):
            try:
                await client.send_message(event.chat_id, message)
            except Exception as e:
                logger.error(f"Fspam error: {e}")
                break
    
    
    # ------------------ .stopspam Command ------------------
    @client.on(events.NewMessage(pattern=r'^\.stopspam$', outgoing=True))
    async def stopspam_handler(event):
        """Placeholder for stopping spam (manual ctrl+c)"""
        await event.edit("⚠️ To stop spam: Press Ctrl+C or disconnect")
        await asyncio.sleep(3)
        try:
            await event.delete()
        except:
            pass
    
    
    logger.info("✅ Spam plugin loaded (commands: .spam, .delspam, .fspam)")


load = load_spam
init = load_spam
