# ─────────────────────────────────────────────────────────────────────────
# Token / Credits Settings
#
# The shortener-verification flow (plugins/start.py, "yu3elk..." deep links)
# used to have its numbers hardcoded in code:
#   • starting credits for a brand new user
#   • credits rewarded per completed verification
#   • the anti-bypass minimum time (a "verification" done faster than this
#     is treated as a shortener bypass and rejected)
#   • how long a verification link stays valid before it expires
#
# This plugin exposes all four through /tokensettings so an admin can tune
# them from the bot itself — every value is validated as a sane positive
# integer before it's saved, so a bad entry can never be applied.
#
# /checktoken <user_id> lets an admin verify/inspect a specific user's
# currently pending verification token — whether it's active, what payload
# it's tied to, and how much time is left before it expires.
# ─────────────────────────────────────────────────────────────────────────

import time
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from pyrogram.errors.pyromod import ListenerTimeout

LABELS = {
    "starting_credits": "sᴛᴀʀᴛɪɴɢ ᴄʀᴇᴅɪᴛs (ɴᴇᴡ ᴜsᴇʀs)",
    "verify_reward_credits": "ᴄʀᴇᴅɪᴛs ᴘᴇʀ ᴠᴇʀɪꜰɪᴄᴀᴛɪᴏɴ",
    "verify_min_time": "ᴀɴᴛɪ-ʙʏᴘᴀss ᴍɪɴ ᴛɪᴍᴇ (sᴇᴄ)",
    "verify_session_timeout": "ᴠᴇʀɪꜰɪᴄᴀᴛɪᴏɴ ʟɪɴᴋ ᴇxᴘɪʀʏ (sᴇᴄ)",
}


async def _render_panel(client, target):
    settings = await client.mongodb.get_token_settings()

    msg = f"""<blockquote>🪙 ᴛᴏᴋᴇɴ / ᴄʀᴇᴅɪᴛs sᴇᴛᴛɪɴɢs</blockquote>
<blockquote>
›› **{LABELS['starting_credits']}:** `{settings['starting_credits']}`
›› **{LABELS['verify_reward_credits']}:** `{settings['verify_reward_credits']}`
›› **{LABELS['verify_min_time']}:** `{settings['verify_min_time']}`
›› **{LABELS['verify_session_timeout']}:** `{settings['verify_session_timeout']}`
</blockquote>
<blockquote>≡ ᴛᴀᴘ ᴀ ʙᴜᴛᴛᴏɴ ᴛᴏ ᴄʜᴀɴɢᴇ ᴀ ᴠᴀʟᴜᴇ. ᴀʟʟ ᴄʜᴀɴɢᴇs ᴀᴘᴘʟʏ ɪɴꜱᴛᴀɴᴛʟʏ, ɴᴏ ʀᴇꜱᴛᴀʀᴛ ɴᴇᴇᴅᴇᴅ.</blockquote>"""

    buttons = InlineKeyboardMarkup([
        [InlineKeyboardButton("• sᴛᴀʀᴛɪɴɢ ᴄʀᴇᴅɪᴛs •", "tset_starting_credits")],
        [InlineKeyboardButton("• ᴠᴇʀɪꜰʏ ʀᴇᴡᴀʀᴅ •", "tset_verify_reward_credits")],
        [InlineKeyboardButton("• ᴀɴᴛɪ-ʙʏᴘᴀss ᴍɪɴ ᴛɪᴍᴇ •", "tset_verify_min_time")],
        [InlineKeyboardButton("• ʟɪɴᴋ ᴇxᴘɪʀʏ ᴛɪᴍᴇ •", "tset_verify_session_timeout")],
        [InlineKeyboardButton("◂ ᴄʟᴏsᴇ", "close")],
    ])

    if isinstance(target, CallbackQuery):
        await target.message.edit_text(msg, reply_markup=buttons)
    else:
        await target.reply(msg, reply_markup=buttons, quote=True)


