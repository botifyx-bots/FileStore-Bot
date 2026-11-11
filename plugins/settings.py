from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors.pyromod import ListenerTimeout
from config import OWNER_ID
from helper.helper_func import parse_button_input, build_custom_buttons_markup
from plugins.others import home
import humanize

#===============================================================#

@Client.on_callback_query(filters.regex("^settings$"))
async def settings(client, query):
    # Count active force subscription channels by type
    total_fsub = len(client.fsub_dict)
    request_enabled = sum(1 for data in client.fsub_dict.values() if data[2])
    timer_enabled = sum(1 for data in client.fsub_dict.values() if data[3] > 0)
    
    # Count DB channels
    total_db_channels = len(getattr(client, 'db_channels', {}))
    primary_db = getattr(client, 'primary_db_channel', client.db)
    
    msg = f"""<blockquote>✦ sᴇᴛᴛɪɴɢs ᴏғ @{client.username}</blockquote>
›› **ꜰꜱᴜʙ ᴄʜᴀɴɴᴇʟs:** `{total_fsub}` (ʀᴇǫᴜᴇsᴛ: {request_enabled}, ᴛɪᴍᴇʀ: {timer_enabled})
›› **ᴅʙ ᴄʜᴀɴɴᴇʟs:** `{total_db_channels}` (ᴘʀɪᴍᴀʀʏ: `{primary_db}`)
›› **ᴀᴜᴛᴏ ᴅᴇʟᴇᴛᴇ ᴛɪᴍᴇʀ:** `{client.auto_del}`
›› **ᴘʀᴏᴛᴇᴄᴛ ᴄᴏɴᴛᴇɴᴛ:** `{"✓ ᴛʀᴜᴇ" if client.protect else "✗ ꜰᴀʟsᴇ"}`
›› **ᴅɪsᴀʙʟᴇ ʙᴜᴛᴛᴏɴ:** `{"✓ ᴛʀᴜᴇ" if client.disable_btn else "✗ ꜰᴀʟsᴇ"}`
›› **ʀᴇᴘʟʏ ᴛᴇxᴛ:** `{client.reply_text if client.reply_text else 'ɴᴏɴᴇ'}`
›› **ᴀᴅᴍɪɴs:** `{len(client.admins)}`
›› **sʜᴏʀᴛɴᴇʀ ᴜʀʟ:** `{getattr(client, 'short_url', 'ɴᴏᴛ sᴇᴛ')}`
›› **ᴛᴜᴛᴏʀɪᴀʟ ʟɪɴᴋ:** `{getattr(client, 'tutorial_link', 'ɴᴏᴛ sᴇᴛ')}`
›› **sᴛᴀʀᴛ ᴍᴇssᴀɢᴇ:**
<pre>{client.messages.get('START', 'ᴇᴍᴘᴛʏ')}</pre>
›› **sᴛᴀʀᴛ ɪᴍᴀɢᴇ:** `{bool(client.messages.get('START_PHOTO', ''))}`
›› **ꜰᴏʀᴄᴇ sᴜʙ ᴍᴇssᴀɢᴇ:**
<pre>{client.messages.get('FSUB', 'ᴇᴍᴘᴛʏ')}</pre>
›› **ꜰᴏʀᴄᴇ sᴜʙ ɪᴍᴀɢᴇ:** `{bool(client.messages.get('FSUB_PHOTO', ''))}`
›› **ᴀʙᴏᴜᴛ ᴍᴇssᴀɢᴇ:**
<pre>{client.messages.get('ABOUT', 'ᴇᴍᴘᴛʏ')}</pre>
›› **ʀᴇᴘʟʏ ᴍᴇssᴀɢᴇ:**
<pre>{client.reply_text}</pre>
    """
    reply_markup = InlineKeyboardMarkup([
        [InlineKeyboardButton('ꜰꜱᴜʙ ᴄʜᴀɴɴᴇʟꜱ', 'fsub'), InlineKeyboardButton('ᴅʙ ᴄʜᴀɴɴᴇʟꜱ', 'db_channels')],
        [InlineKeyboardButton('ᴀᴅᴍɪɴꜱ', 'admins'), InlineKeyboardButton('ᴀᴜᴛᴏ ᴅᴇʟᴇᴛᴇ', 'auto_del')],
        [InlineKeyboardButton('ʜᴏᴍᴇ', 'home'), InlineKeyboardButton('›› ɴᴇxᴛ', 'settings_page_2')]
    ])
    await query.message.edit_text(msg, reply_markup=reply_markup)
    return

#===============================================================#

@Client.on_callback_query(filters.regex("^settings_page_2$"))
async def settings_page_2(client, query):
    # Count active force subscription channels by type
    total_fsub = len(client.fsub_dict)
    request_enabled = sum(1 for data in client.fsub_dict.values() if data[2])
    timer_enabled = sum(1 for data in client.fsub_dict.values() if data[3] > 0)
    
    # Count DB channels
    total_db_channels = len(getattr(client, 'db_channels', {}))
    primary_db = getattr(client, 'primary_db_channel', client.db)
    
    msg = f"""<blockquote>✦ sᴇᴛᴛɪɴɢs ᴏғ @{client.username}</blockquote>
›› **ꜰsᴜʙ ᴄʜᴀɴɴᴇʟs:** `{total_fsub}` (ʀᴇǫᴜᴇsᴛ: {request_enabled}, ᴛɪᴍᴇʀ: {timer_enabled})
›› **ᴅʙ ᴄʜᴀɴɴᴇʟs:** `{total_db_channels}` (ᴘʀɪᴍᴀʀʏ: `{primary_db}`)
›› **ᴀᴜᴛᴏ ᴅᴇʟᴇᴛᴇ ᴛɪᴍᴇʀ:** `{client.auto_del}`
›› **ᴘʀᴏᴛᴇᴄᴛ ᴄᴏɴᴛᴇɴᴛ:** `{"✓ ᴛʀᴜᴇ" if client.protect else "✗ ꜰᴀʟsᴇ"}`
›› **ᴅɪsᴀʙʟᴇ ʙᴜᴛᴛᴏɴ:** `{"✓ ᴛʀᴜᴇ" if client.disable_btn else "✗ ꜰᴀʟsᴇ"}`
›› **ʀᴇᴘʟʏ ᴛᴇxᴛ:** `{client.reply_text if client.reply_text else 'ɴᴏɴᴇ'}`
›› **ᴀᴅᴍɪɴs:** `{len(client.admins)}`
›› **sʜᴏʀᴛɴᴇʀ ᴜʀʟ:** `{getattr(client, 'short_url', 'ɴᴏᴛ sᴇᴛ')}`
›› **ᴛᴜᴛᴏʀɪᴀʟ ʟɪɴᴋ:** `{getattr(client, 'tutorial_link', 'ɴᴏᴛ sᴇᴛ')}`
›› **sᴛᴀʀᴛ ᴍᴇssᴀɢᴇ:**
<pre>{client.messages.get('START', 'ᴇᴍᴘᴛʏ')}</pre>
›› **sᴛᴀʀᴛ ɪᴍᴀɢᴇ:** `{bool(client.messages.get('START_PHOTO', ''))}`
›› **ꜰᴏʀᴄᴇ sᴜʙ ᴍᴇssᴀɢᴇ:**
<pre>{client.messages.get('FSUB', 'ᴇᴍᴘᴛʏ')}</pre>
›› **ꜰᴏʀᴄᴇ sᴜʙ ɪᴍᴀɢᴇ:** `{bool(client.messages.get('FSUB_PHOTO', ''))}`
›› **ᴀʙᴏᴜᴛ ᴍᴇssᴀɢᴇ:**
<pre>{client.messages.get('ABOUT', 'ᴇᴍᴘᴛʏ')}</pre>
›› **ʀᴇᴘʟʏ ᴍᴇssᴀɢᴇ:**
<pre>{client.reply_text}</pre>
    """
    reply_markup = InlineKeyboardMarkup([
        [InlineKeyboardButton('ᴘʀᴏᴛᴇᴄᴛ ᴄᴏɴᴛᴇɴᴛ', 'protect'), InlineKeyboardButton('ᴘʜᴏᴛᴏs', 'photos')],
        [InlineKeyboardButton('ᴛᴇxᴛs', 'texts'), InlineKeyboardButton('sʜᴏʀᴛɴᴇʀ', 'shortner')],
        [InlineKeyboardButton('🪙 ᴛᴏᴋᴇɴs / ᴄʀᴇᴅɪᴛs', 'tokensettings'), InlineKeyboardButton('✎ ᴄᴜsᴛᴏᴍ ʙᴜᴛᴛᴏɴs', 'custom_buttons')],
        [InlineKeyboardButton('‹ ᴘʀᴇᴠ', 'settings'), InlineKeyboardButton('ʜᴏᴍᴇ', 'home')]
    ])
    await query.message.edit_text(msg, reply_markup=reply_markup)
    return

