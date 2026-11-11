from pyrogram import Client, filters
from pyrogram.raw.types import MessageActionPinMessage
from pyrogram.errors import FloodWait, UserIsBlocked, InputUserDeactivated, UserNotParticipant, Forbidden, PeerIdInvalid, ChatAdminRequired
import asyncio

#===============================================================#

@Client.on_message(filters.command('users'))
async def user_count(client, message):
    if not message.from_user.id in client.admins:
        return await client.send_message(message.from_user.id, client.reply_text)
    total_users = await client.mongodb.full_userbase()
    await message.reply(f"<blockquote>✦ <b>{len(total_users)} ᴜsᴇʀs ᴀʀᴇ ᴜsɪɴɢ ᴛʜɪs ʙᴏᴛ ᴄᴜʀʀᴇɴᴛʟʏ!</b></blockquote>")

#===============================================================#

@Client.on_message(filters.private & filters.command('broadcast'))
async def send_text(client, message):
    admin_ids = client.admins
    user_id = message.from_user.id
    if user_id in admin_ids:

        if message.reply_to_message:
            query = await client.mongodb.full_userbase()
            broadcast_msg = message.reply_to_message
            total = 0
            successful = 0
            blocked = 0
            deleted = 0
            unsuccessful = 0

            pls_wait = await message.reply("<blockquote>›› ʙʀᴏᴀᴅᴄᴀsᴛɪɴɢ ᴍᴇssᴀɢᴇ... ᴛʜɪs ᴡɪʟʟ ᴛᴀᴋᴇ sᴏᴍᴇ ᴛɪᴍᴇ</blockquote>")
            for chat_id in query:
                try:
                    await broadcast_msg.copy(chat_id)
                    successful += 1
                except FloodWait as e:
                    await asyncio.sleep(e.x)
                    await broadcast_msg.copy(chat_id)
                    successful += 1
                except UserIsBlocked:
                    await client.mongodb.del_user(chat_id)
                    blocked += 1
                except InputUserDeactivated:
                    await client.mongodb.del_user(chat_id)
                    deleted += 1
                except Exception as e:
                    client.LOGGER(__name__, client.name).warning(f"Broadcast: failed to send to {chat_id}: {e}")
                    unsuccessful += 1
                total += 1

            status = f"""<blockquote>✦ <b>ʙʀᴏᴀᴅᴄᴀsᴛ ᴄᴏᴍᴘʟᴇᴛᴇᴅ</b></blockquote>
<blockquote expandable>›› <b>ᴛᴏᴛᴀʟ ᴜsᴇʀs:</b> <code>{total}</code>
›› <b>sᴜᴄᴄᴇssꜰᴜʟ:</b> <code>{successful}</code>
›› <b>ʙʟᴏᴄᴋᴇᴅ ᴜsᴇʀs:</b> <code>{blocked}</code>
›› <b>ᴅᴇʟᴇᴛᴇᴅ ᴀᴄᴄᴏᴜɴᴛs:</b> <code>{deleted}</code>
›› <b>ᴜɴsᴜᴄᴄᴇssꜰᴜʟ:</b> <code>{unsuccessful}</code></blockquote>"""

            return await pls_wait.edit(status)

        else:
            msg = await message.reply("<blockquote>✎ ᴜsᴇ ᴛʜɪs ᴄᴏᴍᴍᴀɴᴅ ᴀs ᴀ ʀᴇᴘʟʏ ᴛᴏ ᴀɴʏ ᴛᴇʟᴇɢʀᴀᴍ ᴍᴇssᴀɢᴇ.</blockquote>")
            await asyncio.sleep(8)
            await msg.delete()

#===============================================================#

@Client.on_message(filters.private & filters.command('pbroadcast'))
async def pin_bdcst_text(client, message):
    admin_ids = client.admins
    user_id = message.from_user.id
    if user_id in admin_ids:
        if message.reply_to_message:
            query = await client.mongodb.full_userbase()
            broadcast_msg = message.reply_to_message
            total = 0
            successful = 0
            blocked = 0
            deleted = 0
            unsuccessful = 0

            pls_wait = await message.reply("<blockquote>›› ʙʀᴏᴀᴅᴄᴀsᴛɪɴɢ ᴍᴇssᴀɢᴇ... ᴛʜɪs ᴡɪʟʟ ᴛᴀᴋᴇ sᴏᴍᴇ ᴛɪᴍᴇ</blockquote>")

            for chat_id in query:
                try:
                    # Send the message and capture the result
                    sent_msg = await broadcast_msg.copy(chat_id)
                    successful += 1

                    # Pin the sent message immediately after broadcasting
                    await client.pin_chat_message(chat_id=chat_id, message_id=sent_msg.id, both_sides=True)
                except FloodWait as e:
                    await asyncio.sleep(e.x)
                    # Retry sending and pinning after flood wait
                    sent_msg = await broadcast_msg.copy(chat_id)
                    successful += 1
                    await client.pin_chat_message(chat_id=chat_id, message_id=sent_msg.id)
                except UserIsBlocked:
                    await client.mongodb.del_user(chat_id)
                    blocked += 1
                except InputUserDeactivated:
                    await client.mongodb.del_user(chat_id)
                    deleted += 1
                except Exception as e:
                    client.LOGGER(__name__, client.name).warning(f"Pinned broadcast: failed to send to {chat_id}: {e}")
                    unsuccessful += 1
                total += 1

            status = f"""<blockquote>✦ <b>ʙʀᴏᴀᴅᴄᴀsᴛ ᴄᴏᴍᴘʟᴇᴛᴇᴅ</b></blockquote>
<blockquote expandable>›› <b>ᴛᴏᴛᴀʟ ᴜsᴇʀs:</b> <code>{total}</code>
›› <b>sᴜᴄᴄᴇssꜰᴜʟ:</b> <code>{successful}</code>
›› <b>ʙʟᴏᴄᴋᴇᴅ ᴜsᴇʀs:</b> <code>{blocked}</code>
›› <b>ᴅᴇʟᴇᴛᴇᴅ ᴀᴄᴄᴏᴜɴᴛs:</b> <code>{deleted}</code>
›› <b>ᴜɴsᴜᴄᴄᴇssꜰᴜʟ:</b> <code>{unsuccessful}</code></blockquote>"""

            return await pls_wait.edit(status)

        else:
            msg = await message.reply("<blockquote>✎ ᴜsᴇ ᴛʜɪs ᴄᴏᴍᴍᴀɴᴅ ᴀs ᴀ ʀᴇᴘʟʏ ᴛᴏ ᴀɴʏ ᴛᴇʟᴇɢʀᴀᴍ ᴍᴇssᴀɢᴇ.</blockquote>")
            await asyncio.sleep(8)
            await msg.delete()
