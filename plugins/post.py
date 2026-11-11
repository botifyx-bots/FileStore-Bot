"""
plugins/post.py
───────────────
Admin-only post management system.

Commands
────────
/addchnl -100xxx   – add a channel for posting (bot verifies rights immediately)
/delchnl -100xxx   – remove a post channel
/post              – open main post menu
/send              – send / apply the active post session
/abort             – cancel the active post session
"""

import re
import asyncio
from datetime import datetime

from pyrogram import Client, filters
from pyrogram.types import (
    Message,
    CallbackQuery,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)
from pyrogram.types import InputMediaPhoto
from plugins.channel_post import EXCLUDED_COMMANDS
from helper.post_state import sessions as _sessions, active as _active

CHANNELS_PER_PAGE = 6
_URL_RE = re.compile(r'^https?://', re.IGNORECASE)


# ─── helpers ──────────────────────────────────────────────────────────────────

def _is_admin(client: Client, user_id: int) -> bool:
    return user_id in client.admins

def _has_session(user_id: int) -> bool:
    return user_id in _sessions

def _clear_session(user_id: int):
    _sessions.pop(user_id, None)
    _active.discard(user_id)

async def _get_post_channels(client: Client) -> dict:
    return await client.mongodb.get_post_channels()

async def _verify_bot_rights(client: Client, channel_id: int) -> tuple[bool, str]:
    try:
        me     = await client.get_me()
        member = await client.get_chat_member(channel_id, me.id)
        privs  = member.privileges
        if not privs:
            return False, "ʙᴏᴛ ɪs ɴᴏᴛ ᴀɴ ᴀᴅᴍɪɴ ɪɴ ᴛʜɪs ᴄʜᴀɴɴᴇʟ."
        if not privs.can_post_messages:
            return False, "ʙᴏᴛ ʟᴀᴄᴋs <b>ᴘᴏsᴛ ᴍᴇssᴀɢᴇs</b> ᴘᴇʀᴍɪssɪᴏɴ."
        if not privs.can_edit_messages:
            return False, "ʙᴏᴛ ʟᴀᴄᴋs <b>ᴇᴅɪᴛ ᴍᴇssᴀɢᴇs</b> ᴘᴇʀᴍɪssɪᴏɴ."
        return True, ""
    except Exception as e:
        return False, str(e)


# ─── Button parser ─────────────────────────────────────────────────────────────

def safe_callback(data: str, limit: int = 40) -> str:
    """
    Telegram callback_data limit is 64 bytes.
    This safely trims UTF-8 strings.
    """
    return data.encode("utf-8")[:limit].decode("utf-8", "ignore")


def _parse_buttons(text: str) -> list[list[InlineKeyboardButton]]:
    rows: list[list[InlineKeyboardButton]] = []

    for raw_line in text.strip().splitlines():
        line = raw_line.strip()

        if not line:
            continue

        # Single popup button
        if " - " not in line:
            rows.append([
                InlineKeyboardButton(
                    line[:64],  # visible button text
                    callback_data=f"post_alert:{safe_callback(line)}"
                )
            ])
            continue

        cells = [c.strip() for c in line.split("|")]

        if len(cells) > 3:
            raise ValueError(
                f"ᴛᴏᴏ ᴍᴀɴʏ ʙᴜᴛᴛᴏɴs ɪɴ ᴏɴᴇ ʀᴏᴡ (ᴍᴀx 3):\n<code>{line}</code>"
            )

        row: list[InlineKeyboardButton] = []

        for cell in cells:

            if " - " not in cell:
                raise ValueError(
                    f"ɪɴᴠᴀʟɪᴅ ꜰᴏʀᴍᴀᴛ — ᴇxᴘᴇᴄᴛᴇᴅ <code>ᴛᴇxᴛ - ᴜʀʟ</code>:\n<code>{cell}</code>"
                )

            label, _, value = cell.partition(" - ")

            label = label.strip()
            value = value.strip()

            if not label or not value:
                raise ValueError(
                    f"ᴇᴍᴘᴛʏ ʟᴀʙᴇʟ ᴏʀ ᴠᴀʟᴜᴇ: <code>{cell}</code>"
                )

            # URL button
            if _URL_RE.match(value):

                row.append(
                    InlineKeyboardButton(
                        text=label[:64],
                        url=value
                    )
                )

            # Popup alert button
            else:

                safe_data = safe_callback(value)

                row.append(
                    InlineKeyboardButton(
                        text=label[:64],
                        callback_data=f"post_alert:{safe_data}"
                    )
                )

        if row:
            rows.append(row)

    if not rows:
        raise ValueError("ɴᴏ ᴠᴀʟɪᴅ ʙᴜᴛᴛᴏɴs ꜰᴏᴜɴᴅ ɪɴ ʏᴏᴜʀ ᴛᴇxᴛ.")

    return rows


# ─── Keyboards ────────────────────────────────────────────────────────────────

def _main_menu_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("» ᴄʀᴇᴀᴛᴇ ᴘᴏsᴛ «",   callback_data="post_create")],
        [
            InlineKeyboardButton("✎ ᴇᴅɪᴛ ᴘᴏsᴛ",     callback_data="post_edit"),
            InlineKeyboardButton("◈ ᴄʜᴀɴɴᴇʟ sᴛᴀᴛs", callback_data="post_stats"),
        ],
        [InlineKeyboardButton("✗ ᴄʟᴏsᴇ",             callback_data="post_close")],
    ])


