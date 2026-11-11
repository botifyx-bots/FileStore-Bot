# Botifyx bots 
# @BotifyX_Pro_Botz

from pyrogram import Client, filters
from pyrogram.types import Message
from datetime import datetime
from datetime import timedelta
import re
from config import OWNER_ID
#--------------------------------

def parse_duration(duration_str: str) -> timedelta:
    """
    Parse duration strings like '1 day', '2 weeks', '3 months', '1 year' into timedelta
    Returns None if the format is invalid
    """
    duration_str = duration_str.lower().strip()
    match = re.match(r'^(\d+)\s*(day|days|week|weeks|month|months|year|years)$', duration_str)

    if not match:
        return None

    amount = int(match.group(1))
    unit = match.group(2).rstrip('s')  # Remove 's' from plural forms

    if unit == 'day':
        return timedelta(days=amount)
    elif unit == 'week':
        return timedelta(weeks=amount)
    elif unit == 'month':
        return timedelta(days=amount * 30)  # Approximate
    elif unit == 'year':
        return timedelta(days=amount * 365)  # Approximate

    return None

#========================================================================#

@Client.on_message(filters.command('addpremium') & filters.private)
async def add_admin_command(client: Client, message: Message):
    if message.from_user.id != OWNER_ID:
        return await message.reply_text("<blockquote>✗ ᴏɴʟʏ ᴛʜᴇ ᴏᴡɴᴇʀ ᴄᴀɴ ᴜsᴇ ᴛʜɪs ᴄᴏᴍᴍᴀɴᴅ!</blockquote>")

    usage = """<blockquote>✎ <b>ᴜsᴀɢᴇ:</b> /addpremium userid [duration]</blockquote>
<blockquote>›› /addpremium 123456 1 day
›› /addpremium 123456 2 weeks
›› /addpremium 123456 1 month
›› /addpremium 123456 1 year
›› /addpremium 123456 (ꜰᴏʀ ᴘᴇʀᴍᴀɴᴇɴᴛ ᴘʀᴇᴍɪᴜᴍ)</blockquote>"""

    parts = message.command[1:]
    if not parts:
        return await message.reply_text(usage)

    try:
        user_id_to_add = int(parts[0])
    except ValueError:
        return await message.reply_text("<blockquote>✗ ɪɴᴠᴀʟɪᴅ ᴜsᴇʀ ɪᴅ. ᴘʟᴇᴀsᴇ ᴄʜᴇᴄᴋ ᴀɢᴀɪɴ!</blockquote>")

    try:
        user = await client.get_users(user_id_to_add)
        user_name = user.first_name + (" " + user.last_name if user.last_name else "")
    except Exception as e:
        return await message.reply_text(f"<blockquote>✗ ᴇʀʀᴏʀ ꜰᴇᴛᴄʜɪɴɢ ᴜsᴇʀ ɪɴꜰᴏʀᴍᴀᴛɪᴏɴ:</blockquote> `{e}`")

    # Parse duration if provided
    duration_str = " ".join(parts[1:]) if len(parts) > 1 else None
    expiry_date = None
    duration_text = "permanently"

    if duration_str:
        duration = parse_duration(duration_str)
        if not duration:
            return await message.reply_text(f"<blockquote>✗ ɪɴᴠᴀʟɪᴅ ᴅᴜʀᴀᴛɪᴏɴ ꜰᴏʀᴍᴀᴛ.</blockquote>\n{usage}")
        expiry_date = datetime.now() + duration
        duration_text = f"until {expiry_date.strftime('%Y-%m-%d %H:%M:%S')}"

    if not await client.mongodb.is_pro(user_id_to_add):
        await client.mongodb.add_pro(user_id_to_add, expiry_date)
        await message.reply_text(f"<blockquote>✓ <b>{user_name}</b> (`{user_id_to_add}`) ɪs ɴᴏᴡ ᴀ ᴘʀᴏ ᴜsᴇʀ {duration_text}!</blockquote>")
        try:
            notify_msg = "<blockquote>✦ <b>ᴄᴏɴɢʀᴀᴛᴜʟᴀᴛɪᴏɴs! ʏᴏᴜʀ ᴘʀᴇᴍɪᴜᴍ ᴍᴇᴍʙᴇʀsʜɪᴘ ʜᴀs ʙᴇᴇɴ ᴀᴄᴛɪᴠᴀᴛᴇᴅ"
            notify_msg += f" ᴜɴᴛɪʟ {expiry_date.strftime('%Y-%m-%d %H:%M:%S')}</b></blockquote>" if expiry_date else " ᴘᴇʀᴍᴀɴᴇɴᴛʟʏ</b></blockquote>"
            await client.send_message(user_id_to_add, notify_msg)
        except Exception as e:
            await message.reply_text(f"<blockquote>✗ ꜰᴀɪʟᴇᴅ ᴛᴏ ɴᴏᴛɪꜰʏ ᴛʜᴇ ᴜsᴇʀ:</blockquote> `{e}`")
    else:
        current_expiry = await client.mongodb.get_expiry_date(user_id_to_add)
        if current_expiry:
            await message.reply_text(
                f"<blockquote>›› <b>{user_name}</b> (`{user_id_to_add}`) ɪs ᴀʟʀᴇᴀᴅʏ ᴀ ᴘʀᴏ ᴜsᴇʀ "
                f"ᴜɴᴛɪʟ {current_expiry.strftime('%Y-%m-%d %H:%M:%S')}.</blockquote>"
            )
        else:
            await message.reply_text(f"<blockquote>›› <b>{user_name}</b> (`{user_id_to_add}`) ɪs ᴀʟʀᴇᴀᴅʏ ᴀ ᴘᴇʀᴍᴀɴᴇɴᴛ ᴘʀᴏ ᴜsᴇʀ.</blockquote>")

