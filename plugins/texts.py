from pyrogram import Client, filters
from pyrogram.types import CallbackQuery, Message, InlineKeyboardButton, InlineKeyboardMarkup

#===============================================================#

async def texts(client, query):
    msg = f"""<blockquote>✦ <b>ᴛᴇxᴛ ᴄᴏɴꜰɪɢᴜʀᴀᴛɪᴏɴ</b></blockquote>
<blockquote>›› <b>sᴛᴀʀᴛ ᴍᴇssᴀɢᴇ:</b>
<pre>{client.messages.get('START', 'ᴇᴍᴘᴛʏ')}</pre>
›› <b>ꜰᴏʀᴄᴇ sᴜʙ ᴍᴇssᴀɢᴇ:</b>
<pre>{client.messages.get('FSUB', 'ᴇᴍᴘᴛʏ')}</pre>
›› <b>ᴀʙᴏᴜᴛ ᴍᴇssᴀɢᴇ:</b>
<pre>{client.messages.get('ABOUT', 'ᴇᴍᴘᴛʏ')}</pre>
›› <b>ᴄʜᴀɴɴᴇʟs ᴍᴇssᴀɢᴇ:</b>
<pre>{client.messages.get('CHANNELS', 'ᴇᴍᴘᴛʏ')}</pre>
›› <b>ʀᴇᴘʟʏ ᴍᴇssᴀɢᴇ:</b>
<pre>{client.reply_text}</pre></blockquote>"""
    reply_markup = InlineKeyboardMarkup([
        [InlineKeyboardButton(f'ꜱᴛᴀʀᴛ ᴛᴇxᴛ', 'start_txt'), InlineKeyboardButton(f'ꜰꜱᴜʙ ᴛᴇxᴛ', 'fsub_txt')],
        [InlineKeyboardButton('ʀᴇᴘʟʏ ᴛᴇxᴛ', 'reply_txt'), InlineKeyboardButton('ᴀʙᴏᴜᴛ ᴛᴇxᴛ', 'about_txt')],
        [InlineKeyboardButton('ᴄʜᴀɴɴᴇʟ ᴛᴇxᴛ', 'channels_txt')],
        [InlineKeyboardButton('◂ ʙᴀᴄᴋ', 'settings')]]
    )
    await query.message.edit_text(msg, reply_markup=reply_markup)
    return

#===============================================================#

@Client.on_callback_query(filters.regex("^start_txt$"))
async def start_txt(client: Client, query: CallbackQuery):
    await query.answer()
    ask_text = await client.ask(
        query.from_user.id,
        "<blockquote>✎ sᴇɴᴅ ᴛʜᴇ ɴᴇᴡ sᴛᴀʀᴛ ᴛᴇxᴛ ɪɴ ᴛʜᴇ ɴᴇxᴛ 60 sᴇᴄᴏɴᴅs, sᴇɴᴅ `0` ᴛᴏ ᴄᴀɴᴄᴇʟ.</blockquote>\n"
        "__ʏᴏᴜ ᴄᴀɴ ᴜsᴇ ʙᴏᴛʜ ᴍᴀʀᴋᴅᴏᴡɴ ᴀɴᴅ ʜᴛᴍʟ ꜰᴏʀᴍᴀᴛᴛɪɴɢ!__",
        filters=filters.text, timeout=60
    )
    try:
        text = ask_text.text
        if text == '0':
            return await ask_text.reply("<blockquote>✗ sᴛᴀʀᴛ ᴛᴇxᴛ ʜᴀs ɴᴏᴛ ʙᴇᴇɴ ᴄʜᴀɴɢᴇᴅ.</blockquote>")
        client.messages['START'] = text
        await client.mongodb.update_message_setting('START', text)
        await texts(client, query)
        return await ask_text.reply("<blockquote>✓ sᴛᴀʀᴛ ᴛᴇxᴛ ʜᴀs ʙᴇᴇɴ ᴄʜᴀɴɢᴇᴅ!</blockquote>")
    except Exception as e:
        return client.LOGGER(__name__, client.name).error(e)

#===============================================================#

@Client.on_callback_query(filters.regex("^fsub_txt$"))
async def force_txt(client: Client, query: CallbackQuery):
    await query.answer()
    ask_text = await client.ask(
        query.from_user.id,
        "<blockquote>✎ sᴇɴᴅ ᴛʜᴇ ɴᴇᴡ ꜰᴏʀᴄᴇ sᴜʙ ᴛᴇxᴛ ɪɴ ᴛʜᴇ ɴᴇxᴛ 60 sᴇᴄᴏɴᴅs, sᴇɴᴅ `0` ᴛᴏ ᴄᴀɴᴄᴇʟ.</blockquote>\n"
        "__ʏᴏᴜ ᴄᴀɴ ᴜsᴇ ʙᴏᴛʜ ᴍᴀʀᴋᴅᴏᴡɴ ᴀɴᴅ ʜᴛᴍʟ ꜰᴏʀᴍᴀᴛᴛɪɴɢ!__",
        filters=filters.text, timeout=60
    )
    try:
        text = ask_text.text
        if text == '0':
            return await ask_text.reply("<blockquote>✗ ꜰᴏʀᴄᴇ sᴜʙ ᴛᴇxᴛ ʜᴀs ɴᴏᴛ ʙᴇᴇɴ ᴄʜᴀɴɢᴇᴅ.</blockquote>")
        client.messages['FSUB'] = text
        await client.mongodb.update_message_setting('FSUB', text)
        await texts(client, query)
        return await ask_text.reply("<blockquote>✓ ꜰᴏʀᴄᴇ sᴜʙ ᴛᴇxᴛ ʜᴀs ʙᴇᴇɴ ᴄʜᴀɴɢᴇᴅ!</blockquote>")
    except Exception as e:
        return client.LOGGER(__name__, client.name).error(e)

