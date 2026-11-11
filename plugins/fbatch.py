"""
plugins/fbatch.py
─────────────────
/fbatch  – Admin/Owner only.
           Scan a DB-channel range, auto-group files by Season → Quality
           (lowest to highest: 480p → 720p → 1080p → 4K → HD …),
           store each quality-group in MongoDB, and reply with a formatted
           quality-links panel.

/setfbatch – Admin/Owner only.
             Interactive wizard to set:
               • custom_pic   (photo file_id / URL shown before files)
               • start_sticker (sticker sent after info card)
               • end_sticker   (sticker sent after all files)
"""

import os
import asyncio
import secrets
from datetime import datetime

from pyrogram import Client, filters
from pyrogram.errors import FloodWait
from pyrogram.types import (
    Message,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)

from helper.fbatch_helper import (
    extract_quality,
    extract_season,
    extract_audio,
    extract_show_title,
    group_files_by_season_quality,
    build_quality_links_text_plain,
    build_info_caption,
    get_quality_priority,
    get_quality_display,
)
from helper.helper_func import get_message_id, encode
from helper.post_state import active as _active


# ─── Helpers ──────────────────────────────────────────────────────────────────

def _is_admin(client: Client, user_id: int) -> bool:
    return user_id in client.admins


async def _get_db_channels_info(client: Client) -> str:
    """Return a formatted string listing all DB channels (reused from link_generator)."""
    db_channels = getattr(client, 'db_channels', {})
    primary_db  = getattr(client, 'primary_db_channel', client.db)

    if not db_channels:
        try:
            chat = await client.get_chat(primary_db)
            link = getattr(chat, 'invite_link', None)
            if link:
                return f"<blockquote>✦ ᴅʙ ᴄʜᴀɴɴᴇʟ: <a href='{link}'>{chat.title}</a></blockquote>"
            return f"<blockquote>✦ ᴅʙ ᴄʜᴀɴɴᴇʟ: {chat.title} (`{primary_db}`)</blockquote>"
        except Exception:
            return f"<blockquote>✦ ᴅʙ ᴄʜᴀɴɴᴇʟ: `{primary_db}`</blockquote>"

    rows = ["<blockquote>✦ ᴀᴠᴀɪʟᴀʙʟᴇ ᴅʙ ᴄʜᴀɴɴᴇʟs:</blockquote>"]
    for cid_str, cdata in db_channels.items():
        name  = cdata.get('name', 'Unknown')
        label = "✦ ᴘʀɪᴍᴀʀʏ" if cdata.get('is_primary') else "• sᴇᴄᴏɴᴅᴀʀʏ"
        try:
            chat = await client.get_chat(int(cid_str))
            link = getattr(chat, 'invite_link', None)
            rows.append(f"{label}: <a href='{link}'>{name}</a>" if link
                        else f"{label}: {name} (`{cid_str}`)")
        except Exception:
            rows.append(f"{label}: {name} (`{cid_str}`)")
    return "\n".join(rows)


# ─── /fbatch command ───────────────────────────────────────────────────────────