#===============================================================#

@Client.on_callback_query(filters.regex("^fsub$"))
async def fsub(client, query):
    # Create a formatted list of channels with names and IDs
    if client.fsub_dict:
        channel_list = []
        for channel_id, channel_data in client.fsub_dict.items():
            channel_name = channel_data[0] if channel_data and len(channel_data) > 0 else "ᴜɴᴋɴᴏᴡɴ"
            request_status = "✓ ʀᴇǫᴜᴇsᴛ" if channel_data[2] else "✗ ʀᴇǫᴜᴇsᴛ"
            timer_status = f"ᴛɪᴍᴇʀ: {channel_data[3]}ᴍ" if channel_data[3] > 0 else "ᴛɪᴍᴇʀ: ∞"
            channel_list.append(f"• `{channel_name}` (`{channel_id}`) - {request_status}, {timer_status}")
        
        channels_display = "\n".join(channel_list)
    else:
        channels_display = "_ɴᴏ ꜰᴏʀᴄᴇ sᴜʙsᴄʀɪᴘᴛɪᴏɴ ᴄʜᴀɴɴᴇʟs ᴄᴏɴғɪɢᴜʀᴇᴅ_"
    
    msg = f"""<blockquote>✦ ꜰᴏʀᴄᴇ sᴜʙsᴄʀɪᴘᴛɪᴏɴ sᴇᴛᴛɪɴɢs</blockquote>
›› **ᴄᴏɴғɪɢᴜʀᴇᴅ ᴄʜᴀɴɴᴇʟs:**
{channels_display}

__ᴜsᴇ ᴛʜᴇ ᴀᴘᴘʀᴏᴘʀɪᴀᴛᴇ ʙᴜᴛᴛᴏɴ ʙᴇʟᴏᴡ ᴛᴏ ᴀᴅᴅ ᴏʀ ʀᴇᴍᴏᴠᴇ ᴀ ꜰᴏʀᴄᴇ sᴜʙsᴄʀɪᴘᴛɪᴏɴ ᴄʜᴀɴɴᴇʟ ʙᴀsᴇᴅ ᴏɴ ʏᴏᴜʀ ɴᴇᴇᴅs!__
"""
    reply_markup = InlineKeyboardMarkup([
        [InlineKeyboardButton('›› ᴀᴅᴅ ᴄʜᴀɴɴᴇʟ', 'add_fsub'), InlineKeyboardButton('›› ʀᴇᴍᴏᴠᴇ ᴄʜᴀɴɴᴇʟ', 'rm_fsub')],
        [InlineKeyboardButton('‹ ʙᴀᴄᴋ', 'settings')]]
    )
    await query.message.edit_text(msg, reply_markup=reply_markup)
    return

#===============================================================#

@Client.on_callback_query(filters.regex("^db_channels$"))
async def db_channels(client, query):
    if not query.from_user.id in client.admins:
        return await query.answer('✗ ᴏɴʟʏ ᴀᴅᴍɪɴs ᴄᴀɴ ᴜsᴇ ᴛʜɪs!', show_alert=True)
    
    # Create a formatted list of DB channels
    db_channels = getattr(client, 'db_channels', {})
    if db_channels:
        channel_list = []
        for channel_id_str, channel_data in db_channels.items():
            channel_name = channel_data.get('name', 'ᴜɴᴋɴᴏᴡɴ')
            is_primary = "✓ ᴘʀɪᴍᴀʀʏ" if channel_data.get('is_primary', False) else "• sᴇᴄᴏɴᴅᴀʀʏ"
            is_active = "✓ ᴀᴄᴛɪᴠᴇ" if channel_data.get('is_active', True) else "✗ ɪɴᴀᴄᴛɪᴠᴇ"
            channel_list.append(f"• `{channel_name}` (`{channel_id_str}`)\n  {is_primary} | {is_active}")
        
        channels_display = "\n\n".join(channel_list)
    else:
        channels_display = "_ɴᴏ ᴅᴀᴛᴀʙᴀsᴇ ᴄʜᴀɴɴᴇʟs ᴄᴏɴғɪɢᴜʀᴇᴅ_"
    
    # Show current primary DB channel
    primary_db = getattr(client, 'primary_db_channel', client.db)
    
    msg = f"""<blockquote>✦ ᴅᴀᴛᴀʙᴀsᴇ ᴄʜᴀɴɴᴇʟs sᴇᴛᴛɪɴɢs</blockquote>
›› **ᴄᴜʀʀᴇɴᴛ ᴘʀɪᴍᴀʀʏ ᴅʙ:** `{primary_db}`
›› **ᴛᴏᴛᴀʟ ᴅʙ ᴄʜᴀɴɴᴇʟs:** `{len(db_channels)}`

**ᴄᴏɴғɪɢᴜʀᴇᴅ ᴄʜᴀɴɴᴇʟs:**
{channels_display}

__ᴜsᴇ ᴛʜᴇ ᴀᴘᴘʀᴏᴘʀɪᴀᴛᴇ ʙᴜᴛᴛᴏɴ ʙᴇʟᴏᴡ ᴛᴏ ᴍᴀɴᴀɢᴇ ʏᴏᴜʀ ᴅᴀᴛᴀʙᴀsᴇ ᴄʜᴀɴɴᴇʟs!__
"""
    reply_markup = InlineKeyboardMarkup([
        [InlineKeyboardButton('›› ᴀᴅᴅ ᴅʙ ᴄʜᴀɴɴᴇʟ', 'add_db_channel'), InlineKeyboardButton('›› ʀᴇᴍᴏᴠᴇ ᴅʙ ᴄʜᴀɴɴᴇʟ', 'rm_db_channel')],
        [InlineKeyboardButton('›› sᴇᴛ ᴘʀɪᴍᴀʀʏ', 'set_primary_db'), InlineKeyboardButton('›› sᴛᴀᴛᴜs', 'toggle_db_status')],
        [InlineKeyboardButton('‹ ʙᴀᴄᴋ', 'settings')]
    ])
    await query.message.edit_text(msg, reply_markup=reply_markup)
    return