def _channel_picker_kb(channels: dict, page: int, back_cb: str = "post_back_main") -> InlineKeyboardMarkup:
    items = sorted(channels.items(), key=lambda x: x[1].get("name", ""))
    total = len(items)
    pages = max(1, (total + CHANNELS_PER_PAGE - 1) // CHANNELS_PER_PAGE)
    page  = max(0, min(page, pages - 1))
    chunk = items[page * CHANNELS_PER_PAGE: (page + 1) * CHANNELS_PER_PAGE]

    kb: list[list[InlineKeyboardButton]] = []
    row: list[InlineKeyboardButton] = []
    for cid_str, cdata in chunk:
        name = cdata.get("name", cid_str)[:22]
        row.append(InlineKeyboardButton(f"• {name}", callback_data=f"post_sel_ch:{cid_str}"))
        if len(row) == 3:
            kb.append(row); row = []
    if row:
        kb.append(row)

    nav: list[InlineKeyboardButton] = []
    if page > 0:
        nav.append(InlineKeyboardButton("« ᴘʀᴇᴠ", callback_data=f"post_ch_page:{page-1}"))
    nav.append(InlineKeyboardButton(f"[ {page+1} / {pages} ]", callback_data="noop"))
    if page < pages - 1:
        nav.append(InlineKeyboardButton("ɴᴇxᴛ »", callback_data=f"post_ch_page:{page+1}"))
    if nav:
        kb.append(nav)

    kb.append([InlineKeyboardButton("‹ ʙᴀᴄᴋ", callback_data=back_cb)])
    return InlineKeyboardMarkup(kb)


# ─── /addchnl ─────────────────────────────────────────────────────────────────

@Client.on_message(filters.private & filters.command("addchnl"))
async def cmd_addchnl(client: Client, message: Message):
    if not _is_admin(client, message.from_user.id):
        return await message.reply(client.reply_text)
    args = message.command
    if len(args) < 2:
        return await message.reply(
            "<blockquote><b>⌗ ᴜsᴀɢᴇ</b>\n\n"
            "<code>/addchnl -100xxxxxxxxxx</code></blockquote>"
        )
    try:
        channel_id = int(args[1])
    except ValueError:
        return await message.reply(
            "<blockquote>✗ ɪɴᴠᴀʟɪᴅ ɪᴅ — ᴍᴜsᴛ ʙᴇ ᴀ ɴᴜᴍʙᴇʀ ʟɪᴋᴇ <code>-100xxxxxxxxxx</code></blockquote>"
        )
    ok, err = await _verify_bot_rights(client, channel_id)
    if not ok:
        return await message.reply(
            f"<blockquote>✗ <b>ᴄᴀɴɴᴏᴛ ᴀᴅᴅ ᴄʜᴀɴɴᴇʟ</b>\n\n{err}\n\n"
            f"ᴇɴsᴜʀᴇ ᴛʜᴇ ʙᴏᴛ ɪs ᴀᴅᴍɪɴ ᴡɪᴛʜ <b>ᴘᴏsᴛ ᴍᴇssᴀɢᴇs</b> "
            f"ᴀɴᴅ <b>ᴇᴅɪᴛ ᴍᴇssᴀɢᴇs</b> ᴘᴇʀᴍɪssɪᴏɴs.</blockquote>"
        )
    try:
        chat = await client.get_chat(channel_id)
        name = chat.title
    except Exception as e:
        return await message.reply(f"<blockquote>✗ ᴄᴏᴜʟᴅ ɴᴏᴛ ꜰᴇᴛᴄʜ ᴄʜᴀɴɴᴇʟ ɪɴꜰᴏ : {e}</blockquote>")
    await client.mongodb.add_post_channel(channel_id, {
        "name":     name,
        "added_on": datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC"),
    })
    await message.reply(f"<blockquote>✓ <b>{name}</b> ᴀᴅᴅᴇᴅ ᴀs ᴀ ᴘᴏsᴛ ᴄʜᴀɴɴᴇʟ.</blockquote>")


# ─── /delchnl ─────────────────────────────────────────────────────────────────

@Client.on_message(filters.private & filters.command("delchnl"))
async def cmd_delchnl(client: Client, message: Message):
    if not _is_admin(client, message.from_user.id):
        return await message.reply(client.reply_text)
    args = message.command
    if len(args) < 2:
        return await message.reply(
            "<blockquote><b>⌗ ᴜsᴀɢᴇ</b>\n\n<code>/delchnl -100xxxxxxxxxx</code></blockquote>"
        )
    try:
        channel_id = int(args[1])
    except ValueError:
        return await message.reply("<blockquote>✗ ɪɴᴠᴀʟɪᴅ ᴄʜᴀɴɴᴇʟ ɪᴅ.</blockquote>")
    channels = await _get_post_channels(client)
    if str(channel_id) not in channels:
        return await message.reply("<blockquote>✗ ᴛʜɪs ᴄʜᴀɴɴᴇʟ ɪs ɴᴏᴛ ɪɴ ᴛʜᴇ ᴘᴏsᴛ-ᴄʜᴀɴɴᴇʟs ʟɪsᴛ.</blockquote>")
    name = channels[str(channel_id)].get("name", str(channel_id))
    await client.mongodb.remove_post_channel(channel_id)
    await message.reply(f"<blockquote>✓ <b>{name}</b> ʀᴇᴍᴏᴠᴇᴅ ꜰʀᴏᴍ ᴘᴏsᴛ ᴄʜᴀɴɴᴇʟs.</blockquote>")


# ─── /post ────────────────────────────────────────────────────────────────────

@Client.on_message(filters.private & filters.command("post"))
async def cmd_post(client: Client, message: Message):
    if not _is_admin(client, message.from_user.id):
        return await message.reply(client.reply_text)
    await message.reply(
        "<blockquote><b>▸ ᴘᴏsᴛ ᴍᴀɴᴀɢᴇʀ</b>\n\nsᴇʟᴇᴄᴛ ᴀɴ ᴏᴘᴛɪᴏɴ ʙᴇʟᴏᴡ :</blockquote>",
        reply_markup=_main_menu_kb(),
    )


# ─── /abort ───────────────────────────────────────────────────────────────────

@Client.on_message(filters.private & filters.command("abort"))
async def cmd_abort(client: Client, message: Message):
    if not _is_admin(client, message.from_user.id):
        return await message.reply(client.reply_text)
    if not _has_session(message.from_user.id):
        return await message.reply("<blockquote>◌ ɴᴏ ᴀᴄᴛɪᴠᴇ ᴘᴏsᴛ sᴇssɪᴏɴ ᴛᴏ ᴀʙᴏʀᴛ.</blockquote>")
    _clear_session(message.from_user.id)
    await message.reply("<blockquote>✗ ᴘᴏsᴛ sᴇssɪᴏɴ ᴀʙᴏʀᴛᴇᴅ.</blockquote>")


# ─── /send ────────────────────────────────────────────────────────────────────

@Client.on_message(filters.private & filters.command("send"))
async def cmd_send(client: Client, message: Message):
    uid = message.from_user.id
    if not _is_admin(client, uid):
        return await message.reply(client.reply_text)
    if not _has_session(uid):
        return await message.reply(
            "<blockquote>◌ ɴᴏ ᴀᴄᴛɪᴠᴇ sᴇssɪᴏɴ — ᴜsᴇ /post ᴛᴏ sᴛᴀʀᴛ.</blockquote>"
        )

    sess = _sessions[uid]
    mode = sess.get("mode")

    # ── CREATE ────────────────────────────────────────────────────────────────
    if mode == "create":
        if sess.get("step") != "READY":
            return await message.reply(
                "<blockquote>△ ᴘᴏsᴛ ɪs ɴᴏᴛ ʀᴇᴀᴅʏ ʏᴇᴛ — ᴄᴏᴍᴘʟᴇᴛᴇ ᴛʜᴇ sᴇᴛᴜᴘ ꜰɪʀsᴛ.</blockquote>"
            )
        channel_id   = sess["channel_id"]
        content_msg  = sess["content_msg"]
        buttons      = sess.get("buttons")
        reply_markup = InlineKeyboardMarkup(buttons) if buttons else None
        try:
            sent = await _copy_to_channel(client, content_msg, channel_id, reply_markup)
        except Exception as e:
            return await message.reply(
                f"<blockquote>✗ ꜰᴀɪʟᴇᴅ ᴛᴏ sᴇɴᴅ ᴘᴏsᴛ : <code>{e}</code></blockquote>"
            )
        channels = await _get_post_channels(client)
        cname    = channels.get(str(channel_id), {}).get("name", str(channel_id))
        post_url = f"https://t.me/c/{str(channel_id).replace('-100', '')}/{sent.id}"
        _clear_session(uid)
        await message.reply(
            f"<blockquote>✓ ᴘᴏsᴛ sᴇɴᴛ sᴜᴄᴄᴇssꜰᴜʟʟʏ ᴛᴏ <b>{cname}</b>\n\n"
            f"» <a href='{post_url}'>ᴠɪᴇᴡ ᴘᴏsᴛ</a></blockquote>",
            disable_web_page_preview=True,
        )

    # ── EDIT ──────────────────────────────────────────────────────────────────
    elif mode == "edit":
        if sess.get("step") != "EDIT_READY":
            return await message.reply(
                "<blockquote>△ ᴇᴅɪᴛ ɪs ɴᴏᴛ ʀᴇᴀᴅʏ ʏᴇᴛ — ᴄᴏᴍᴘʟᴇᴛᴇ ᴛʜᴇ sᴇᴛᴜᴘ ꜰɪʀsᴛ.</blockquote>"
            )
        channel_id  = sess["channel_id"]
        edit_msg_id = sess["edit_msg_id"]
        edit_type   = sess.get("edit_type")
        content_msg = sess.get("content_msg")
        buttons     = sess.get("buttons")
        try:
            if edit_type == "media":
                await _edit_channel_post_media(client, channel_id, edit_msg_id, content_msg)
            elif edit_type == "buttons":
                reply_markup = InlineKeyboardMarkup(buttons) if buttons else None
                await client.edit_message_reply_markup(channel_id, edit_msg_id, reply_markup)
        except Exception as e:
            return await message.reply(
                f"<blockquote>✗ ꜰᴀɪʟᴇᴅ ᴛᴏ ᴇᴅɪᴛ ᴘᴏsᴛ : <code>{e}</code></blockquote>"
            )
        channels = await _get_post_channels(client)
        cname    = channels.get(str(channel_id), {}).get("name", str(channel_id))
        post_url = f"https://t.me/c/{str(channel_id).replace('-100', '')}/{edit_msg_id}"
        _clear_session(uid)
        await message.reply(
            f"<blockquote>✓ ᴘᴏsᴛ ᴇᴅɪᴛᴇᴅ sᴜᴄᴄᴇssꜰᴜʟʟʏ ɪɴ <b>{cname}</b>\n\n"
            f"» <a href='{post_url}'>ᴠɪᴇᴡ ᴘᴏsᴛ</a></blockquote>",
            disable_web_page_preview=True,
        )
    else:
        await message.reply(
            "<blockquote>✗ ᴜɴᴋɴᴏᴡɴ sᴇssɪᴏɴ ᴍᴏᴅᴇ — ᴜsᴇ /abort ᴀɴᴅ sᴛᴀʀᴛ ᴀɢᴀɪɴ.</blockquote>"
        )


# ─── Copy / edit helpers ───────────────────────────────────────────────────────

async def _copy_to_channel(client: Client, src: Message, channel_id: int, reply_markup) -> Message:
    if src.document or src.audio or src.video or src.voice or src.video_note:
        return await src.copy(
        chat_id=channel_id,
        reply_markup=reply_markup
    )
    if src.photo:
        return await client.send_photo(
            chat_id=channel_id,
            photo=src.photo.file_id,
            caption=src.caption.html if src.caption else None,
            reply_markup=reply_markup,
        )
    if src.text:
        return await client.send_message(
            chat_id=channel_id,
            text=src.text.html,
            reply_markup=reply_markup,
        )
    return await src.copy(chat_id=channel_id, reply_markup=reply_markup)


async def _edit_channel_post_media(client: Client, channel_id: int, msg_id: int, new_msg: Message):
    if new_msg.photo:
        await client.edit_message_media(
            chat_id=channel_id,
            message_id=msg_id,
            media=InputMediaPhoto(
                media=new_msg.photo.file_id,
                caption=new_msg.caption.html if new_msg.caption else None,
            ),
        )
    elif new_msg.text:
        await client.edit_message_text(
            chat_id=channel_id,
            message_id=msg_id,
            text=new_msg.text.html,
        )
    else:
        await new_msg.copy(chat_id=channel_id)


# ─── Resolve post link / forward ──────────────────────────────────────────────

async def _resolve_post_ref(client: Client, message: Message) -> tuple[int | None, int | None]:
    # pyrofork uses forward_from_chat / forward_from_message_id (no forward_origin)
    if getattr(message, 'forward_from_chat', None) and getattr(message, 'forward_from_message_id', None):
        return message.forward_from_message_id, message.forward_from_chat.id

    if message.text:
        m = re.search(r't\.me/c/(\d+)/(\d+)', message.text)
        if m:
            return int(m.group(2)), int(f"-100{m.group(1)}")
        m2 = re.search(r't\.me/([^/]+)/(\d+)', message.text)
        if m2:
            try:
                chat = await client.get_chat(m2.group(1))
                return int(m2.group(2)), chat.id
            except Exception:
                pass
    return None, None


# ─── Preview sender ────────────────────────────────────────────────────────────

async def _send_preview(client: Client, chat_id: int, sess: dict):
    content_msg: Message = sess["content_msg"]
    buttons      = sess.get("buttons")
    reply_markup = InlineKeyboardMarkup(buttons) if buttons else None

    await client.send_message(chat_id=chat_id, text="<blockquote>◉ <b>ᴘᴏsᴛ ᴘʀᴇᴠɪᴇᴡ :</b></blockquote>")
    try:
        if content_msg.photo:
            await client.send_photo(
                chat_id=chat_id,
                photo=content_msg.photo.file_id,
                caption=content_msg.caption.html if content_msg.caption else None,
                reply_markup=reply_markup,
            )
        elif content_msg.text:
            await client.send_message(
                chat_id=chat_id,
                text=content_msg.text.html,
                reply_markup=reply_markup,
            )
        else:
            await content_msg.copy(chat_id=chat_id, reply_markup=None)
    except Exception as e:
        await client.send_message(
            chat_id=chat_id,
            text=f"<blockquote>△ ᴘʀᴇᴠɪᴇᴡ ᴇʀʀᴏʀ : <code>{e}</code></blockquote>",
        )
    await client.send_message(
        chat_id=chat_id,
        text="<blockquote>✓ ᴘᴏsᴛ ɪs ʀᴇᴀᴅʏ\n\nsᴇɴᴅ /send ᴛᴏ ᴘᴜʙʟɪsʜ  ·  /abort ᴛᴏ ᴄᴀɴᴄᴇʟ</blockquote>",
    )


# ─── Callbacks: Close / noop / alert ──────────────────────────────────────────

@Client.on_callback_query(filters.regex(r'^post_close$'))
async def cb_post_close(client: Client, query: CallbackQuery):
    if not _is_admin(client, query.from_user.id):
        return await query.answer("✗ ᴀᴅᴍɪɴs ᴏɴʟʏ.", show_alert=True)
    await query.message.delete()
    await query.answer()


@Client.on_callback_query(filters.regex(r'^noop$'))
async def cb_noop(client: Client, query: CallbackQuery):
    await query.answer()


@Client.on_callback_query(filters.regex(r'^post_alert:'))
async def cb_post_alert(client: Client, query: CallbackQuery):
    await query.answer(query.data.split(":", 1)[1], show_alert=True)


# ─── Callback: Back to main menu ──────────────────────────────────────────────

@Client.on_callback_query(filters.regex(r'^post_back_main$'))
async def cb_back_main(client: Client, query: CallbackQuery):
    if not _is_admin(client, query.from_user.id):
        return await query.answer("✗ ᴀᴅᴍɪɴs ᴏɴʟʏ.", show_alert=True)
    _clear_session(query.from_user.id)
    await query.message.edit_text(
        "<blockquote><b>▸ ᴘᴏsᴛ ᴍᴀɴᴀɢᴇʀ</b>\n\nsᴇʟᴇᴄᴛ ᴀɴ ᴏᴘᴛɪᴏɴ ʙᴇʟᴏᴡ :</blockquote>",
        reply_markup=_main_menu_kb(),
    )
    await query.answer()


# ─── Callback: Create Post ────────────────────────────────────────────────────

@Client.on_callback_query(filters.regex(r'^post_create$'))
async def cb_post_create(client: Client, query: CallbackQuery):
    uid = query.from_user.id
    if not _is_admin(client, uid):
        return await query.answer("✗ ᴀᴅᴍɪɴs ᴏɴʟʏ.", show_alert=True)
    if _has_session(uid):
        return await query.answer(
            "△ ʏᴏᴜ ᴀʟʀᴇᴀᴅʏ ʜᴀᴠᴇ ᴀɴ ᴀᴄᴛɪᴠᴇ sᴇssɪᴏɴ — ᴜsᴇ /abort ꜰɪʀsᴛ.",
            show_alert=True,
        )
    channels = await _get_post_channels(client)
    if not channels:
        await query.answer()
        return await query.message.edit_text(
            "<blockquote><b>◌ ɴᴏ ᴘᴏsᴛ ᴄʜᴀɴɴᴇʟs ᴀᴅᴅᴇᴅ ʏᴇᴛ</b>\n\n"
            "ᴀᴅᴅ ᴏɴᴇ ᴜsɪɴɢ :\n<code>/addchnl -100xxxxxxxxxx</code></blockquote>",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("‹ ʙᴀᴄᴋ", callback_data="post_back_main")]
            ]),
        )
    _sessions[uid] = {"mode": "create", "step": "SELECT_CHANNEL", "page": 0}
    _active.add(uid)
    await query.message.edit_text(
        "<blockquote><b>▸ sᴇʟᴇᴄᴛ ᴀ ᴄʜᴀɴɴᴇʟ :</b></blockquote>",
        reply_markup=_channel_picker_kb(channels, 0),
    )
    await query.answer()


