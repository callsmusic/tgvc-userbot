"""!ping reply with pong
!uptime check uptime

dashezup/tgbot: plugins/ping.py
"""
from time import time
from datetime import datetime
from pyrogram import Client, filters, emoji
from pyrogram.types import Message

# DELAY_DELETE = 60
START_TIME = datetime.utcnow()
START_TIME_ISO = START_TIME.replace(microsecond=0).isoformat()
TIME_DURATION_UNITS = (
    ('week', 60 * 60 * 24 * 7),
    ('day', 60 * 60 * 24),
    ('hour', 60 * 60),
    ('min', 60),
    ('sec', 1)
)


# https://gist.github.com/borgstrom/936ca741e885a1438c374824efb038b3
def _human_time_duration(seconds):
    if seconds == 0:
        return 'inf'
    parts = []
    for unit, div in TIME_DURATION_UNITS:
        amount, seconds = divmod(int(seconds), div)
        if amount > 0:
            parts.append('{} {}{}'
                         .format(amount, unit, "" if amount == 1 else "s"))
    return ', '.join(parts)


@Client.on_message(filters.text
                   & filters.outgoing
                   & ~filters.edited
                   & filters.regex("^!ping$"))
async def ping_pong(_, message: Message):
    """reply ping with pong and delete both messages"""
    start = time()
    await message.edit_text("...")
    delta_ping = time() - start
    await update_userbot_message(
        message,
        message.text,
        f" ping: `{delta_ping * 1000:.3f} ms`"
    )


@Client.on_message(filters.text
                   & filters.outgoing
                   & ~filters.edited
                   & filters.regex("^!uptime$"))
async def get_uptime(_, message: Message):
    """/uptime Reply with readable uptime and ISO 8601 start time"""
    current_time = datetime.utcnow()
    uptime_sec = (current_time - START_TIME).total_seconds()
    uptime = _human_time_duration(int(uptime_sec))
    await update_userbot_message(
        message,
        message.text,
        f"\n- uptime: `{uptime}`\n- start time: `{START_TIME_ISO}`"
    )


async def update_userbot_message(message: Message, text_user, text_bot):
    await message.edit_text(f"{emoji.SPEECH_BALLOON} `{text_user}`\n"
                            f"{emoji.ROBOT}{text_bot}")