#===============================================================#

@Client.on_callback_query(filters.regex("^add_db_channel$"))
async def add_db_channel(client, query):
    if not query.from_user.id in client.admins:
        return await query.answer('✗ ᴏɴʟʏ ᴀᴅᴍɪɴs ᴄᴀɴ ᴜsᴇ ᴛʜɪs!', show_alert=True)
    
    await query.answer()
    msg = f"""<blockquote>✦ ᴀᴅᴅ ɴᴇᴡ ᴅᴀᴛᴀʙᴀsᴇ ᴄʜᴀɴɴᴇʟ</blockquote>
›› **ᴄᴜʀʀᴇɴᴛ ᴅʙ ᴄʜᴀɴɴᴇʟs:** `{len(getattr(client, 'db_channels', {}))}`

__sᴇɴᴅ ᴛʜᴇ ᴄʜᴀɴɴᴇʟ ɪᴅ (ɴᴇɢᴀᴛɪᴠᴇ ɪɴᴛᴇɢᴇʀ ᴠᴀʟᴜᴇ) ᴏғ ᴛʜᴇ ᴅᴀᴛᴀʙᴀsᴇ ᴄʜᴀɴɴᴇʟ ʏᴏᴜ ᴡᴀɴᴛ ᴛᴏ ᴀᴅᴅ ɪɴ ᴛʜᴇ ɴᴇxᴛ 60 sᴇᴄᴏɴᴅs!__

**ᴇxᴀᴍᴘʟᴇ:** `-1001234567675`
**ɴᴏᴛᴇ:** ᴍᴀᴋᴇ sᴜʀᴇ ᴛʜᴇ ʙᴏᴛ ɪs ᴀᴅᴍɪɴ ɪɴ ᴛʜᴇ ᴄʜᴀɴɴᴇʟ!"""
    
    await query.message.edit_text(msg)
    try:
        res = await client.listen(user_id=query.from_user.id, filters=filters.text, timeout=60)
        channel_id_text = res.text.strip()
        
        if not channel_id_text.lstrip('-').isdigit():
            return await query.message.edit_text("**✗ ɪɴᴠᴀʟɪᴅ ᴄʜᴀɴɴᴇʟ ɪᴅ! ᴘʟᴇᴀsᴇ sᴇɴᴅ ᴀ ᴠᴀʟɪᴅ ɴᴇɢᴀᴛɪᴠᴇ ɪɴᴛᴇɢᴇʀ.**", 
                                                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton('‹ ʙᴀᴄᴋ', 'db_channels')]]))
        
        channel_id = int(channel_id_text)
        
        # Check if channel already exists
        db_channels = getattr(client, 'db_channels', {})
        if str(channel_id) in db_channels:
            return await query.message.edit_text(f"**✗ ᴄʜᴀɴɴᴇʟ `{channel_id}` ɪs ᴀʟʀᴇᴀᴅʏ ᴀᴅᴅᴇᴅ ᴀs ᴀ ᴅʙ ᴄʜᴀɴɴᴇʟ!**", 
                                                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton('‹ ʙᴀᴄᴋ', 'db_channels')]]))
        
        # Verify bot can access the channel
        try:
            chat = await client.get_chat(channel_id)
            test_msg = await client.send_message(chat_id=channel_id, text="ᴛᴇsᴛɪɴɢ ᴅʙ ᴄʜᴀɴɴᴇʟ ᴀᴄᴄᴇss - @Okabe_xRintarou")
            await test_msg.delete()
            
            # Add channel to database
            channel_data = {
                'name': chat.title,
                'is_primary': len(db_channels) == 0,  # First channel becomes primary
                'is_active': True,
                'added_by': query.from_user.id
            }
            
            await client.mongodb.add_db_channel(channel_id, channel_data)
            
            # Update client attributes
            if not hasattr(client, 'db_channels'):
                client.db_channels = {}
            client.db_channels[str(channel_id)] = channel_data
            
            # Set as primary if it's the first channel
            if channel_data['is_primary']:
                client.primary_db_channel = channel_id
                await client.mongodb.set_primary_db_channel(channel_id)
            
            await query.message.edit_text(f"""**✓ ᴅᴀᴛᴀʙᴀsᴇ ᴄʜᴀɴɴᴇʟ ᴀᴅᴅᴇᴅ sᴜᴄᴄᴇssғᴜʟʟʏ!**

›› **ᴄʜᴀɴɴᴇʟ:** `{chat.title}`
›› **ɪᴅ:** `{channel_id}`
›› **sᴛᴀᴛᴜs:** {'ᴘʀɪᴍᴀʀʏ' if channel_data['is_primary'] else 'sᴇᴄᴏɴᴅᴀʀʏ'}""", 
                                        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton('‹ ʙᴀᴄᴋ', 'db_channels')]]))
        
        except Exception as e:
            await query.message.edit_text(f"""**✗ ᴇʀʀᴏʀ ᴀᴄᴄᴇssɪɴɢ ᴄʜᴀɴɴᴇʟ!**

›› **ᴇʀʀᴏʀ:** `{str(e)}`

**ᴘʟᴇᴀsᴇ ᴍᴀᴋᴇ sᴜʀᴇ:**
• ʙᴏᴛ ɪs ᴀᴅᴍɪɴ ɪɴ ᴛʜᴇ ᴄʜᴀɴɴᴇʟ
• ᴄʜᴀɴɴᴇʟ ɪᴅ ɪs ᴄᴏʀʀᴇᴄᴛ
• ᴄʜᴀɴɴᴇʟ ᴇxɪsᴛs""", 
                                        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton('‹ ʙᴀᴄᴋ', 'db_channels')]]))
    
    except Exception as e:
        await query.message.edit_text(f"""**✗ ᴛɪᴍᴇᴏᴜᴛ ᴏʀ ᴇʀʀᴏʀ ᴏᴄᴄᴜʀʀᴇᴅ!**

›› **ᴇʀʀᴏʀ:** `{str(e)}`""", 
                                    reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton('‹ ʙᴀᴄᴋ', 'db_channels')]]))

#===============================================================#