# ─── Callback: Channel picker pagination ──────────────────────────────────────

@Client.on_callback_query(filters.regex(r'^post_ch_page:(\d+)$'))
async def cb_ch_page(client: Client, query: CallbackQuery):
    uid  = query.from_user.id
    page = int(query.matches[0].group(1))
    if not _is_admin(client, uid):
        return await query.answer("✗ ᴀᴅᴍɪɴs ᴏɴʟʏ.", show_alert=True)
    if uid in _sessions:
        _sessions[uid]["page"] = page
    channels = await _get_post_channels(client)
    await query.message.edit_reply_markup(reply_markup=_channel_picker_kb(channels, page))
    await query.answer()


# ─── Callback: Channel selected ───────────────────────────────────────────────

@Client.on_callback_query(filters.regex(r'^post_sel_ch:(-?\d+)$'))
async def cb_sel_channel(client: Client, query: CallbackQuery):
    uid        = query.from_user.id
    channel_id = int(query.matches[0].group(1))
    if not _is_admin(client, uid):
        return await query.answer("✗ ᴀᴅᴍɪɴs ᴏɴʟʏ.", show_alert=True)
    if uid not in _sessions:
        return await query.answer("sᴇssɪᴏɴ ᴇxᴘɪʀᴇᴅ — ᴜsᴇ /post ᴀɢᴀɪɴ.", show_alert=True)
    channels = await _get_post_channels(client)
    cname    = channels.get(str(channel_id), {}).get("name", str(channel_id))
    _sessions[uid].update({"step": "WAITING_CONTENT", "channel_id": channel_id})
    await query.message.edit_text(
        f"<blockquote><b>◈ ᴄʜᴀɴɴᴇʟ : {cname}</b>\n\n"
        f"sᴇɴᴅ ʏᴏᴜʀ ᴘᴏsᴛ ɴᴏᴡ\n\n"
        f"ʏᴏᴜ ᴄᴀɴ sᴇɴᴅ :\n"
        f"<b>ᴛᴇxᴛ  ·  ᴘʜᴏᴛᴏ  ·  ᴘʜᴏᴛᴏ + ᴄᴀᴘᴛɪᴏɴ</b>\n"
        f"<b>ᴅᴏᴄᴜᴍᴇɴᴛ  ·  ᴀᴜᴅɪᴏ  ·  ᴠɪᴅᴇᴏ</b>\n\n"
        f"ᴜsᴇ /abort ᴛᴏ ᴄᴀɴᴄᴇʟ</blockquote>"
    )
    await query.answer()


