from pyrogram import Client, filters
from pyrogram.types import CallbackQuery, Message, InlineKeyboardButton, InlineKeyboardMarkup
from helper.helper_func import is_bot_admin

#===============================================================#

async def fsub(client, query):
    # Create a formatted list of channels with names and IDs
    if client.fsub_dict:
        channel_list = []
        for channel_id, channel_data in client.fsub_dict.items():
            channel_name = channel_data[0] if channel_data and len(channel_data) > 0 else "ᴜɴᴋɴᴏᴡɴ"
            request_status = "ʀᴇǫᴜᴇsᴛ: ✓" if channel_data[2] else "ʀᴇǫᴜᴇsᴛ: ✗"
            timer_status = f"ᴛɪᴍᴇʀ: {channel_data[3]}ᴍ" if channel_data[3] > 0 else "ᴛɪᴍᴇʀ: ∞"
            channel_list.append(f"• `{channel_name}` (`{channel_id}`) - {request_status}, {timer_status}")

        channels_display = "\n".join(channel_list)
    else:
        channels_display = "_ɴᴏ ꜰᴏʀᴄᴇ sᴜʙsᴄʀɪᴘᴛɪᴏɴ ᴄʜᴀɴɴᴇʟs ᴄᴏɴꜰɪɢᴜʀᴇᴅ_"

    msg = f"""<blockquote>✦ <b>ꜰᴏʀᴄᴇ sᴜʙsᴄʀɪᴘᴛɪᴏɴ sᴇᴛᴛɪɴɢs</b></blockquote>
<blockquote>›› <b>ᴄᴏɴꜰɪɢᴜʀᴇᴅ ᴄʜᴀɴɴᴇʟs:</b>
{channels_display}</blockquote>

<blockquote>≡ ᴜsᴇ ᴛʜᴇ ᴀᴘᴘʀᴏᴘʀɪᴀᴛᴇ ʙᴜᴛᴛᴏɴ ʙᴇʟᴏᴡ ᴛᴏ ᴀᴅᴅ ᴏʀ ʀᴇᴍᴏᴠᴇ ᴀ ꜰᴏʀᴄᴇ sᴜʙ ᴄʜᴀɴɴᴇʟ.</blockquote>"""
    reply_markup = InlineKeyboardMarkup([
        [InlineKeyboardButton('ᴀᴅᴅ ᴄʜᴀɴɴᴇʟ', 'add_fsub'), InlineKeyboardButton('ʀᴇᴍᴏᴠᴇ ᴄʜᴀɴɴᴇʟ', 'rm_fsub')],
        [InlineKeyboardButton('◂ ʙᴀᴄᴋ', 'settings')]]
    )
    await query.message.edit_text(msg, reply_markup=reply_markup)
    return

#===============================================================#