@Client.on_callback_query(filters.regex("^rm_db_channel$"))
async def rm_db_channel(client, query):
    if not query.from_user.id in client.admins:
        return await query.answer('✗ ᴏɴʟʏ ᴀᴅᴍɪɴs ᴄᴀɴ ᴜsᴇ ᴛʜɪs!', show_alert=True)
    
    await query.answer()
    db_channels = getattr(client, 'db_channels', {})
    
    if not db_channels:
        return await query.message.edit_text("<blockquote>✗ ɴᴏ ᴅᴀᴛᴀʙᴀsᴇ ᴄʜᴀɴɴᴇʟs ᴛᴏ ʀᴇᴍᴏᴠᴇ!</blockquote>", 
                                            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton('◂ ʙᴀᴄᴋ', 'db_channels')]]))
    
    msg = f"""<blockquote>✦ ʀᴇᴍᴏᴠᴇ ᴅᴀᴛᴀʙᴀsᴇ ᴄʜᴀɴɴᴇʟ</blockquote>
<blockquote>›› <b>ᴀᴠᴀɪʟᴀʙʟᴇ ᴄʜᴀɴɴᴇʟs:</b>
"""
    
    for channel_id_str, channel_data in db_channels.items():
        channel_name = channel_data.get('name', 'ᴜɴᴋɴᴏᴡɴ')
        is_primary = " (ᴘʀɪᴍᴀʀʏ)" if channel_data.get('is_primary', False) else ""
        msg += f"• `{channel_name}` - `{channel_id_str}`{is_primary}\n"
    msg += "</blockquote>"
    
    msg += "\n__sᴇɴᴅ ᴛʜᴇ ᴄʜᴀɴɴᴇʟ ɪᴅ ʏᴏᴜ ᴡᴀɴᴛ ᴛᴏ ʀᴇᴍᴏᴠᴇ ɪɴ ᴛʜᴇ ɴᴇxᴛ 60 sᴇᴄᴏɴᴅs!__"
    
    await query.message.edit_text(msg)
    try:
        res = await client.listen(user_id=query.from_user.id, filters=filters.text, timeout=60)
        channel_id_text = res.text.strip()
        
        if not channel_id_text.lstrip('-').isdigit():
            return await query.message.edit_text("<blockquote>✗ ɪɴᴠᴀʟɪᴅ ᴄʜᴀɴɴᴇʟ ɪᴅ!</blockquote>", 
                                                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton('◂ ʙᴀᴄᴋ', 'db_channels')]]))
        
        channel_id = int(channel_id_text)
        
        if str(channel_id) not in db_channels:
            return await query.message.edit_text(f"<blockquote>✗ ᴄʜᴀɴɴᴇʟ `{channel_id}` ɪs ɴᴏᴛ ɪɴ ᴛʜᴇ ᴅʙ ᴄʜᴀɴɴᴇʟs ʟɪsᴛ!</blockquote>", 
                                                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton('◂ ʙᴀᴄᴋ', 'db_channels')]]))
        
        # Check if trying to remove primary channel
        if db_channels[str(channel_id)].get('is_primary', False) and len(db_channels) > 1:
            return await query.message.edit_text("<blockquote>✗ ᴄᴀɴɴᴏᴛ ʀᴇᴍᴏᴠᴇ ᴘʀɪᴍᴀʀʏ ᴄʜᴀɴɴᴇʟ!</blockquote>\n\n__ᴘʟᴇᴀsᴇ sᴇᴛ ᴀɴᴏᴛʜᴇʀ ᴄʜᴀɴɴᴇʟ ᴀs ᴘʀɪᴍᴀʀʏ ꜰɪʀsᴛ.__", 
                                                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton('◂ ʙᴀᴄᴋ', 'db_channels')]]))
        
        # Remove from database and client
        channel_name = db_channels[str(channel_id)].get('name', 'ᴜɴᴋɴᴏᴡɴ')
        await client.mongodb.remove_db_channel(channel_id)
        del client.db_channels[str(channel_id)]
        
        await query.message.edit_text(f"<blockquote>✓ ᴅᴀᴛᴀʙᴀsᴇ ᴄʜᴀɴɴᴇʟ ʀᴇᴍᴏᴠᴇᴅ sᴜᴄᴄᴇssꜰᴜʟʟʏ!</blockquote>\n\n<b>ʀᴇᴍᴏᴠᴇᴅ:</b> `{channel_name}` (`{channel_id}`)", 
                                    reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton('◂ ʙᴀᴄᴋ', 'db_channels')]]))
    
    except Exception as e:
        await query.message.edit_text(f"<blockquote>✗ ᴛɪᴍᴇᴏᴜᴛ ᴏʀ ᴇʀʀᴏʀ ᴏᴄᴄᴜʀʀᴇᴅ!</blockquote>\n\n<b>ᴇʀʀᴏʀ:</b> `{str(e)}`", 
                                    reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton('◂ ʙᴀᴄᴋ', 'db_channels')]]))

#===============================================================#

@Client.on_callback_query(filters.regex("^set_primary_db$"))
async def set_primary_db(client, query):
    if not query.from_user.id in client.admins:
        return await query.answer('✗ ᴏɴʟʏ ᴀᴅᴍɪɴs ᴄᴀɴ ᴜsᴇ ᴛʜɪs!', show_alert=True)
    
    await query.answer()
    db_channels = getattr(client, 'db_channels', {})
    
    if not db_channels:
        return await query.message.edit_text("<blockquote>✗ ɴᴏ ᴅᴀᴛᴀʙᴀsᴇ ᴄʜᴀɴɴᴇʟs ᴀᴠᴀɪʟᴀʙʟᴇ!</blockquote>", 
                                            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton('◂ ʙᴀᴄᴋ', 'db_channels')]]))
    
    msg = f"""<blockquote>✦ sᴇᴛ ᴘʀɪᴍᴀʀʏ ᴅᴀᴛᴀʙᴀsᴇ ᴄʜᴀɴɴᴇʟ</blockquote>
<blockquote>›› <b>ᴀᴠᴀɪʟᴀʙʟᴇ ᴄʜᴀɴɴᴇʟs:</b>
"""
    
    for channel_id_str, channel_data in db_channels.items():
        channel_name = channel_data.get('name', 'ᴜɴᴋɴᴏᴡɴ')
        is_primary = " (ᴄᴜʀʀᴇɴᴛ ᴘʀɪᴍᴀʀʏ)" if channel_data.get('is_primary', False) else ""
        msg += f"• `{channel_name}` - `{channel_id_str}`{is_primary}\n"
    msg += "</blockquote>"
    
    msg += "\n__sᴇɴᴅ ᴛʜᴇ ᴄʜᴀɴɴᴇʟ ɪᴅ ʏᴏᴜ ᴡᴀɴᴛ ᴛᴏ sᴇᴛ ᴀs ᴘʀɪᴍᴀʀʏ ɪɴ ᴛʜᴇ ɴᴇxᴛ 60 sᴇᴄᴏɴᴅs!__"
    
    await query.message.edit_text(msg)
    try:
        res = await client.listen(user_id=query.from_user.id, filters=filters.text, timeout=60)
        channel_id_text = res.text.strip()
        
        if not channel_id_text.lstrip('-').isdigit():
            return await query.message.edit_text("<blockquote>✗ ɪɴᴠᴀʟɪᴅ ᴄʜᴀɴɴᴇʟ ɪᴅ!</blockquote>", 
                                                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton('◂ ʙᴀᴄᴋ', 'db_channels')]]))
        
        channel_id = int(channel_id_text)
        
        if str(channel_id) not in db_channels:
            return await query.message.edit_text(f"<blockquote>✗ ᴄʜᴀɴɴᴇʟ `{channel_id}` ɪs ɴᴏᴛ ɪɴ ᴛʜᴇ ᴅʙ ᴄʜᴀɴɴᴇʟs ʟɪsᴛ!</blockquote>", 
                                                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton('◂ ʙᴀᴄᴋ', 'db_channels')]]))
        
        # Set as primary
        await client.mongodb.set_primary_db_channel(channel_id)
        
        # Update client attributes
        for ch_id, ch_data in client.db_channels.items():
            ch_data['is_primary'] = (int(ch_id) == channel_id)
        
        client.primary_db_channel = channel_id
        client.db = channel_id  # Update current db reference
        
        channel_name = db_channels[str(channel_id)].get('name', 'ᴜɴᴋɴᴏᴡɴ')
        await query.message.edit_text(f"<blockquote>✓ ᴘʀɪᴍᴀʀʏ ᴅᴀᴛᴀʙᴀsᴇ ᴄʜᴀɴɴᴇʟ ᴜᴘᴅᴀᴛᴇᴅ!</blockquote>\n\n<b>ɴᴇᴡ ᴘʀɪᴍᴀʀʏ:</b> `{channel_name}` (`{channel_id}`)", 
                                    reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton('◂ ʙᴀᴄᴋ', 'db_channels')]]))
    
    except Exception as e:
        await query.message.edit_text(f"<blockquote>✗ ᴛɪᴍᴇᴏᴜᴛ ᴏʀ ᴇʀʀᴏʀ ᴏᴄᴄᴜʀʀᴇᴅ!</blockquote>\n\n<b>ᴇʀʀᴏʀ:</b> `{str(e)}`", 
                                    reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton('◂ ʙᴀᴄᴋ', 'db_channels')]]))