# ─── Message handler: all session input ───────────────────────────────────────

@Client.on_message(
    filters.private & ~filters.command(EXCLUDED_COMMANDS),
    group=2,
)
async def handle_session_input(client: Client, message: Message):
    uid = message.from_user.id
    if not _is_admin(client, uid) or uid not in _sessions:
        return

    sess = _sessions[uid]
    step = sess.get("step")

    # ── Waiting for post content ──────────────────────────────────────────────
    if step == "WAITING_CONTENT":
        sess["content_msg"] = message
        sess["step"]        = "WAITING_BTN_CHOICE"
        is_file = bool(
            message.document or message.audio
            or message.video  or message.voice
            or message.video_note
        )
        if is_file:
            sess["buttons"] = None
            sess["step"]    = "READY"
            await _send_preview(client, message.chat.id, sess)
            return
        await message.reply(
            "<blockquote><b>◆ ᴀᴅᴅ ʙᴜᴛᴛᴏɴs ᴛᴏ ᴛʜɪs ᴘᴏsᴛ ?</b></blockquote>",
            reply_markup=InlineKeyboardMarkup([
                [
                    InlineKeyboardButton("✎ ᴀᴅᴅ ᴍᴀɴᴜᴀʟʟʏ", callback_data="post_btn_manual"),
                    InlineKeyboardButton("▦ ꜰʀᴏᴍ ꜰʙᴀᴛᴄʜ",   callback_data="post_btn_fbatch"),
                ],
                [InlineKeyboardButton("» sᴋɪᴘ ʙᴜᴛᴛᴏɴs",    callback_data="post_btn_skip")],
            ]),
        )

    # ── Waiting for manual buttons ────────────────────────────────────────────
    elif step == "WAITING_MANUAL_BUTTONS":
        try:
            buttons = _parse_buttons(message.text or "")
        except ValueError as e:
            return await message.reply(
                f"<blockquote>✗ <b>ʙᴜᴛᴛᴏɴ ꜰᴏʀᴍᴀᴛ ᴇʀʀᴏʀ :</b>\n\n{e}\n\nᴛʀʏ ᴀɢᴀɪɴ ᴏʀ /abort</blockquote>"
            )
        sess["buttons"] = buttons
        sess["step"]    = "READY"
        await _send_preview(client, message.chat.id, sess)

    # ── Waiting for fbatch paste ──────────────────────────────────────────────
    elif step == "WAITING_FBATCH_TEXT":
        try:
            buttons = _parse_buttons(message.text or "")
        except ValueError as e:
            return await message.reply(
                f"<blockquote>✗ <b>ᴄᴏᴜʟᴅ ɴᴏᴛ ᴘᴀʀsᴇ ꜰʙᴀᴛᴄʜ ᴏᴜᴛᴘᴜᴛ :</b>\n\n{e}\n\nᴛʀʏ ᴀɢᴀɪɴ ᴏʀ /abort</blockquote>"
            )
        sess["buttons"] = buttons
        sess["step"]    = "READY"
        await _send_preview(client, message.chat.id, sess)

    # ── Edit: waiting for post reference ──────────────────────────────────────
    elif step == "EDIT_WAITING_POST":
        msg_id, channel_id = await _resolve_post_ref(client, message)
        if not msg_id:
            return await message.reply(
                "<blockquote>✗ ᴄᴏᴜʟᴅ ɴᴏᴛ ʀᴇsᴏʟᴠᴇ ᴛʜɪs ᴍᴇssᴀɢᴇ\n\n"
                "ꜰᴏʀᴡᴀʀᴅ ᴛʜᴇ ᴄʜᴀɴɴᴇʟ ᴘᴏsᴛ ʜᴇʀᴇ ᴏʀ sᴇɴᴅ ɪᴛs ᴅɪʀᴇᴄᴛ ʟɪɴᴋ\n"
                "ᴛʀʏ ᴀɢᴀɪɴ ᴏʀ /abort</blockquote>"
            )
        sess["edit_msg_id"] = msg_id
        sess["channel_id"]  = channel_id
        sess["step"]        = "EDIT_WAITING_CHOICE"
        await message.reply(
            "<blockquote><b>✎ ᴡʜᴀᴛ ᴅᴏ ʏᴏᴜ ᴡᴀɴᴛ ᴛᴏ ᴇᴅɪᴛ ?</b></blockquote>",
            reply_markup=InlineKeyboardMarkup([
                [
                    InlineKeyboardButton("▣ ᴍᴇᴅɪᴀ / ᴛᴇxᴛ", callback_data="post_edit_media"),
                    InlineKeyboardButton("◉ ʙᴜᴛᴛᴏɴs",       callback_data="post_edit_buttons"),
                ],
                [InlineKeyboardButton("✗ ᴄᴀɴᴄᴇʟ",           callback_data="post_back_main")],
            ]),
        )

    # ── Edit: waiting for new media ────────────────────────────────────────────
    elif step == "EDIT_WAITING_MEDIA":
        sess["content_msg"] = message
        sess["step"]        = "EDIT_READY"
        await message.reply(
            "<blockquote>✓ <b>ɴᴇᴡ ᴄᴏɴᴛᴇɴᴛ ʀᴇᴄᴇɪᴠᴇᴅ</b>\n\n"
            "sᴇɴᴅ /send ᴛᴏ ᴀᴘᴘʟʏ  ·  /abort ᴛᴏ ᴄᴀɴᴄᴇʟ</blockquote>"
        )

    # ── Edit: waiting for new buttons ─────────────────────────────────────────
    elif step == "EDIT_WAITING_BUTTONS":
        try:
            buttons = _parse_buttons(message.text or "")
        except ValueError as e:
            return await message.reply(
                f"<blockquote>✗ <b>ʙᴜᴛᴛᴏɴ ꜰᴏʀᴍᴀᴛ ᴇʀʀᴏʀ :</b>\n\n{e}\n\nᴛʀʏ ᴀɢᴀɪɴ ᴏʀ /abort</blockquote>"
            )
        sess["buttons"]   = buttons
        sess["edit_type"] = "buttons"
        sess["step"]      = "EDIT_READY"
        await message.reply(
            "<blockquote>✓ <b>ɴᴇᴡ ʙᴜᴛᴛᴏɴs ʀᴇᴀᴅʏ</b>\n\n"
            "sᴇɴᴅ /send ᴛᴏ ᴀᴘᴘʟʏ  ·  /abort ᴛᴏ ᴄᴀɴᴄᴇʟ</blockquote>"
        )


