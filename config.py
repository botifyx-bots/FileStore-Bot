import logging
from logging.handlers import RotatingFileHandler

# Bot Configuration
LOG_FILE_NAME = "bot.log"
PORT = '8000'
OWNER_ID = 7815384262

MSG_EFFECT = 5046509860389126442

SHORT_URL = "shrinkme.io" # shortner url 
SHORT_API = "e75f29485ddb045e6887d284f762f3daeb84f869"
SHORT_TUT = "https://t.me/ANIME_X_FLEX/19"

# Bot Configuration
SESSION = "KdramaVoid"
TOKEN = "8987193253:AAGoIdQQyConZL7Kl2fb3iZb4zkpmqEqJWY"
API_ID = "38102569"
API_HASH = "19b252f74e4584256515f52e795f431f"
WORKERS = 5

DB_URI = "mongodb+srv://ANI_OTAKU:ANI_OTAKU@cluster0.t3frstc.mongodb.net/?appName=Cluster0"
DB_NAME = "KdramaVoidBot"

FSUBS = [[-1004332291461, True, 10]] # Force Subscription Channels [channel_id, request_enabled, timer_in_minutes]
# Database Channel (Primary)
DB_CHANNEL = -1003807929416 # just put channel id dont add ""
# Multiple Database Channels (can be set via bot settings)
# DB_CHANNELS = {
#     "-1002595092736": {"name": "Primary DB", "is_primary": True, "is_active": True},
#     "-1001234567890": {"name": "Secondary DB", "is_primary": False, "is_active": True}
# }
# Auto Delete Timer (seconds)
AUTO_DEL = 300
# Admin IDs
ADMINS = [7156099919]
# Bot Settings
DISABLE_BTN = True
PROTECT = False