@Client.on_message(filters.command("tokensettings") & filters.private)
async def tokensettings_command(client: Client, message: Message):
    if message.from_user.id not in client.admins:
        return await message.reply(client.reply_text)
    await _render_panel(client, message)


@Client.on_callback_query(filters.regex("^tokensettings$"))
async def tokensettings_cb(client: Client, query: CallbackQuery):
    if query.from_user.id not in client.admins:
        return await query.answer("✗ ᴏɴʟʏ ᴀᴅᴍɪɴs ᴄᴀɴ ᴜsᴇ ᴛʜɪs!", show_alert=True)
    await query.answer()
    await _render_panel(client, query)


@Client.on_callback_query(filters.regex("^tset_(starting_credits|verify_reward_credits|verify_min_time|verify_session_timeout)$"))
async def tokensettings_edit(client: Client, query: CallbackQuery):
    if query.from_user.id not in client.admins:
        return await query.answer("✗ ᴏɴʟʏ ᴀᴅᴍɪɴs ᴄᴀɴ ᴜsᴇ ᴛʜɪs!", show_alert=True)
    await query.answer()

    key = query.data[len("tset_"):]
    current = await client.mongodb.get_token_setting(key)

    await query.message.edit_text(
        f"<blockquote>**{LABELS[key]}**</blockquote>\n"
        f"ᴄᴜʀʀᴇɴᴛ ᴠᴀʟᴜᴇ: `{current}`\n\n"
        "__sᴇɴᴅ ᴛʜᴇ ɴᴇᴡ ᴠᴀʟᴜᴇ (ᴀ ᴡʜᴏʟᴇ ɴᴜᴍʙᴇʀ, 0 ᴏʀ ᴍᴏʀᴇ) ɪɴ ᴛʜᴇ ɴᴇxᴛ 60 sᴇᴄᴏɴᴅs__",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("◂ ᴄᴀɴᴄᴇʟ", "tokensettings")]])
    )

    try:
        res = await client.listen(user_id=query.from_user.id, filters=filters.text, timeout=60)
    except ListenerTimeout:
        return await query.message.edit_text(
            "<blockquote>⏰ ᴛɪᴍᴇᴏᴜᴛ! ᴛʀʏ ᴀɢᴀɪɴ.</blockquote>",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("◂ ʙᴀᴄᴋ", "tokensettings")]])
        )

    raw = res.text.strip()
    if not raw.isdigit():
        return await res.reply(
            "<blockquote>✗ ɪɴᴠᴀʟɪᴅ ᴠᴀʟᴜᴇ! ᴍᴜsᴛ ʙᴇ ᴀ ᴡʜᴏʟᴇ ɴᴜᴍʙᴇʀ, 0 ᴏʀ ᴍᴏʀᴇ. ɴᴏᴛʜɪɴɢ ᴡᴀs ᴄʜᴀɴɢᴇᴅ.</blockquote>",
            quote=True,
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("◂ ʙᴀᴄᴋ", "tokensettings")]])
        )

    new_value = int(raw)

    # Sanity guard: min_time should never be >= session_timeout, or every
    # verification would look either like a bypass or already expired.
    if key in ("verify_min_time", "verify_session_timeout"):
        settings = await client.mongodb.get_token_settings()
        min_time = new_value if key == "verify_min_time" else settings["verify_min_time"]
        timeout = new_value if key == "verify_session_timeout" else settings["verify_session_timeout"]
        if min_time >= timeout:
            return await res.reply(
                "<blockquote>✗ ɪɴᴠᴀʟɪᴅ! ᴀɴᴛɪ-ʙʏᴘᴀss ᴍɪɴ ᴛɪᴍᴇ ᴍᴜsᴛ ʙᴇ ʟᴏᴡᴇʀ ᴛʜᴀɴ ᴛʜᴇ ʟɪɴᴋ ᴇxᴘɪʀʏ ᴛɪᴍᴇ. ɴᴏᴛʜɪɴɢ ᴡᴀs ᴄʜᴀɴɢᴇᴅ.</blockquote>",
                quote=True,
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("◂ ʙᴀᴄᴋ", "tokensettings")]])
            )

    await client.mongodb.set_token_setting(key, new_value)
    await res.reply(
        f"<blockquote>✓ **{LABELS[key]}** ᴜᴘᴅᴀᴛᴇᴅ ᴛᴏ `{new_value}`!</blockquote>",
        quote=True,
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("◂ ʙᴀᴄᴋ", "tokensettings")]])
    )