# ─── Callback: Button add choice ──────────────────────────────────────────────

@Client.on_callback_query(filters.regex(r'^post_btn_(manual|fbatch|skip)$'))
async def cb_btn_choice(client: Client, query: CallbackQuery):
    uid    = query.from_user.id
    choice = query.matches[0].group(1)
    if not _is_admin(client, uid):
        return await query.answer("✗ ᴀᴅᴍɪɴs ᴏɴʟʏ.", show_alert=True)
    if uid not in _sessions:
        return await query.answer("sᴇssɪᴏɴ ᴇxᴘɪʀᴇᴅ — ᴜsᴇ /post", show_alert=True)

    sess = _sessions[uid]
    if choice == "skip":
        sess["buttons"] = None
        sess["step"]    = "READY"
        await query.message.delete()
        await _send_preview(client, query.message.chat.id, sess)
        return await query.answer()

    if choice == "manual":
        sess["step"] = "WAITING_MANUAL_BUTTONS"
        await query.message.edit_text(
            "<blockquote><b>✎ sᴇɴᴅ ᴍᴇ ᴛʜᴇ ʙᴜᴛᴛᴏɴs :</b></blockquote>\n\n"
            "<b>ꜰᴏʀᴍᴀᴛ :</b>\n"
            "<code>Button text 1 - http://example.com/\n"
            "Button text 2 - http://example2.com/</code>\n\n"
            "<b>ᴜsᴇ | ꜰᴏʀ ᴜᴘ ᴛᴏ 3 ʙᴜᴛᴛᴏɴs ᴘᴇʀ ʀᴏᴡ :</b>\n"
            "<code>Btn 1 - http://x.com/ | Btn 2 - http://y.com/\n"
            "Btn 3 - http://z.com/</code>\n\n"
            "<b>ᴘᴏᴘᴜᴘ ᴀʟᴇʀᴛ (ɴᴏ ʟɪɴᴋ) — ᴜsᴇ ᴘʟᴀɪɴ ᴛᴇxᴛ ᴀs ᴠᴀʟᴜᴇ :</b>\n"
            "<code>Season 01 - SEASON 01\n"
            "480p - https://xxx | 720p - https://xxx\n"
            "1080p - https://xxx\n"
            "Season 02 - SEASON 02\n"
            "480p - https://xxx | 720p - https://xxx</code>\n\n"
            "ᴜsᴇ /abort ᴛᴏ ᴄᴀɴᴄᴇʟ"
        )
    elif choice == "fbatch":
        sess["step"] = "WAITING_FBATCH_TEXT"
        await query.message.edit_text(
            "<blockquote><b>▦ ᴘᴀsᴛᴇ ᴛʜᴇ ꜰʙᴀᴛᴄʜ ᴏᴜᴛᴘᴜᴛ ʙᴇʟᴏᴡ :</b></blockquote>\n\n"
            "ᴄᴏᴘʏ ᴛʜᴇ ǫᴜᴀʟɪᴛʏ-ʟɪɴᴋs ᴛᴇxᴛ ꜰʀᴏᴍ ᴛʜᴇ <code>/fbatch</code> ʀᴇsᴜʟᴛ\n"
            "(ᴄᴏɴᴛᴇɴᴛ ɪɴsɪᴅᴇ ᴛʜᴇ ᴄᴏᴅᴇ ʙʟᴏᴄᴋ) ᴀɴᴅ ᴘᴀsᴛᴇ ɪᴛ ʜᴇʀᴇ\n\n"
            "ᴜsᴇ /abort ᴛᴏ ᴄᴀɴᴄᴇʟ"
        )
    await query.answer()