# Messages Configuration
MESSAGES = {
    "START": "<b>›› ʜᴇʏ!! {mention}× sᴇɴᴘᴀɪ 🎊\n</b><blockquote><b>I'ᴍ ᴀ ғɪʟᴇsʜᴀʀᴇ ʙᴏᴛ ʙᴜɪʟᴅ ᴡɪᴛʜ ʟᴏᴠᴇ .....</b></blockquote>\n<blockquote>❝ ɴᴏ ᴍᴀᴛᴛᴇʀ ʜᴏᴡ ᴅᴇᴇᴘ ᴛʜᴇ ɴɪɢʜᴛ, ɪᴛ ᴀʟᴡᴀʏꜱ ᴛᴜʀɴꜱ ᴛᴏ ᴅᴀʏ, ᴇᴠᴇɴᴛᴜᴀʟʟʏ. ᴀꜱ ʟᴏɴɢ ᴀꜱ ʏᴏᴜ ᴅᴏɴ’ᴛ ɢɪᴠᴇ ᴜᴘ, ᴛʜᴇʀᴇ ᴡɪʟʟ ᴀʟᴡᴀʏꜱ ʙᴇ ᴀ ᴘᴀᴛʜ ꜰᴏʀᴡᴀʀᴅ. ❞</blockquote>\n<blockquote>― ᴋᴇɴ ᴋᴀɴᴇᴋɪ</blockquote>",
    "FSUB": "<blockquote>›› ʜᴇʏ {mention}× sᴇɴᴘᴀɪ 🎊</blockquote>\n<blockquote><b>ʏᴏᴜʀ ғɪʟᴇ ɪs ʀᴇᴀᴅʏ ‼️ ʟᴏᴏᴋs ʟɪᴋᴇ ʏᴏᴜ ʜᴀᴠᴇɴ'ᴛ sᴜʙsᴄʀɪʙᴇᴅ ᴛᴏ ᴏᴜʀ ᴄʜᴀɴɴᴇʟs ʏᴇᴛ, sᴜʙsᴄʀɪʙᴇ ɴᴏᴡ ᴛᴏ ɢᴇᴛ ʏᴏᴜʀ ғɪʟᴇs</b></blockquote>",
    "ABOUT": "<b>›› ғᴏʀ ᴍᴏʀᴇ: <a href='https://t.me/ITsANIMEN'>Cʟɪᴄᴋ ʜᴇʀᴇ</a>\n<blockquote expandable>›› ᴜᴘᴅᴀᴛᴇs ᴄʜᴀɴɴᴇʟ: <a href='https://t.me/BotifyX_Pro_Botz'>Bᴏᴛɪғʏx ʙᴏᴛs</a> \n›› ᴏᴡɴᴇʀ: @joyboy_core\n›› ʟᴀɴɢᴜᴀɢᴇ: <a href='https://docs.python.org/3/'>Pʏᴛʜᴏɴ 3</a> \n›› ʟɪʙʀᴀʀʏ: <a href='https://docs.pyrogram.org/'>Pʏʀᴏɢʀᴀᴍ ᴠ2</a> \n›› ᴅᴀᴛᴀʙᴀsᴇ: <a href='https://www.mongodb.com/docs/'>Mᴏɴɢᴏ ᴅʙ</a> \n›› ᴅᴇᴠᴇʟᴏᴘᴇʀ: @Era_Ghost</b></blockquote>",
    "CHANNELS":"<b>›› ᴀɴɪᴍᴇ ᴄʜᴀɴɴᴇʟ: <a href='https://t.me/Void_Animes'>꧁༒ 𝙰𝚗𝚒𝚖𝚎 𝚅𝚘𝚒𝚍 ༒꧂</a>\n<blockquote expandable>›› ᴀɴɪᴍᴇ ᴇᴅɪᴛᴢ: <a href='https://t.me/Animez_Edits'>ᴀɴɪᴍᴇ'ᴢ ᴇᴅɪᴛ'ᴢ</a>\n›› ᴜᴘᴅᴀᴛᴇs ᴄʜᴀɴɴᴇʟs: <a href='https://t.me/BotifyX_Pro_Botz'>Bᴏᴛɪғʏx ʙᴏᴛs</a>\n›› ᴀɴɪᴍᴇ ᴄʜᴀᴛ: <a href='https://t.me/AnimeVoid_Gc'>https://t.me/AnimeVoid_Gc</a>\n›› ᴄᴏᴍᴍᴜɴɪᴛʏ: <a href='https://t.me/Void_Association'>༒ 𝚟𝚘𝚒𝚍 𝙰𝚜𝚜𝚘𝚌𝚒𝚊𝚝𝚒𝚘𝚗 ༒</a>\n›› ᴅᴇᴠᴇʟᴏᴘᴇʀ: @Era_Ghost</b></blockquote>",
    "REPLY": "<blockquote><b>ᴡᴛғ sʜᴜᴛᴜᴘ ᴘʟᴢ....</b></blockquote>",
    "SHORT_MSG": "<blockquote><b>✧ TOKEN EXPIRED</b></blockquote>\n<blockquote>›› ᴘʟᴇᴀsᴇ ᴠᴇʀɪғʏ ᴛᴏ ʀᴇɢᴀɪɴ ᴀᴄᴄᴇss ᴛᴏ ᴛʜᴇ ғɪʟᴇs\n›› ᴠᴀʟɪᴅ ᴄʀᴇᴅɪᴛs: 3 ᴄʀᴇᴅɪᴛs</blockquote>\n────────────────────────\n<blockquote>›› ᴡʜᴀᴛ ɪs ᴀ ᴛᴏᴋᴇɴ?</blockquote>\n<blockquote>≡  ᴇᴀᴄʜ ᴀᴅ ʙʏᴘᴀss ʀᴇᴡᴀʀᴅ ʏᴏᴜ ᴡɪᴛʜ 3 ᴄʀᴇᴅɪᴛs.ᴏɴᴇ ᴄʀᴇᴅɪᴛ ɪs ᴄᴏɴsᴜᴍᴇᴅ ᴘᴇʀ ғɪʟᴇ/ʟɪɴᴋ ᴀᴄᴄᴇss.</blockquote>",
    "START_PHOTO": "https://i.pinimg.com/736x/e9/bd/63/e9bd634633c73b65b6da4acd5e4f118c.jpg",
    "FSUB_PHOTO": "https://i.pinimg.com/1200x/89/ce/8b/89ce8be141c52feb40cde2df5825ce18.jpg",
    "SHORT_PIC": "https://ibb.co/FbxLPxrq",
    "SHORT": "https://i.pinimg.com/736x/27/c4/7c/27c47c72cbc7bfef7919533274e15c37.jpg",
    "SHORT_VERIFY": "https://ibb.co/yFyv12bD",
    "PREMIUM_PLANS_PIC": "https://ibb.co/H9fpH1R",
    "QR_PAYMENT_PIC": "https://ibb.co/kVPDT5cP"
}

def LOGGER(name: str, client_name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    formatter = logging.Formatter(
        f"[%(asctime)s - %(levelname)s] - {client_name} - %(name)s - %(message)s",
        datefmt='%d-%b-%y %H:%M:%S'
    )
    file_handler = RotatingFileHandler(LOG_FILE_NAME, maxBytes=50_000_000, backupCount=10)
    file_handler.setFormatter(formatter)
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    logger.setLevel(logging.INFO)
    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)

    return logger