#===============================================================#

@Client.on_callback_query(filters.regex("^toggle_db_status$"))
async def toggle_db_status(client, query):
    if not query.from_user.id in client.admins:
        return await query.answer('✗ ᴏɴʟʏ ᴀᴅᴍɪɴs ᴄᴀɴ ᴜsᴇ ᴛʜɪs!', show_alert=True)
    
    await query.answer()
    db_channels = getattr(client, 'db_channels', {})
    
    if not db_channels:
        return await query.message.edit_text("<blockquote>✗ ɴᴏ ᴅᴀᴛᴀʙᴀsᴇ ᴄʜᴀɴɴᴇʟs ᴀᴠᴀɪʟᴀʙʟᴇ!</blockquote>", 
                                            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton('◂ ʙᴀᴄᴋ', 'db_channels')]]))
    
    msg = f"""<blockquote>✦ ᴛᴏɢɢʟᴇ ᴄʜᴀɴɴᴇʟ sᴛᴀᴛᴜs</blockquote>
<blockquote>›› <b>ᴀᴠᴀɪʟᴀʙʟᴇ ᴄʜᴀɴɴᴇʟs:</b>
"""
    
    for channel_id_str, channel_data in db_channels.items():
        channel_name = channel_data.get('name', 'ᴜɴᴋɴᴏᴡɴ')
        status = "✓ ᴀᴄᴛɪᴠᴇ" if channel_data.get('is_active', True) else "✗ ɪɴᴀᴄᴛɪᴠᴇ"
        msg += f"• `{channel_name}` - `{channel_id_str}` ({status})\n"
    msg += "</blockquote>"
    
    msg += "\n__sᴇɴᴅ ᴛʜᴇ ᴄʜᴀɴɴᴇʟ ɪᴅ ʏᴏᴜ ᴡᴀɴᴛ ᴛᴏ ᴛᴏɢɢʟᴇ ᴀᴄᴛɪᴠᴇ/ɪɴᴀᴄᴛɪᴠᴇ sᴛᴀᴛᴜs ꜰᴏʀ ɪɴ ᴛʜᴇ ɴᴇxᴛ 60 sᴇᴄᴏɴᴅs!__"
    
    await query.message.edit_text(msg)
    try:
        res = await client.listen(user_id=query.from_user.id, filters=filters.text, timeout=60)
        channel_id_text = res.text.strip()
        
        if not channel_id_text.lstrip('-').isdigit():
            return await query.message.edit_text("<blockquote>✗ ɪɴᴠᴀʟɪᴅ ᴄʜᴀɴɴᴇʟ ɪᴅ!</blockquote>", 
                                                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton('◂ ʙᴀᴄᴋ', 'db_channels')]]))
        
        channel_id = int(channel_id_text)
        
        if str(channel_id) not in db_channels:
            return await query.message.edit_text(f"<blockquote>✗ ᴄʜᴀɴɴᴇʟ `{channel_id}` ɪs ɴᴏᴛ ɪɴ ᴛʜᴇ ᴅʙ ᴄʜᴀɴɴᴇʟs ʟɪsᴛ!</blockquote>", 
                                                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton('◂ ʙᴀᴄᴋ', 'db_channels')]]))
        
        # Toggle status
        new_status = await client.mongodb.toggle_db_channel_status(channel_id)
        
        if new_status is not None:
            # Update client attributes
            client.db_channels[str(channel_id)]['is_active'] = new_status
            
            channel_name = db_channels[str(channel_id)].get('name', 'ᴜɴᴋɴᴏᴡɴ')
            status_text = "✓ ᴀᴄᴛɪᴠᴇ" if new_status else "✗ ɪɴᴀᴄᴛɪᴠᴇ"
            await query.message.edit_text(f"<blockquote>✓ ᴄʜᴀɴɴᴇʟ sᴛᴀᴛᴜs ᴜᴘᴅᴀᴛᴇᴅ!</blockquote>\n\n<b>ᴄʜᴀɴɴᴇʟ:</b> `{channel_name}` (`{channel_id}`)\n<b>ɴᴇᴡ sᴛᴀᴛᴜs:</b> {status_text}", 
                                        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton('◂ ʙᴀᴄᴋ', 'db_channels')]]))
        else:
            await query.message.edit_text("<blockquote>✗ ꜰᴀɪʟᴇᴅ ᴛᴏ ᴛᴏɢɢʟᴇ ᴄʜᴀɴɴᴇʟ sᴛᴀᴛᴜs!</blockquote>", 
                                        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton('◂ ʙᴀᴄᴋ', 'db_channels')]]))
    
    except Exception as e:
        await query.message.edit_text(f"<blockquote>✗ ᴛɪᴍᴇᴏᴜᴛ ᴏʀ ᴇʀʀᴏʀ ᴏᴄᴄᴜʀʀᴇᴅ!</blockquote>\n\n<b>ᴇʀʀᴏʀ:</b> `{str(e)}`", 
                                    reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton('◂ ʙᴀᴄᴋ', 'db_channels')]]))

#===============================================================#

@Client.on_callback_query(filters.regex("^admins$"))
async def admins(client, query):
    if not (query.from_user.id==OWNER_ID):
        return await query.answer('This can only be used by owner.')
    msg = f"""<blockquote>**Admin Settings:**</blockquote>
**Admin User IDs:** {", ".join(f"`{a}`" for a in client.admins)}

__Use the appropriate button below to add or remove an admin based on your needs!__
"""
    reply_markup = InlineKeyboardMarkup([
        [InlineKeyboardButton('ᴀᴅᴅ ᴀᴅᴍɪɴ', 'add_admin'), InlineKeyboardButton('ʀᴇᴍᴏᴠᴇ ᴀᴅᴍɪɴ', 'rm_admin')],
        [InlineKeyboardButton('◂ ʙᴀᴄᴋ', 'settings')]]
    )
    await query.message.edit_text(msg, reply_markup=reply_markup)
    return