# ─── Callback: Edit Post ──────────────────────────────────────────────────────

@Client.on_callback_query(filters.regex(r'^post_edit$'))
async def cb_post_edit(client: Client, query: CallbackQuery):
    uid = query.from_user.id
    if not _is_admin(client, uid):
        return await query.answer("✗ ᴀᴅᴍɪɴs ᴏɴʟʏ.", show_alert=True)
    if _has_session(uid):
        return await query.answer(
            "△ ʏᴏᴜ ᴀʟʀᴇᴀᴅʏ ʜᴀᴠᴇ ᴀɴ ᴀᴄᴛɪᴠᴇ sᴇssɪᴏɴ — ᴜsᴇ /abort ꜰɪʀsᴛ.",
            show_alert=True,
        )
    _sessions[uid] = {"mode": "edit", "step": "EDIT_WAITING_POST"}
    _active.add(uid)
    await query.message.edit_text(
        "<blockquote><b>✎ ᴇᴅɪᴛ ᴘᴏsᴛ</b>\n\n"
        "ꜰᴏʀᴡᴀʀᴅ ᴛʜᴇ ᴄʜᴀɴɴᴇʟ ᴘᴏsᴛ ʜᴇʀᴇ\n"
        "ᴏʀ sᴇɴᴅ ɪᴛs ᴅɪʀᴇᴄᴛ ʟɪɴᴋ :\n"
        "<code>https://t.me/c/123456789/42</code>\n\n"
        "ᴜsᴇ /abort ᴛᴏ ᴄᴀɴᴄᴇʟ</blockquote>"
    )
    await query.answer()


