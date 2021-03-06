"""Record Audio from Telegram Voice Chat

Dependencies:
- ffmpeg
- opus-tools
- bpm-tools

Start the bot, go to the group where have the voice chat started and
you want to record audio from, record with !record command

Send the command as a reply to another message to record longer audio
"""
import os
from pathlib import Path
import asyncio
import subprocess
from datetime import datetime
from pyrogram import Client, filters, emoji
from pyrogram.types import Message
from pyrogram.methods.messages.download_media import DEFAULT_DOWNLOAD_DIR
from pytgcalls import GroupCall
import ffmpeg

VOICE_CHATS = {}


@Client.on_message(filters.text
                   & filters.outgoing
                   & ~filters.edited
                   & filters.regex("^!join_vc$"))
async def join_voice_chat(client, message: Message):
    input_filename = os.path.join(client.workdir, DEFAULT_DOWNLOAD_DIR,
                                  "input.raw")
    if message.chat.id in VOICE_CHATS:
        await update_userbot_message(message, message.text, " Already joined")
        return
    chat_id = message.chat.id
    group_call = GroupCall(client, input_filename)
    await group_call.start(chat_id, False)
    VOICE_CHATS[chat_id] = group_call
    await update_userbot_message(
        message,
        message.text,
        " Joined the Voice Chat"
    )


@Client.on_message(filters.text
                   & filters.outgoing
                   & ~filters.edited
                   & filters.regex("^!leave_vc$"))
async def leave_voice_chat(client, message: Message):
    chat_id = message.chat.id
    group_call = VOICE_CHATS[chat_id]
    await group_call.stop()
    VOICE_CHATS.pop(chat_id, None)
    await update_userbot_message(message, message.text, " Left the Voice Chat")


@Client.on_message(filters.text
                   & filters.outgoing
                   & ~filters.edited
                   & filters.regex("^!list_vc$"))
async def list_voice_chat(client, message: Message):
    if not VOICE_CHATS:
        await update_userbot_message(
            message,
            message.text,
            " Didn't join any voice chat yet"
        )
        return
    vc_chats = ""
    for chat_id in VOICE_CHATS:
        chat = await client.get_chat(chat_id)
        vc_chats += f"- **{chat.title}**\n"
    await update_userbot_message(
        message,
        message.text,
        f" Currently joined:\n{vc_chats}"
    )


@Client.on_message(filters.text
                   & filters.outgoing
                   & ~filters.edited
                   & filters.command("record", prefixes="!"))
async def record_audio(client, message: Message):
    download_dir = os.path.join(client.workdir, DEFAULT_DOWNLOAD_DIR)
    Path(download_dir).mkdir(parents=True, exist_ok=True)
    record_raw = os.path.join(download_dir, "output.raw")
    if message.reply_to_message:
        duration = 60
    else:
        duration = 15
    chat = message.chat
    if not VOICE_CHATS or chat.id not in VOICE_CHATS:
        group_call = GroupCall(client)
        await group_call.start(chat.id, False)
        VOICE_CHATS[chat.id] = group_call
        status = (
            "\n- Joined the Voice Chat, send the command again to record"
        )
        await update_userbot_message(message, message.text, status)
        return
    status = ("\n- recording...")
    await update_userbot_message(message, message.text, status)
    group_call = VOICE_CHATS[chat.id]
    group_call.output_filename = record_raw
    time_record = datetime.utcnow()
    task = asyncio.create_task(asyncio.sleep(duration))
    time_spent = 0
    while not task.done():
        await asyncio.sleep(10)
        time_spent += 10
        await update_userbot_message(
            message,
            message.text,
            f"{status} **{time_spent}/{duration}**"
        )
    group_call.stop_output()
    status += "\n- transcoding..."
    record_opus = os.path.join(download_dir,
                               f"vcrec-{time_record.strftime('%s')}.opus")
    await update_userbot_message(message, message.text, status)
    ffmpeg.input(
        record_raw,
        format='s16le',
        acodec='pcm_s16le',
        ac=2,
        ar='48k'
    ).output(record_opus).overwrite_output().run()
    # ffmpeg -y -f s16le -ac 2 -ar 48000 -acodec pcm_s16le \
    # -i output.raw record.opus
    duration = int(float(ffmpeg.probe(record_opus)['format']['duration']))
    # sox {record_opus} -t raw -r 44100 -e float -c 1 - | bpm -f '%0.0f'
    # sox -t raw -r 48000 -e signed -b 16 -c 2 \
    # output.raw -t raw -r 44100 -e float -c 1 - | bpm -f '%0.0f'
    bpm = subprocess.getoutput(
        f"opusdec --quiet --rate 44100 --float {record_opus} - "
        "| bpm -f '%0.0f'"
    )
    probe = ffmpeg.probe(record_opus, pretty=None)
    time_record_readable = time_record.strftime('%Y-%m-%d %H:%M:%S')
    title = f"[VCREC] {time_record_readable}"
    caption = (
        f"- BPM: `{bpm}`\n"
        f"- Format: `{probe['streams'][0]['codec_name']}`\n"
        f"- Channel(s): `{str(probe['streams'][0]['channels'])}`\n"
        f"- Sampling rate: `{probe['streams'][0]['sample_rate']}`\n"
        f"- Bit rate: `{probe['format']['bit_rate']}`\n"
        f"- File size: `{probe['format']['size']}`"
    )
    status += "\n- uploading..."
    await update_userbot_message(message, message.text, status)
    thumb = await client.download_media(chat.photo.big_file_id)
    performer = (
        f"@{chat.username}"
        if chat.username
        else chat.title
    )
    await message.reply_audio(record_opus,
                              quote=False,
                              caption=caption,
                              duration=duration,
                              performer=performer,
                              title=title,
                              thumb=thumb)
    for f in [record_opus, thumb]:
        os.remove(f)
    open(record_raw, 'w').close()


async def update_userbot_message(message: Message, text_user, text_bot):
    await message.edit_text(f"{emoji.SPEECH_BALLOON} `{text_user}`\n"
                            f"{emoji.ROBOT}{text_bot}")