#===============================================================#

@Client.on_callback_query(filters.regex("^photos$"))
async def photos(client, query):
    msg = f"""<blockquote>✦ <b>ᴘʜᴏᴛᴏ sᴇᴛᴛɪɴɢs</b></blockquote>
<blockquote>›› <b>sᴛᴀʀᴛ ᴘʜᴏᴛᴏ:</b> `{client.messages.get("START_PHOTO", "ɴᴏɴᴇ")}`
›› <b>ꜰᴏʀᴄᴇ sᴜʙ ᴘʜᴏᴛᴏ:</b> `{client.messages.get('FSUB_PHOTO', 'ɴᴏɴᴇ')}`</blockquote>

<blockquote>≡ ᴜsᴇ ᴛʜᴇ ᴀᴘᴘʀᴏᴘʀɪᴀᴛᴇ ʙᴜᴛᴛᴏɴ ʙᴇʟᴏᴡ ᴛᴏ sᴇᴛ, ᴄʜᴀɴɢᴇ ᴏʀ ʀᴇᴍᴏᴠᴇ ᴀ ᴘʜᴏᴛᴏ.</blockquote>"""
    reply_markup = InlineKeyboardMarkup([
    [
        InlineKeyboardButton(
            ('ꜱᴇᴛ' if client.messages.get("START_PHOTO", "") == "" else 'ᴄʜᴀɴɢᴇ') + '\nꜱᴛᴀʀᴛ ᴘʜᴏᴛᴏ', 
            callback_data='add_start_photo'
        ),
        InlineKeyboardButton(
            ('ꜱᴇᴛ' if client.messages.get("FSUB_PHOTO", "") == "" else 'ᴄʜᴀɴɢᴇ') + '\nꜰꜱᴜʙ ᴘʜᴏᴛᴏ', 
            callback_data='add_fsub_photo'
        )
    ],
    [
        InlineKeyboardButton('ʀᴇᴍᴏᴠᴇ\nꜱᴛᴀʀᴛ ᴘʜᴏᴛᴏ', callback_data='rm_start_photo'),
        InlineKeyboardButton('ʀᴇᴍᴏᴠᴇ\nꜰꜱᴜʙ ᴘʜᴏᴛᴏ', callback_data='rm_fsub_photo')
    ],
    [InlineKeyboardButton('◂ ʙᴀᴄᴋ', callback_data='settings')]

    ])
    await query.message.edit_text(msg, reply_markup=reply_markup)
    return

#===============================================================#

@Client.on_callback_query(filters.regex("^protect$"))
async def protect(client, query):
    client.protect = False if client.protect else True
    await client.mongodb.update_bot_setting("protect_content", client.protect)
    return await settings(client, query)

#===============================================================#

@Client.on_callback_query(filters.regex("^auto_del$"))
async def auto_del(client, query):
    msg = f"""<blockquote>✦ <b>ᴄʜᴀɴɢᴇ ᴀᴜᴛᴏ ᴅᴇʟᴇᴛᴇ ᴛɪᴍᴇ</b></blockquote>
<blockquote>›› <b>ᴄᴜʀʀᴇɴᴛ ᴛɪᴍᴇʀ:</b> `{client.auto_del}`</blockquote>

<blockquote>≡ ᴇɴᴛᴇʀ ᴀ ɴᴇᴡ ɪɴᴛᴇɢᴇʀ ᴠᴀʟᴜᴇ ꜰᴏʀ ᴛʜᴇ ᴀᴜᴛᴏ ᴅᴇʟᴇᴛᴇ ᴛɪᴍᴇʀ (sᴇᴄᴏɴᴅs). ᴋᴇᴇᴘ 0 ᴛᴏ ᴅɪsᴀʙʟᴇ ᴀᴜᴛᴏ ᴅᴇʟᴇᴛᴇ, ᴏʀ ᴡᴀɪᴛ ꜰᴏʀ ᴛʜᴇ 60 sᴇᴄᴏɴᴅ ᴛɪᴍᴇᴏᴜᴛ.</blockquote>"""
    await query.answer()
    await query.message.edit_text(msg)
    try:
        res = await client.listen(user_id=query.from_user.id, filters=filters.text, timeout=60)
        timer = res.text.strip()
        if timer.isdigit() or (timer.startswith('+' or '-') and timer[1:].isdigit()):
            timer = int(timer)
            if timer >= 0:
                client.auto_del = timer
                await client.mongodb.update_bot_setting("auto_delete_timer", timer)
                return await query.message.edit_text(f'<blockquote>✓ ᴀᴜᴛᴏ ᴅᴇʟᴇᴛᴇ ᴛɪᴍᴇʀ ᴄʜᴀɴɢᴇᴅ ᴛᴏ {timer} sᴇᴄᴏɴᴅs!</blockquote>', reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton('◂ ʙᴀᴄᴋ', 'settings')]]))
            else:
                return await query.message.edit_text("<blockquote>✗ ɴᴏ ᴄʜᴀɴɢᴇ ᴡᴀs ᴍᴀᴅᴇ ᴛᴏ ᴛʜᴇ ᴀᴜᴛᴏ ᴅᴇʟᴇᴛᴇ ᴛɪᴍᴇʀ.</blockquote>", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton('◂ ʙᴀᴄᴋ', 'settings')]]))
        else:
            return await query.message.edit_text("<blockquote>✗ ᴛʜᴀᴛ ɪs ɴᴏᴛ ᴀ ᴠᴀʟɪᴅ ɪɴᴛᴇɢᴇʀ ᴠᴀʟᴜᴇ.</blockquote>", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton('◂ ʙᴀᴄᴋ', 'settings')]]))
    except ListenerTimeout:
        return await query.message.edit_text("<blockquote>⏰ ᴛɪᴍᴇᴏᴜᴛ, ᴛʀʏ ᴀɢᴀɪɴ!</blockquote>", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton('◂ ʙᴀᴄᴋ', 'settings')]]))

#===============================================================#

#===============================================================#
# NOTE: the "texts" settings panel (callback_data="texts") is handled in
# plugins/texts.py — that file owns the ^texts$ callback and all of the
# individual start/fsub/about/channels/reply text-edit flows. A second,
# out-of-date copy used to live here too, which meant two handlers fired
# for the same button press; it's been removed to avoid the duplicate.
#===============================================================#

#===============================================================#

@Client.on_callback_query(filters.regex('^rm_start_photo$'))
async def rm_start_photo(client, query):
    client.messages['START_PHOTO'] = ''
    await client.mongodb.update_message_setting('START_PHOTO', '')
    await query.answer()
    await photos(client, query)

#===============================================================#

@Client.on_callback_query(filters.regex('^rm_fsub_photo$'))
async def rm_fsub_photo(client, query):
    client.messages['FSUB_PHOTO'] = ''
    await client.mongodb.update_message_setting('FSUB_PHOTO', '')
    await query.answer()
    await photos(client, query)