# ─── Callback: Edit choice ────────────────────────────────────────────────────

@Client.on_callback_query(filters.regex(r'^post_edit_(media|buttons)$'))
async def cb_edit_choice(client: Client, query: CallbackQuery):
    uid    = query.from_user.id
    choice = query.matches[0].group(1)
    if not _is_admin(client, uid):
        return await query.answer("✗ ᴀᴅᴍɪɴs ᴏɴʟʏ.", show_alert=True)
    if uid not in _sessions:
        return await query.answer("sᴇssɪᴏɴ ᴇxᴘɪʀᴇᴅ — ᴜsᴇ /post", show_alert=True)

    sess = _sessions[uid]
    if choice == "media":
        sess["step"]      = "EDIT_WAITING_MEDIA"
        sess["edit_type"] = "media"
        await query.message.edit_text(
            "<blockquote><b>▣ sᴇɴᴅ ᴛʜᴇ ɴᴇᴡ ᴄᴏɴᴛᴇɴᴛ :</b>\n\n"
            "sᴇɴᴅ ᴀ ɴᴇᴡ ᴘʜᴏᴛᴏ + ᴄᴀᴘᴛɪᴏɴ ᴏʀ ᴘʟᴀɪɴ ᴛᴇxᴛ\n\n"
            "ᴜsᴇ /abort ᴛᴏ ᴄᴀɴᴄᴇʟ</blockquote>"
        )
    else:
        sess["step"]      = "EDIT_WAITING_BUTTONS"
        sess["edit_type"] = "buttons"
        await query.message.edit_text(
            "<blockquote><b>◉ sᴇɴᴅ ᴛʜᴇ ɴᴇᴡ ʙᴜᴛᴛᴏɴs :</b>\n\n"
            "ᴜsᴇ ᴛʜᴇ sᴀᴍᴇ ꜰᴏʀᴍᴀᴛ ᴀs ᴄʀᴇᴀᴛᴇ-ᴘᴏsᴛ ʙᴜᴛᴛᴏɴs\n"
            "ᴏʀ ᴘᴀsᴛᴇ ꜰʙᴀᴛᴄʜ ᴏᴜᴛᴘᴜᴛ ᴅɪʀᴇᴄᴛʟʏ\n\n"
            "ᴜsᴇ /abort ᴛᴏ ᴄᴀɴᴄᴇʟ</blockquote>"
        )
    await query.answer()