@Client.on_message(filters.private & filters.command("fbatch"))
async def fbatch_command(client: Client, message: Message):
    """Admin/owner command: generate quality-grouped batch links."""
    user_id = message.from_user.id
    if not _is_admin(client, user_id):
        return await message.reply(client.reply_text)

    db_info = await _get_db_channels_info(client)

    # Block DB-channel forwarding for the entire conversation
    _active.add(user_id)
    try:
        # ── Step 1: First message ─────────────────────────────────────────────────
        while True:
            try:
                first_msg = await client.ask(
                    chat_id=user_id,
                    text=(
                        "<blockquote><b>✦ ꜰʙᴀᴛᴄʜ — sᴛᴇᴘ 1/2</b></blockquote>\n\n"
                        "ꜰᴏʀᴡᴀʀᴅ ᴛʜᴇ <b>ꜰɪʀsᴛ</b> ᴍᴇssᴀɢᴇ ꜰʀᴏᴍ ᴛʜᴇ ᴅʙ ᴄʜᴀɴɴᴇʟ\n"
                        "(ᴏʀ sᴇɴᴅ ᴛʜᴇ ᴘᴏsᴛ ʟɪɴᴋ)\n\n"
                        f"{db_info}"
                    ),
                    filters=(filters.forwarded | (filters.text & ~filters.forwarded)),
                    timeout=120,
                )
            except asyncio.TimeoutError:
                await message.reply("<blockquote>⏰ ᴛɪᴍᴇᴅ ᴏᴜᴛ. ᴜsᴇ /fbatch ᴀɢᴀɪɴ.</blockquote>")
                return
            except Exception:
                return

            f_msg_id, source_channel_id = await get_message_id(client, first_msg)
            if f_msg_id:
                break
            await first_msg.reply(
                "<blockquote>✗ ɪɴᴠᴀʟɪᴅ</blockquote>\n"
                "ᴛʜɪs ᴍᴇssᴀɢᴇ ɪs ɴᴏᴛ ꜰʀᴏᴍ ᴀ ᴋɴᴏᴡɴ ᴅʙ ᴄʜᴀɴɴᴇʟ. ᴛʀʏ ᴀɢᴀɪɴ.",
                quote=True,
            )

        # ── Step 2: Last message ──────────────────────────────────────────────
        while True:
            try:
                last_msg = await client.ask(
                    chat_id=user_id,
                    text=(
                        "<blockquote><b>✦ ꜰʙᴀᴛᴄʜ — sᴛᴇᴘ 2/2</b></blockquote>\n\n"
                        "ꜰᴏʀᴡᴀʀᴅ ᴛʜᴇ <b>ʟᴀsᴛ</b> ᴍᴇssᴀɢᴇ ꜰʀᴏᴍ ᴛʜᴇ ᴅʙ ᴄʜᴀɴɴᴇʟ\n"
                        "(ᴏʀ sᴇɴᴅ ᴛʜᴇ ᴘᴏsᴛ ʟɪɴᴋ)\n\n"
                        f"{db_info}"
                    ),
                    filters=(filters.forwarded | (filters.text & ~filters.forwarded)),
                    timeout=120,
                )
            except asyncio.TimeoutError:
                await message.reply("<blockquote>⏰ ᴛɪᴍᴇᴅ ᴏᴜᴛ. ᴜsᴇ /fbatch ᴀɢᴀɪɴ.</blockquote>")
                return
            except Exception:
                return

            s_msg_id, _ = await get_message_id(client, last_msg)
            if s_msg_id:
                break
            await last_msg.reply(
                "<blockquote>✗ ɪɴᴠᴀʟɪᴅ</blockquote>\n"
                "ᴛʜɪs ᴍᴇssᴀɢᴇ ɪs ɴᴏᴛ ꜰʀᴏᴍ ᴀ ᴋɴᴏᴡɴ ᴅʙ ᴄʜᴀɴɴᴇʟ. ᴛʀʏ ᴀɢᴀɪɴ.",
                quote=True,
            )

    finally:
        # Always unblock DB-channel forwarding when fbatch conversation ends
        _active.discard(user_id)

    # Ensure correct order
    if f_msg_id > s_msg_id:
        f_msg_id, s_msg_id = s_msg_id, f_msg_id

    # ── Scan range ────────────────────────────────────────────────────────────
    progress = await last_msg.reply(
        f"<blockquote>⏳ sᴄᴀɴɴɪɴɢ {s_msg_id - f_msg_id + 1} ᴍᴇssᴀɢᴇs…</blockquote>",
        quote=True,
    )

    file_list: list[dict] = []
    try:
        all_ids = list(range(f_msg_id, s_msg_id + 1))
        msgs = []
        for i in range(0, len(all_ids), 200):  # Telegram's get_messages id-count limit
            chunk_ids = all_ids[i:i + 200]
            try:
                chunk_msgs = await client.get_messages(chat_id=source_channel_id, message_ids=chunk_ids)
            except FloodWait as e:
                await asyncio.sleep(e.x)
                chunk_msgs = await client.get_messages(chat_id=source_channel_id, message_ids=chunk_ids)
            msgs.extend(chunk_msgs)
        for m in msgs:
            if m and m.document and m.document.file_name:
                file_list.append({
                    "msg_id":     m.id,
                    "channel_id": source_channel_id,
                    "filename":   m.document.file_name,
                })
    except Exception as e:
        return await progress.edit_text(f"<blockquote>✗ ᴇʀʀᴏʀ sᴄᴀɴɴɪɴɢ ʀᴀɴɢᴇ:</blockquote> <code>{e}</code>")

    if not file_list:
        return await progress.edit_text(
            "<blockquote>✗ ɴᴏ ᴅᴏᴄᴜᴍᴇɴᴛs ꜰᴏᴜɴᴅ ɪɴ ᴛʜɪs ʀᴀɴɢᴇ.</blockquote>"
        )

    # ── Group by Season → Quality ─────────────────────────────────────────────
    grouped = group_files_by_season_quality(file_list)
    # {season: {quality: [file_info, ...]}}

    # Derive common metadata from the first file
    first_fname   = file_list[0]["filename"]
    show_title    = extract_show_title(first_fname)
    audio         = extract_audio(first_fname)

    # All seasons (sorted) and all qualities across all seasons
    all_seasons   = sorted(grouped.keys())
    all_qualities_global = sorted(
        {q for s in grouped.values() for q in s.keys()},
        key=get_quality_priority,
    )

    # ── Save each quality-group to MongoDB & build link map ───────────────────
    season_quality_links: dict[str, dict[str, str]] = {}

    for season in all_seasons:
        season_quality_links[season] = {}
        season_qualities = sorted(grouped[season].keys(), key=get_quality_priority)

        for quality in season_qualities:
            files_in_group = grouped[season][quality]
            batch_id       = "fbatch_" + secrets.token_hex(8)

            doc = {
                "show_title":    show_title,
                "season":        season,
                "audio":         audio,
                "quality":       quality,
                "all_qualities": [get_quality_display(q) for q in season_qualities],
                "all_seasons":   all_seasons,
                "msg_ids":       [fi["msg_id"]     for fi in files_in_group],
                "channel_id":    source_channel_id,
                "created_at":    datetime.utcnow(),
            }
            await client.mongodb.save_fbatch_group(batch_id, doc)

            # Encode the batch_id exactly like /batch and /genlink encode their payloads,
            # so the link looks identical in format and works with the shortener system.
            encoded = await encode(batch_id)
            link = f"https://t.me/{client.username}?start={encoded}"
            season_quality_links[season][quality] = link

    # ── Build and send the quality-links panel ────────────────────────────────
    # Plain-text version goes inside <code> so every URL is directly copy-pasteable
    links_plain = build_quality_links_text_plain(season_quality_links)

    header = (
        f"<blockquote><b>✓ ꜰʙᴀᴛᴄʜ ᴄᴏᴍᴘʟᴇᴛᴇ</b></blockquote>\n\n"
        f"<b>ᴀɴɪᴍᴇ :</b> {show_title}\n"
        f"<b>ᴀᴜᴅɪᴏ :</b> {audio or 'ɴ/ᴀ'}\n"
        f"<b>sᴇᴀsᴏɴs :</b> {', '.join(all_seasons)}\n\n"
        f"<b>ǫᴜᴀʟɪᴛʏ ʟɪɴᴋs:</b>\n\n"
        f"<code>{links_plain}</code>"
    )

    await progress.delete()
    await last_msg.reply(
        header,
        quote=True,
        disable_web_page_preview=True,
    )