#===============================================================#

@Client.on_callback_query(filters.regex("^add_start_photo$"))
async def add_start_photo(client, query):
    msg = f"""<blockquote>✦ <b>ᴄʜᴀɴɢᴇ sᴛᴀʀᴛ ɪᴍᴀɢᴇ</b></blockquote>
<blockquote>›› <b>ᴄᴜʀʀᴇɴᴛ sᴛᴀʀᴛ ɪᴍᴀɢᴇ:</b> `{client.messages.get('START_PHOTO', '')}`</blockquote>

<blockquote>≡ ᴇɴᴛᴇʀ ᴀ ɴᴇᴡ ʟɪɴᴋ ᴏʀ sᴇɴᴅ ᴛʜᴇ ᴘʜᴏᴛᴏ, ᴏʀ ᴡᴀɪᴛ ꜰᴏʀ ᴛʜᴇ 60 sᴇᴄᴏɴᴅ ᴛɪᴍᴇᴏᴜᴛ.</blockquote>"""
    await query.answer()
    await query.message.edit_text(msg)
    try:
        res = await client.listen(user_id=query.from_user.id, filters=(filters.text|filters.photo), timeout=60)
        if res.text and res.text.startswith('https://' or 'http://'):
            client.messages['START_PHOTO'] = res.text
            await client.mongodb.update_message_setting('START_PHOTO', res.text)
            return await query.message.edit_text("<blockquote>✓ ᴛʜɪs ʟɪɴᴋ ʜᴀs ʙᴇᴇɴ sᴇᴛ ᴀs ᴛʜᴇ sᴛᴀʀᴛ ᴘʜᴏᴛᴏ!</blockquote>", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton('◂ ʙᴀᴄᴋ', 'photos')]]))
        elif res.photo:
            loc = await res.download()
            client.messages['START_PHOTO'] = loc
            await client.mongodb.update_message_setting('START_PHOTO', loc)
            return await query.message.edit_text("<blockquote>✓ ᴛʜɪs ɪᴍᴀɢᴇ ʜᴀs ʙᴇᴇɴ sᴇᴛ ᴀs ᴛʜᴇ sᴛᴀʀᴛ ᴘʜᴏᴛᴏ!</blockquote>", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton('◂ ʙᴀᴄᴋ', 'photos')]]))
        else:
            return await query.message.edit_text("<blockquote>✗ ɪɴᴠᴀʟɪᴅ ᴘʜᴏᴛᴏ ᴏʀ ʟɪɴᴋ ꜰᴏʀᴍᴀᴛ!\nʟɪɴᴋs ᴍᴜsᴛ sᴛᴀʀᴛ ᴡɪᴛʜ `http` ᴏʀ `https`.</blockquote>", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton('◂ ʙᴀᴄᴋ', 'photos')]]))
    except ListenerTimeout:
        return await query.message.edit_text("<blockquote>⏰ ᴛɪᴍᴇᴏᴜᴛ, ᴛʀʏ ᴀɢᴀɪɴ!</blockquote>", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton('◂ ʙᴀᴄᴋ', 'photos')]]))

#===============================================================#

@Client.on_callback_query(filters.regex("^add_fsub_photo$"))
async def add_fsub_photo(client, query):
    msg = f"""<blockquote>✦ <b>ᴄʜᴀɴɢᴇ ꜰᴏʀᴄᴇ sᴜʙ ɪᴍᴀɢᴇ</b></blockquote>
<blockquote>›› <b>ᴄᴜʀʀᴇɴᴛ ꜰᴏʀᴄᴇ sᴜʙ ɪᴍᴀɢᴇ:</b> `{client.messages.get('FSUB_PHOTO', '')}`</blockquote>

<blockquote>≡ ᴇɴᴛᴇʀ ᴀ ɴᴇᴡ ʟɪɴᴋ ᴏʀ sᴇɴᴅ ᴛʜᴇ ᴘʜᴏᴛᴏ, ᴏʀ ᴡᴀɪᴛ ꜰᴏʀ ᴛʜᴇ 60 sᴇᴄᴏɴᴅ ᴛɪᴍᴇᴏᴜᴛ.</blockquote>"""
    await query.answer()
    await query.message.edit_text(msg)
    try:
        res = await client.listen(user_id=query.from_user.id, filters=(filters.text|filters.photo), timeout=60)
        if res.text and res.text.startswith('https://' or 'http://'):
            client.messages['FSUB_PHOTO'] = res.text
            await client.mongodb.update_message_setting('FSUB_PHOTO', res.text)
            return await query.message.edit_text("<blockquote>✓ ᴛʜɪs ʟɪɴᴋ ʜᴀs ʙᴇᴇɴ sᴇᴛ ᴀs ᴛʜᴇ ꜰᴏʀᴄᴇ sᴜʙ ᴘʜᴏᴛᴏ!</blockquote>", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton('◂ ʙᴀᴄᴋ', 'photos')]]))
        elif res.photo:
            loc = await res.download()
            client.messages['FSUB_PHOTO'] = loc
            await client.mongodb.update_message_setting('FSUB_PHOTO', loc)
            return await query.message.edit_text("<blockquote>✓ ᴛʜɪs ɪᴍᴀɢᴇ ʜᴀs ʙᴇᴇɴ sᴇᴛ ᴀs ᴛʜᴇ ꜰᴏʀᴄᴇ sᴜʙ ᴘʜᴏᴛᴏ!</blockquote>", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton('◂ ʙᴀᴄᴋ', 'photos')]]))
        else:
            return await query.message.edit_text("<blockquote>✗ ɪɴᴠᴀʟɪᴅ ᴘʜᴏᴛᴏ ᴏʀ ʟɪɴᴋ ꜰᴏʀᴍᴀᴛ!\nʟɪɴᴋs ᴍᴜsᴛ sᴛᴀʀᴛ ᴡɪᴛʜ `http` ᴏʀ `https`.</blockquote>", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton('◂ ʙᴀᴄᴋ', 'photos')]]))
    except ListenerTimeout:
        return await query.message.edit_text("<blockquote>⏰ ᴛɪᴍᴇᴏᴜᴛ, ᴛʀʏ ᴀɢᴀɪɴ!</blockquote>", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton('◂ ʙᴀᴄᴋ', 'photos')]]))

#===============================================================#

@Client.on_callback_query(filters.regex("^show_cplan$"))
async def show_cplan_callback(client, query):

    text = (
        "<blockquote>✦ <b>𝗖𝗥𝗘𝗗𝗜𝗧 𝗕𝗔𝗦𝗘𝗗 𝗣𝗟𝗔𝗡𝗦</b></blockquote>\n"
        "━━━━━━━━━━━━━━━━━━━\n"
        "<blockquote>\n"
        "» 30 credits : ₹50\n"
        "» 60 credits : ₹110\n"
        "» 120 credits : ₹220\n"
        "» 240 credits : ₹480</blockquote>\n"
        "━━━━━━━━━━━━━━━━━━━\n"
        "<blockquote>✦ ᴄᴏɴᴛᴀᴄᴛ @ITSANIMEN ᴛᴏ ʙᴜʏ ᴄʀᴇᴅɪᴛs</blockquote>"
    )

    await query.message.edit_text(
        text,
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("• ᴄʟᴏꜱᴇ •", callback_data="close")]
        ])
    )