@Client.on_callback_query(filters.regex('^add_fsub$'))
async def add_fsub(client: Client, query: CallbackQuery):
    await query.answer()
    ask_channel_info = await client.ask(
        query.from_user.id,
        "<blockquote>✎ sᴇɴᴅ ᴄʜᴀɴɴᴇʟ ɪᴅ (ɴᴇɢᴀᴛɪᴠᴇ ɪɴᴛᴇɢᴇʀ), ʀᴇǫᴜᴇsᴛ ʙᴏᴏʟᴇᴀɴ (ʏᴇs/ɴᴏ/ᴛʀᴜᴇ/ꜰᴀʟsᴇ), ᴛɪᴍᴇʀ (ɪɴᴛᴇɢᴇʀ, 0 ᴛᴏ ᴅɪsᴀʙʟᴇ) sᴇᴘᴀʀᴀᴛᴇᴅ ʙʏ ᴀ sᴘᴀᴄᴇ ɪɴ ᴛʜᴇ ɴᴇxᴛ 60 sᴇᴄᴏɴᴅs!</blockquote>\n"
        "<blockquote expandable>ᴇɢ: `-10089479289 yes 5`\n\n"
        "__ᴛʜɪs ᴍᴇᴀɴs `-10089479289` ɪs ᴛʜᴇ ꜰᴏʀᴄᴇ sᴜʙ ᴄʜᴀɴɴᴇʟ ɪᴅ, `yes` ᴇɴᴀʙʟᴇs ʀᴇǫᴜᴇsᴛ ᴍᴏᴅᴇ (ᴛʜᴇ ʟɪɴᴋ ʙᴇᴄᴏᴍᴇs ᴀ ʀᴇǫᴜᴇsᴛ-ᴛᴏ-ᴊᴏɪɴ ʟɪɴᴋ ᴀɴᴅ ᴛʜᴇ ʙᴏᴛ ᴡᴏʀᴋs ꜰᴏʀ ᴀ ᴜsᴇʀ ᴀs sᴏᴏɴ ᴀs ᴛʜᴇʏ ʀᴇǫᴜᴇsᴛ, ᴇᴠᴇɴ ʙᴇꜰᴏʀᴇ ʏᴏᴜ ᴀᴄᴄᴇᴘᴛ), `5` ɪs ᴛʜᴇ ᴛɪᴍᴇʀ ɪɴ ᴍɪɴᴜᴛᴇs ᴀꜰᴛᴇʀ ᴡʜɪᴄʜ ᴛʜᴇ ɪɴᴠɪᴛᴇ ʟɪɴᴋ ᴇxᴘɪʀᴇs.__</blockquote>",
        filters=filters.text, timeout=60
    )
    try:
        channel_info = ask_channel_info.text.split()
        channel_id, request, timer = channel_info
        channel_id = int(channel_id)
        if channel_id in client.fsub_dict.keys():
            return await ask_channel_info.reply("<blockquote>✗ ᴛʜɪs ᴄʜᴀɴɴᴇʟ ɪᴅ ᴀʟʀᴇᴀᴅʏ ᴇxɪsᴛs ɪɴ ᴛʜᴇ ꜰᴏʀᴄᴇ sᴜʙ ʟɪsᴛ, ʀᴇᴍᴏᴠᴇ ɪᴛ ᴛᴏ ᴄʜᴀɴɢᴇ ɪᴛs ᴄᴏɴꜰɪɢᴜʀᴀᴛɪᴏɴ!</blockquote>")
        val, res = await is_bot_admin(client, channel_id)
        if not val:
            return await ask_channel_info.reply(f"<blockquote>✗ ᴇʀʀᴏʀ:</blockquote> `{res}`")
        if request.lower() in ('true', 'on', 'yes'):
            request = True
        elif request.lower() in ('false', 'off', 'no'):
            request = False
        else:
            raise Exception("Invalid request value or type.")
        if timer.isdigit():
            timer = int(timer)
        else:
            raise Exception("Timer is not a valid integer.")
        chat = await client.get_chat(channel_id)
        name = chat.title
        if timer > 0:
            client.fsub_dict[channel_id] = [name, None, request, timer]
        else:
            chat_link = await client.create_chat_invite_link(channel_id, creates_join_request=request)
            link = chat_link.invite_link
            client.fsub_dict[channel_id] = [name, link, request, timer]

        # Update req_channels list if request is enabled
        if request and channel_id not in client.req_channels:
            client.req_channels.append(channel_id)
            await client.mongodb.set_channels(client.req_channels)

        # Save to database for persistence across bot restarts
        await client.mongodb.add_fsub_channel(channel_id, client.fsub_dict[channel_id])

        await fsub(client, query)
        return await ask_channel_info.reply(f"<blockquote>✓ ᴄʜᴀɴɴᴇʟ <b>{name.strip()}</b> ᴀᴅᴅᴇᴅ ᴀs ᴀ ꜰᴏʀᴄᴇ sᴜʙ ᴄʜᴀɴɴᴇʟ!</blockquote>")
    except Exception as e:
        return await ask_channel_info.reply(f"<blockquote>✗ ᴇʀʀᴏʀ:</blockquote> `{e}`")

#===============================================================#

@Client.on_callback_query(filters.regex('^rm_fsub$'))
async def rm_fsub(client: Client, query: CallbackQuery):
    await query.answer()
    ask_channel_info = await client.ask(
        query.from_user.id,
        "<blockquote>✎ sᴇɴᴅ ᴄʜᴀɴɴᴇʟ ɪᴅ (ɴᴇɢᴀᴛɪᴠᴇ ɪɴᴛᴇɢᴇʀ) ɪɴ ᴛʜᴇ ɴᴇxᴛ 60 sᴇᴄᴏɴᴅs!</blockquote>",
        filters=filters.text, timeout=60
    )
    try:
        channel_id = int(ask_channel_info.text)
        if channel_id not in client.fsub_dict.keys():
            return await ask_channel_info.reply("<blockquote>✗ ᴛʜɪs ᴄʜᴀɴɴᴇʟ ɪᴅ ɪs ɴᴏᴛ ɪɴ ᴛʜᴇ ꜰᴏʀᴄᴇ sᴜʙ ʟɪsᴛ!</blockquote>")

        # Check if it was a request channel and remove from req_channels
        if channel_id in client.req_channels:
            client.req_channels.remove(channel_id)
            await client.mongodb.set_channels(client.req_channels)

        client.fsub_dict.pop(channel_id)

        # Remove from database for persistence across bot restarts
        await client.mongodb.remove_fsub_channel(channel_id)

        await fsub(client, query)
        return await ask_channel_info.reply(f"<blockquote>✓ ᴄʜᴀɴɴᴇʟ `{channel_id}` ʜᴀs ʙᴇᴇɴ ʀᴇᴍᴏᴠᴇᴅ ᴀs ᴀ ꜰᴏʀᴄᴇ sᴜʙ ᴄʜᴀɴɴᴇʟ!</blockquote>")
    except Exception as e:
        return await ask_channel_info.reply(f"<blockquote>✗ ᴇʀʀᴏʀ:</blockquote> `{e}`")