# ─── /setfbatch command ────────────────────────────────────────────────────────

@Client.on_message(filters.private & filters.command("setfbatch"))
async def setfbatch_command(client: Client, message: Message):
    """
    Admin/owner wizard to configure fbatch assets:
      custom_pic, start_sticker, end_sticker
    """
    user_id = message.from_user.id
    if not _is_admin(client, user_id):
        return await message.reply(client.reply_text)

    # ── Fetch current settings ────────────────────────────────────────────────
    cur_pic   = await client.mongodb.get_bot_setting("fbatch_custom_pic",    "✗ ɴᴏᴛ sᴇᴛ")
    cur_start = await client.mongodb.get_bot_setting("fbatch_start_sticker", "✗ ɴᴏᴛ sᴇᴛ")
    cur_end   = await client.mongodb.get_bot_setting("fbatch_end_sticker",   "✗ ɴᴏᴛ sᴇᴛ")

    panel_text = (
        "<blockquote><b>✦ ꜰʙᴀᴛᴄʜ sᴇᴛᴛɪɴɢs</b></blockquote>\n\n"
        f"›› <b>ᴄᴜsᴛᴏᴍ ᴘɪᴄ :</b> <code>{cur_pic}</code>\n"
        f"›› <b>sᴛᴀʀᴛ sᴛɪᴄᴋᴇʀ :</b> <code>{cur_start}</code>\n"
        f"›› <b>ᴇɴᴅ sᴛɪᴄᴋᴇʀ :</b> <code>{cur_end}</code>\n\n"
        "<i>ʀᴇᴘʟʏ ᴡɪᴛʜ ᴡʜᴀᴛ ʏᴏᴜ ᴡᴀɴᴛ ᴛᴏ ᴄʜᴀɴɢᴇ ʙᴇʟᴏᴡ:</i>"
    )

    buttons = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("sᴇᴛ ᴄᴜsᴛᴏᴍ ᴘɪᴄ",    callback_data="sfb_pic"),
            InlineKeyboardButton("sᴇᴛ sᴛᴀʀᴛ sᴛɪᴄᴋᴇʀ", callback_data="sfb_start"),
        ],
        [
            InlineKeyboardButton("sᴇᴛ ᴇɴᴅ sᴛɪᴄᴋᴇʀ",   callback_data="sfb_end"),
            InlineKeyboardButton("✓ ᴅᴏɴᴇ",             callback_data="sfb_done"),
        ],
    ])

    await message.reply(panel_text, reply_markup=buttons)