#===============================================================#
# /checktoken — inspect a user's live verification token/session
#===============================================================#

@Client.on_message(filters.command("checktoken") & filters.private)
async def checktoken_command(client: Client, message: Message):
    if message.from_user.id not in client.admins:
        return await message.reply(client.reply_text)

    if len(message.command) != 2 or not message.command[1].isdigit():
        return await message.reply(
            "<blockquote>⚠️ ᴜsᴀɢᴇ: /checktoken user_id</blockquote>"
        )

    target_id = int(message.command[1])

    if not await client.mongodb.present_user(target_id):
        return await message.reply("<blockquote>✗ ᴛʜɪs ᴜsᴇʀ ʜᴀs ɴᴇᴠᴇʀ sᴛᴀʀᴛᴇᴅ ᴛʜᴇ ʙᴏᴛ.</blockquote>")

    session, payload, verify_time = await client.mongodb.get_verify_data(target_id)
    credits = await client.mongodb.get_credits(target_id)
    used = await client.mongodb.get_used_credits(target_id)
    is_pro = await client.mongodb.is_pro(target_id)

    if not session:
        token_status = "<blockquote>✗ ɴᴏ ᴀᴄᴛɪᴠᴇ ᴠᴇʀɪꜰɪᴄᴀᴛɪᴏɴ ᴛᴏᴋᴇɴ ꜰᴏʀ ᴛʜɪs ᴜsᴇʀ.</blockquote>"
    else:
        settings = await client.mongodb.get_token_settings()
        elapsed = int(time.time()) - (verify_time or 0)
        remaining = settings["verify_session_timeout"] - elapsed
        if remaining <= 0:
            state = "✗ ᴇxᴘɪʀᴇᴅ (ᴡɪʟʟ ʙᴇ ʀᴇᴊᴇᴄᴛᴇᴅ ᴏɴ ɴᴇxᴛ ᴄʟɪᴄᴋ)"
        elif elapsed < settings["verify_min_time"]:
            state = f"⧗ ᴛᴏᴏ ᴇᴀʀʟʏ — {settings['verify_min_time'] - elapsed}s ʟᴇꜰᴛ ʙᴇꜰᴏʀᴇ ɪᴛ ᴡᴏɴ'ᴛ ʙᴇ ꜰʟᴀɢɢᴇᴅ ᴀs ᴀ ʙʏᴘᴀss"
        else:
            state = f"✓ ᴠᴀʟɪᴅ — {remaining}s ʟᴇꜰᴛ ʙᴇꜰᴏʀᴇ ᴇxᴘɪʀʏ"
        token_status = (
            "<blockquote>"
            f"›› **sᴛᴀᴛᴜs:** {state}\n"
            f"›› **ᴘᴀʏʟᴏᴀᴅ:** `{payload}`\n"
            f"›› **ᴄʀᴇᴀᴛᴇᴅ:** {elapsed}s ᴀɢᴏ"
            "</blockquote>"
        )

    text = (
        f"<blockquote>🪙 ᴛᴏᴋᴇɴ ɪɴꜰᴏ ꜰᴏʀ <code>{target_id}</code></blockquote>\n"
        f"{token_status}\n"
        f"<blockquote>›› **ᴄʀᴇᴅɪᴛs:** `{credits}` (ᴜsᴇᴅ: `{used}`)\n"
        f"›› **ᴘʀᴇᴍɪᴜᴍ:** `{'✓ ʏᴇs' if is_pro else '✗ ɴᴏ'}`</blockquote>"
    )
    await message.reply(text, quote=True)