#===============================================================#

@Client.on_callback_query(filters.regex("^about_txt$"))
async def about_txt(client: Client, query: CallbackQuery):
    await query.answer()
    ask_text = await client.ask(
        query.from_user.id,
        "<blockquote>✎ sᴇɴᴅ ᴛʜᴇ ɴᴇᴡ ᴀʙᴏᴜᴛ ᴛᴇxᴛ ɪɴ ᴛʜᴇ ɴᴇxᴛ 60 sᴇᴄᴏɴᴅs, sᴇɴᴅ `0` ᴛᴏ ᴄᴀɴᴄᴇʟ.</blockquote>\n"
        "__ʏᴏᴜ ᴄᴀɴ ᴜsᴇ ʙᴏᴛʜ ᴍᴀʀᴋᴅᴏᴡɴ ᴀɴᴅ ʜᴛᴍʟ ꜰᴏʀᴍᴀᴛᴛɪɴɢ!__",
        filters=filters.text, timeout=60
    )
    try:
        text = ask_text.text
        if text == '0':
            return await ask_text.reply("<blockquote>✗ ᴀʙᴏᴜᴛ ᴛᴇxᴛ ʜᴀs ɴᴏᴛ ʙᴇᴇɴ ᴄʜᴀɴɢᴇᴅ.</blockquote>")
        client.messages['ABOUT'] = text
        await client.mongodb.update_message_setting('ABOUT', text)
        await texts(client, query)
        return await ask_text.reply("<blockquote>✓ ᴀʙᴏᴜᴛ ᴛᴇxᴛ ʜᴀs ʙᴇᴇɴ ᴄʜᴀɴɢᴇᴅ!</blockquote>")
    except Exception as e:
        return client.LOGGER(__name__, client.name).error(e)

#==========================================================================#

@Client.on_callback_query(filters.regex("^channels_txt$"))
async def channels_txt(client: Client, query: CallbackQuery):
    await query.answer()
    ask_text = await client.ask(
        query.from_user.id,
        "<blockquote>✎ sᴇɴᴅ ᴛʜᴇ ɴᴇᴡ ᴄʜᴀɴɴᴇʟs ᴛᴇxᴛ ɪɴ ᴛʜᴇ ɴᴇxᴛ 60 sᴇᴄᴏɴᴅs, sᴇɴᴅ `0` ᴛᴏ ᴄᴀɴᴄᴇʟ.</blockquote>\n"
        "__ʏᴏᴜ ᴄᴀɴ ᴜsᴇ ʙᴏᴛʜ ᴍᴀʀᴋᴅᴏᴡɴ ᴀɴᴅ ʜᴛᴍʟ ꜰᴏʀᴍᴀᴛᴛɪɴɢ!__",
        filters=filters.text, timeout=60
    )
    try:
        text = ask_text.text
        if text == '0':
            return await ask_text.reply("<blockquote>✗ ᴄʜᴀɴɴᴇʟs ᴛᴇxᴛ ʜᴀs ɴᴏᴛ ʙᴇᴇɴ ᴄʜᴀɴɢᴇᴅ.</blockquote>")
        client.messages['CHANNELS'] = text
        await client.mongodb.update_message_setting('CHANNELS', text)
        await texts(client, query)
        return await ask_text.reply("<blockquote>✓ ᴄʜᴀɴɴᴇʟs ᴛᴇxᴛ ʜᴀs ʙᴇᴇɴ ᴄʜᴀɴɢᴇᴅ!</blockquote>")
    except Exception as e:
        return client.LOGGER(__name__, client.name).error(e)
#===============================================================#

@Client.on_callback_query(filters.regex("^reply_txt$"))
async def reply_txt(client: Client, query: CallbackQuery):
    await query.answer()
    ask_text = await client.ask(
        query.from_user.id,
        "<blockquote>✎ sᴇɴᴅ ᴛʜᴇ ɴᴇᴡ ʀᴇᴘʟʏ ᴛᴇxᴛ ɪɴ ᴛʜᴇ ɴᴇxᴛ 60 sᴇᴄᴏɴᴅs, sᴇɴᴅ `0` ᴛᴏ ᴄᴀɴᴄᴇʟ.</blockquote>\n"
        "__ʏᴏᴜ ᴄᴀɴ ᴜsᴇ ʙᴏᴛʜ ᴍᴀʀᴋᴅᴏᴡɴ ᴀɴᴅ ʜᴛᴍʟ ꜰᴏʀᴍᴀᴛᴛɪɴɢ!__",
        filters=filters.text, timeout=60
    )
    try:
        text = ask_text.text
        if text == '0':
            return await ask_text.reply("<blockquote>✗ ʀᴇᴘʟʏ ᴛᴇxᴛ ʜᴀs ɴᴏᴛ ʙᴇᴇɴ ᴄʜᴀɴɢᴇᴅ.</blockquote>")
        client.reply_text = text
        await client.mongodb.update_message_setting('REPLY', text)
        await texts(client, query)
        return await ask_text.reply("<blockquote>✓ ʀᴇᴘʟʏ ᴛᴇxᴛ ʜᴀs ʙᴇᴇɴ ᴄʜᴀɴɢᴇᴅ!</blockquote>")
    except Exception as e:
        return client.LOGGER(__name__, client.name).error(e)
