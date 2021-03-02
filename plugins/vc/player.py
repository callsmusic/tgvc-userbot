"""Play and Control Audio playing in Telegram Voice Chat

This Pyrogram Smart Plugin requires this constant to be set:

# ../config.py
INPUT_FILENAME = '/bot/downloads/input.raw'

After start the bot, use the userbot account to send !join_vc command
in a group where voice chat is already started, after it join the voice
chat, reply an audio in the group with !play to play it in the current
voice chat.

Commands:
!join_vc   join the current voice chat
!play      reply to an audio to play it in current voice chat
!list_vc   list joined voice chats
!leave_vc  leave the current voice chat
!stop      stop
!replay    play the track from beginning
!mute      mute the userbot in the current voice chat
!unmute    unmute the userbot in the current voice chat

"""
import os
import ffmpeg
from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.raw.functions.channels import GetFullChannel
from pyrogram.raw.functions.phone import LeaveGroupCall
from pytgcalls import GroupCall
from config import INPUT_FILENAME

VOICE_CHATS = {}


@Client.on_message(filters.text
                   & filters.outgoing
                   & ~filters.edited
                   & filters.regex("^!join_vc$"))
async def join_voice_chat(client, message: Message):
    if message.chat.id in VOICE_CHATS:
        await message.edit_text("`[userbot]`: already joined")
        return
    chat_id = message.chat.id
    group_call = GroupCall(client, INPUT_FILENAME)
    await group_call.start(chat_id)
    VOICE_CHATS[chat_id] = group_call
    await message.edit_text("`[userbot]`: Joined Voice Chat")


@Client.on_message(filters.text
                   & filters.outgoing
                   & ~filters.edited
                   & filters.regex("^!leave_vc$"))
async def leave_voice_chat(client, message: Message):
    chat_id = message.chat.id
    await leave_group_call(client, chat_id)
    VOICE_CHATS.pop(chat_id, None)
    await message.edit_text("`[userbot]`: Left Voice Chat")


async def leave_group_call(client, chat_id):
    peer = await client.resolve_peer(chat_id)
    full_chat = await client.send(GetFullChannel(channel=peer))
    chat_call = full_chat.full_chat.call
    await client.send(LeaveGroupCall(call=chat_call, source=0))


@Client.on_message(filters.text
                   & filters.outgoing
                   & ~filters.edited
                   & filters.regex("^!list_vc$"))
async def list_voice_chat(client, message: Message):
    if not VOICE_CHATS:
        await message.edit_text("`[userbot]`: Didn't join any voice chat yet")
        return
    vc_chats = ""
    for chat_id in VOICE_CHATS:
        chat = await client.get_chat(chat_id)
        vc_chats += f"- **{chat.title}**\n"
    await message.edit_text(f"`[userbot]`: currently joined:\n{vc_chats}")


@Client.on_message(filters.text
                   & filters.outgoing
                   & ~filters.edited
                   & filters.regex("^!stop$"))
async def stop_playing(_, message: Message):
    chat_id = message.chat.id
    group_call = VOICE_CHATS[chat_id]
    group_call.stop_playout()
    await message.edit_text("`[userbot]`: Stopped Playing")


@Client.on_message(filters.text
                   & filters.outgoing
                   & ~filters.edited
                   & filters.regex("^!replay$"))
async def restart_playing(_, message: Message):
    chat_id = message.chat.id
    group_call = VOICE_CHATS[chat_id]
    group_call.input_filename = INPUT_FILENAME
    group_call.restart_playout()
    await message.edit_text("`[userbot]`: Playing from beginning...")


@Client.on_message(filters.text
                   & filters.outgoing
                   & ~filters.edited
                   & filters.regex("^!play$"))
async def play_track(_, message: Message):
    if not message.reply_to_message or not message.reply_to_message.audio:
        return
    if not VOICE_CHATS or message.chat.id not in VOICE_CHATS:
        await message.edit_text("`[userbot]`: not joined the current VC yet")
        return
    audio = message.reply_to_message.audio
    await message.edit_text("`[userbot]`: **1/3** Downloading audio file...")
    audio_original = await message.reply_to_message.download()
    await message.edit_text("`[userbot]`: **2/3** Transcoding...")
    ffmpeg.input(audio_original).output(
        INPUT_FILENAME,
        format='s16le',
        acodec='pcm_s16le',
        ac=2, ar='48k'
    ).overwrite_output().run()
    await message.edit_text(f"`[userbot]`: Playing **{audio.title}**...")
    os.remove(audio_original)


@Client.on_message(filters.text
                   & filters.outgoing
                   & ~filters.edited
                   & filters.regex("^!mute$"))
async def mute(_, message: Message):
    chat_id = message.chat.id
    group_call = VOICE_CHATS[chat_id]
    group_call.set_is_mute(True)
    await message.edit_text("`[userbot]`: Muted")


@Client.on_message(filters.text
                   & filters.outgoing
                   & ~filters.edited
                   & filters.regex("^!unmute$"))
async def unmute(_, message: Message):
    chat_id = message.chat.id
    group_call = VOICE_CHATS[chat_id]
    group_call.set_is_mute(False)
    await message.edit_text("`[userbot]`: Unmuted")