#========================================================================#

@Client.on_message(filters.command('delpremium') & filters.private)
async def remove_admin_command(client: Client, message: Message):
    if message.from_user.id != OWNER_ID:
        return await message.reply_text("<blockquote>✗ ᴏɴʟʏ ᴛʜᴇ ᴏᴡɴᴇʀ ᴄᴀɴ ᴜsᴇ ᴛʜɪs ᴄᴏᴍᴍᴀɴᴅ!</blockquote>")

    if len(message.command) != 2:
        return await message.reply_text("<blockquote>✗ ᴡʀᴏɴɢ ꜰᴏʀᴍᴀᴛ! ᴜsᴇ:</blockquote> /delpremium userid")

    try:
        user_id_to_remove = int(message.command[1])
    except ValueError:
        return await message.reply_text("<blockquote>✗ ɪɴᴠᴀʟɪᴅ ᴜsᴇʀ ɪᴅ. ᴘʟᴇᴀsᴇ ᴄʜᴇᴄᴋ ᴀɢᴀɪɴ!</blockquote>")

    try:
        user = await client.get_users(user_id_to_remove)
        user_name = user.first_name + (" " + user.last_name if user.last_name else "")
    except Exception as e:
        return await message.reply_text(f"<blockquote>✗ ᴇʀʀᴏʀ ꜰᴇᴛᴄʜɪɴɢ ᴜsᴇʀ ɪɴꜰᴏʀᴍᴀᴛɪᴏɴ:</blockquote> `{e}`")

    if await client.mongodb.is_pro(user_id_to_remove):
        await client.mongodb.remove_pro(user_id_to_remove)
        await message.reply_text(f"<blockquote>✓ <b>{user_name}</b> (`{user_id_to_remove}`) ʜᴀs ʙᴇᴇɴ ʀᴇᴍᴏᴠᴇᴅ ꜰʀᴏᴍ ᴘʀᴏ ᴜsᴇʀs.</blockquote>")
        try:
            await client.send_message(user_id_to_remove, "<blockquote>✗ ʏᴏᴜʀ ᴍᴇᴍʙᴇʀsʜɪᴘ ʜᴀs ᴇɴᴅᴇᴅ.</blockquote>\nᴛᴏ ʀᴇɴᴇᴡ, ᴄᴏɴᴛᴀᴄᴛ: @ITSANIMEN.")
        except Exception as e:
            await message.reply_text(f"<blockquote>✗ ꜰᴀɪʟᴇᴅ ᴛᴏ ɴᴏᴛɪꜰʏ ᴛʜᴇ ᴜsᴇʀ:</blockquote> `{e}`")
    else:
        await message.reply_text(f"<blockquote>›› <b>{user_name}</b> (`{user_id_to_remove}`) ɪs ɴᴏᴛ ᴀ ᴘʀᴏ ᴜsᴇʀ ᴏʀ ᴡᴀs ɴᴏᴛ ꜰᴏᴜɴᴅ.</blockquote>")

#========================================================================#


@Client.on_message(filters.command('premiumusers') & filters.private)
async def admin_list_command(client: Client, message: Message):
    if message.from_user.id != OWNER_ID:
        return await message.reply_text("<blockquote>✗ ᴏɴʟʏ ᴛʜᴇ ᴏᴡɴᴇʀ ᴄᴀɴ ᴜsᴇ ᴛʜɪs ᴄᴏᴍᴍᴀɴᴅ!</blockquote>")

    pro_user_ids = await client.mongodb.get_pros_list()
    formatted_admins = []

    for user_id in pro_user_ids:
        try:
            user = await client.get_users(user_id)
            full_name = user.first_name + (" " + user.last_name if user.last_name else "")
            username = f"@{user.username}" if user.username else "ɴᴏ ᴜsᴇʀɴᴀᴍᴇ"
            expiry_date = await client.mongodb.get_expiry_date(user_id)
            status = f"(ᴇxᴘɪʀᴇs: {expiry_date.strftime('%Y-%m-%d %H:%M:%S')})" if expiry_date else "(ᴘᴇʀᴍᴀɴᴇɴᴛ)"
            formatted_admins.append(f"{full_name} - {username} {status}")
        except Exception:
            continue

    if formatted_admins:
        await message.reply_text(
            "<blockquote>✦ <b>ᴘʀᴇᴍɪᴜᴍ ᴜsᴇʀs ʟɪsᴛ:</b></blockquote>\n\n" + "\n".join(formatted_admins),
            disable_web_page_preview=True
        )
    else:
        await message.reply_text("<blockquote>›› ɴᴏ ᴘʀᴇᴍɪᴜᴍ ᴜsᴇʀs ꜰᴏᴜɴᴅ.</blockquote>")