# ─── Callbacks for setfbatch panel ────────────────────────────────────────────

@Client.on_callback_query(filters.regex(r'^sfb_(pic|start|end|done)$'))
async def sfb_callback(client: Client, query):
    user_id = query.from_user.id
    if not _is_admin(client, user_id):
        return await query.answer("✗ ᴀᴅᴍɪɴs ᴏɴʟʏ.", show_alert=True)

    action = query.data  # sfb_pic / sfb_start / sfb_end / sfb_done

    if action == "sfb_done":
        await query.message.edit_text("<blockquote>✓ ꜰʙᴀᴛᴄʜ sᴇᴛᴛɪɴɢs sᴀᴠᴇᴅ.</blockquote>")
        return await query.answer()

    prompts = {
        "sfb_pic":   ("sᴇɴᴅ ᴛʜᴇ <b>ᴄᴜsᴛᴏᴍ ᴘɪᴄ</b> (ᴘʜᴏᴛᴏ ᴍᴇssᴀɢᴇ ᴏʀ ꜰɪʟᴇ_ɪᴅ / ᴜʀʟ):",   "fbatch_custom_pic"),
        "sfb_start": ("sᴇɴᴅ ᴛʜᴇ <b>sᴛᴀʀᴛ sᴛɪᴄᴋᴇʀ</b> (ꜰᴏʀᴡᴀʀᴅ ᴀ sᴛɪᴄᴋᴇʀ ᴏʀ sᴇɴᴅ ɪᴛs ꜰɪʟᴇ_ɪᴅ):", "fbatch_start_sticker"),
        "sfb_end":   ("sᴇɴᴅ ᴛʜᴇ <b>ᴇɴᴅ sᴛɪᴄᴋᴇʀ</b> (ꜰᴏʀᴡᴀʀᴅ ᴀ sᴛɪᴄᴋᴇʀ ᴏʀ sᴇɴᴅ ɪᴛs ꜰɪʟᴇ_ɪᴅ):",   "fbatch_end_sticker"),
    }

    prompt_text, setting_key = prompts[action]
    await query.answer()

    try:
        response = await client.ask(
            chat_id=user_id,
            text=f"<blockquote>{prompt_text}</blockquote>\n\n"
                 "<i>sᴇɴᴅ /cancel ᴛᴏ ᴀʙᴏʀᴛ.</i>",
            filters=(filters.text | filters.photo | filters.sticker),
            timeout=120,
        )
    except asyncio.TimeoutError:
        return await query.message.reply("<blockquote>⏰ ᴛɪᴍᴇᴅ ᴏᴜᴛ.</blockquote>")
    except Exception:
        return

    if response.text and response.text.strip() == "/cancel":
        return await response.reply("<blockquote>✗ ᴄᴀɴᴄᴇʟʟᴇᴅ.</blockquote>")

    # Extract the value: sticker → file_id, photo → file_id, text → URL/file_id
    value = None
    if response.sticker:
        value = response.sticker.file_id
    elif response.photo:
        value = response.photo.file_id
    elif response.text:
        value = response.text.strip()

    if not value:
        return await response.reply("<blockquote>✗ ᴄᴏᴜʟᴅɴ'ᴛ ᴇxᴛʀᴀᴄᴛ ᴀ ᴠᴀʟᴜᴇ. ᴛʀʏ ᴀɢᴀɪɴ.</blockquote>")

    await client.mongodb.update_bot_setting(setting_key, value)
    await response.reply(
        f"<blockquote>✓ <b>{setting_key}</b> ᴜᴘᴅᴀᴛᴇᴅ sᴜᴄᴄᴇssꜰᴜʟʟʏ!\n\n"
        f"<code>{value}</code></blockquote>"
    )

# ─── "Share and Support Us" alert callback ────────────────────────────────────

@Client.on_callback_query(filters.regex(r'^fbatch_share_alert$'))
async def fbatch_share_alert_cb(client: Client, query):
    """Show a popup alert when user taps the Share and Support Us button."""
    await query.answer(
        text="ꜱʜᴀʀᴇ ᴀɴᴅ ꜱᴜᴘᴘᴏʀᴛ ᴜꜱ -",
        show_alert=True,
    )