# ─── Callback: Channel Stats ──────────────────────────────────────────────────

@Client.on_callback_query(filters.regex(r'^post_stats$'))
async def cb_post_stats(client: Client, query: CallbackQuery):
    uid = query.from_user.id
    if not _is_admin(client, uid):
        return await query.answer("✗ ᴀᴅᴍɪɴs ᴏɴʟʏ.", show_alert=True)
    channels = await _get_post_channels(client)
    if not channels:
        await query.answer()
        return await query.message.edit_text(
            "<blockquote>◌ ɴᴏ ᴘᴏsᴛ ᴄʜᴀɴɴᴇʟs ᴀᴅᴅᴇᴅ ʏᴇᴛ\n\n"
            "ᴜsᴇ <code>/addchnl -100xxxxxxxxxx</code> ᴛᴏ ᴀᴅᴅ ᴏɴᴇ</blockquote>",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("‹ ʙᴀᴄᴋ", callback_data="post_back_main")]
            ]),
        )
    await _show_stats_page(query.message, channels, page=0, edit=True)
    await query.answer()


@Client.on_callback_query(filters.regex(r'^post_stats_page:(\d+)$'))
async def cb_stats_page(client: Client, query: CallbackQuery):
    if not _is_admin(client, query.from_user.id):
        return await query.answer("✗ ᴀᴅᴍɪɴs ᴏɴʟʏ.", show_alert=True)
    channels = await _get_post_channels(client)
    await _show_stats_page(
        query.message, channels,
        page=int(query.matches[0].group(1)),
        edit=True,
    )
    await query.answer()


@Client.on_callback_query(filters.regex(r'^post_ch_info:(-?\d+)$'))
async def cb_ch_info(client: Client, query: CallbackQuery):
    if not _is_admin(client, query.from_user.id):
        return await query.answer("✗ ᴀᴅᴍɪɴs ᴏɴʟʏ.", show_alert=True)
    channel_id = int(query.matches[0].group(1))
    channels   = await _get_post_channels(client)
    cdata      = channels.get(str(channel_id), {})
    cname      = cdata.get("name",     str(channel_id))
    added_on   = cdata.get("added_on", "ᴜɴᴋɴᴏᴡɴ")
    await query.message.edit_text(
        f"<blockquote><b>◈ ᴄʜᴀɴɴᴇʟ ɪɴꜰᴏ</b>\n\n"
        f"◆ <b>ɴᴀᴍᴇ :</b> {cname}\n"
        f"⌗ <b>ɪᴅ :</b> <code>{channel_id}</code>\n"
        f"◷ <b>ᴀᴅᴅᴇᴅ ᴏɴ :</b> {added_on}</blockquote>",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("‹ ʙᴀᴄᴋ", callback_data="post_stats")]
        ]),
    )
    await query.answer()


async def _show_stats_page(message: Message, channels: dict, page: int, edit: bool):
    items = sorted(channels.items(), key=lambda x: x[1].get("name", ""))
    total = len(items)
    pages = max(1, (total + CHANNELS_PER_PAGE - 1) // CHANNELS_PER_PAGE)
    page  = max(0, min(page, pages - 1))
    chunk = items[page * CHANNELS_PER_PAGE: (page + 1) * CHANNELS_PER_PAGE]

    kb: list[list[InlineKeyboardButton]] = []
    row: list[InlineKeyboardButton] = []
    for cid_str, cdata in chunk:
        name = cdata.get("name", cid_str)[:22]
        row.append(InlineKeyboardButton(f"• {name}", callback_data=f"post_ch_info:{cid_str}"))
        if len(row) == 3:
            kb.append(row); row = []
    if row:
        kb.append(row)

    nav: list[InlineKeyboardButton] = []
    if page > 0:
        nav.append(InlineKeyboardButton("« ᴘʀᴇᴠ", callback_data=f"post_stats_page:{page-1}"))
    nav.append(InlineKeyboardButton(f"[ {page+1} / {pages} ]", callback_data="noop"))
    if page < pages - 1:
        nav.append(InlineKeyboardButton("ɴᴇxᴛ »", callback_data=f"post_stats_page:{page+1}"))
    if nav:
        kb.append(nav)

    kb.append([InlineKeyboardButton("‹ ʙᴀᴄᴋ", callback_data="post_back_main")])

    text = (
        "<blockquote><b>◈ ᴘᴏsᴛ ᴄʜᴀɴɴᴇʟs</b>\n\n"
        "sᴇʟᴇᴄᴛ ᴀ ᴄʜᴀɴɴᴇʟ ᴛᴏ ᴠɪᴇᴡ ɪᴛs ᴅᴇᴛᴀɪʟs :</blockquote>"
    )
    if edit:
        await message.edit_text(text, reply_markup=InlineKeyboardMarkup(kb))
    else:
        await message.reply(text, reply_markup=InlineKeyboardMarkup(kb))