#===============================================================#
# Custom Buttons — bot-wide extra inline buttons appended under every
# file/post delivered via /genlink, /batch, /nbatch and /fbatch links.
#===============================================================#

def _preview_custom_buttons(rows) -> str:
    if not rows:
        return "ɴᴏɴᴇ sᴇᴛ"
    lines = []
    for row in rows:
        lines.append(" | ".join(f"{b['text']} → {b['url']}" for b in row))
    return "\n".join(lines)


@Client.on_callback_query(filters.regex("^custom_buttons$"))
async def custom_buttons_panel(client, query):
    if query.from_user.id not in client.admins:
        return await query.answer("✗ ᴏɴʟʏ ᴀᴅᴍɪɴs ᴄᴀɴ ᴜsᴇ ᴛʜɪs!", show_alert=True)
    await query.answer()
    await _render_custom_buttons_panel(client, query)


async def _render_custom_buttons_panel(client, query):
    rows = await client.mongodb.get_custom_buttons()
    msg = (
        "<blockquote>✎ ᴄᴜsᴛᴏᴍ ʙᴜᴛᴛᴏɴs</blockquote>\n"
        "<blockquote>ᴛʜᴇsᴇ ʙᴜᴛᴛᴏɴs ᴀʀᴇ ᴀᴜᴛᴏᴍᴀᴛɪᴄᴀʟʟʏ ᴀᴅᴅᴇᴅ ᴜɴᴅᴇʀ ᴇᴠᴇʀʏ ꜰɪʟᴇ sʜᴀʀᴇᴅ ᴛʜʀᴏᴜɢʜ ɢᴇɴʟɪɴᴋ, ʙᴀᴛᴄʜ ᴀɴᴅ ꜰʙᴀᴛᴄʜ ʟɪɴᴋs.</blockquote>\n\n"
        f"<blockquote>›› **ᴄᴜʀʀᴇɴᴛ ʙᴜᴛᴛᴏɴs:**\n{_preview_custom_buttons(rows)}</blockquote>"
    )
    buttons = [
        [InlineKeyboardButton('✎ sᴇᴛ ʙᴜᴛᴛᴏɴs', 'set_custom_buttons')],
    ]
    if rows:
        buttons.append([InlineKeyboardButton('🗑 ᴄʟᴇᴀʀ ʙᴜᴛᴛᴏɴs', 'clear_custom_buttons')])
    buttons.append([InlineKeyboardButton('◂ ʙᴀᴄᴋ', 'settings_page_2')])

    await query.message.edit_text(msg, reply_markup=InlineKeyboardMarkup(buttons))


@Client.on_callback_query(filters.regex("^set_custom_buttons$"))
async def set_custom_buttons(client, query):
    if query.from_user.id not in client.admins:
        return await query.answer("✗ ᴏɴʟʏ ᴀᴅᴍɪɴs ᴄᴀɴ ᴜsᴇ ᴛʜɪs!", show_alert=True)
    await query.answer()

    prompt = (
        "✎ sᴇɴᴅ ᴍᴇ ᴛʜᴇ ʙᴜᴛᴛᴏɴs :\n\n"
        "ꜰᴏʀᴍᴀᴛ :\n"
        "`Button text 1 - http://example.com/`\n"
        "`Button text 2 - http://example2.com/`\n\n"
        "ᴜsᴇ | ꜰᴏʀ ᴜᴘ ᴛᴏ 2 ʙᴜᴛᴛᴏɴs ᴘᴇʀ ʀᴏᴡ :\n"
        "`Btn 1 - http://x.com/ | Btn 2 - http://y.com/`\n\n"
        "<blockquote>sᴇɴᴅ **0** ᴛᴏ ᴄᴀɴᴄᴇʟ ᴀɴᴅ ɢᴏ ʙᴀᴄᴋ ᴛᴏ ʜᴏᴍᴇ. ᴀᴜᴛᴏ-ᴀʙᴏʀᴛs ɪɴ 2 ᴍɪɴᴜᴛᴇs ɪꜰ ɴᴏᴛʜɪɴɢ ɪs sᴇɴᴛ.</blockquote>"
    )
    await query.message.edit_text(prompt)

    while True:
        try:
            res = await client.listen(user_id=query.from_user.id, filters=filters.text, timeout=120)
        except ListenerTimeout:
            return await query.message.edit_text(
                "<blockquote>⏰ ᴛɪᴍᴇᴏᴜᴛ — ɴᴏ ʙᴜᴛᴛᴏɴs ʀᴇᴄᴇɪᴠᴇᴅ, ᴘʀᴏᴄᴇss ᴀʙᴏʀᴛᴇᴅ.</blockquote>",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton('◂ ʙᴀᴄᴋ', 'custom_buttons')]])
            )

        raw = res.text.strip()
        if raw == "0":
            return await home(client, query)

        rows = parse_button_input(raw)
        if not rows:
            await res.reply(
                "<blockquote>✗ ᴄᴏᴜʟᴅɴ'ᴛ ʀᴇᴀᴅ ᴀɴʏ ʙᴜᴛᴛᴏɴs ꜰʀᴏᴍ ᴛʜᴀᴛ. ꜰᴏʟʟᴏᴡ ᴛʜᴇ ꜰᴏʀᴍᴀᴛ ᴀʙᴏᴠᴇ ᴀɴᴅ sᴇɴᴅ ᴀɢᴀɪɴ, ᴏʀ sᴇɴᴅ **0** ᴛᴏ ᴄᴀɴᴄᴇʟ.</blockquote>",
                quote=True
            )
            continue  # give them another shot within remaining conversation

        await client.mongodb.set_custom_buttons(rows)
        preview_markup = build_custom_buttons_markup(rows)
        await res.reply(
            "<blockquote>✓ ᴄᴜsᴛᴏᴍ ʙᴜᴛᴛᴏɴs sᴀᴠᴇᴅ! ᴛʜᴇʏ'ʟʟ ɴᴏᴡ ᴀᴘᴘᴇᴀʀ ᴏɴ ᴇᴠᴇʀʏ ꜰɪʟᴇ sʜᴀʀᴇᴅ ᴛʜʀᴏᴜɢʜ ɢᴇɴʟɪɴᴋ/ʙᴀᴛᴄʜ/ꜰʙᴀᴛᴄʜ.</blockquote>",
            quote=True,
            reply_markup=preview_markup
        )
        return await res.reply(
            "<blockquote>◂ ʙᴀᴄᴋ ᴛᴏ sᴇᴛᴛɪɴɢs</blockquote>",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton('◂ ʙᴀᴄᴋ', 'custom_buttons')]])
        )


@Client.on_callback_query(filters.regex("^clear_custom_buttons$"))
async def clear_custom_buttons(client, query):
    if query.from_user.id not in client.admins:
        return await query.answer("✗ ᴏɴʟʏ ᴀᴅᴍɪɴs ᴄᴀɴ ᴜsᴇ ᴛʜɪs!", show_alert=True)
    await query.answer()
    await client.mongodb.clear_custom_buttons()
    await _render_custom_buttons_panel(client, query)
