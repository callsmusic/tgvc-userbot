"""Play and Control Audio playing in Telegram Voice Chat

Dependencies:
- ffmpeg

Recommended admin permissions:
- Pin messages
- Manage voice chats

How to use:
- Start the userbot
- send !join to a voice chat enabled group chat
  from userbot account itself or its contacts
- reply to an audio with /play to start playing
  it in the voice chat, every member of the group
  can use the !play command now
- check !help for more commands
"""
import os
from datetime import datetime, timedelta
from pyrogram import Client, filters, emoji
from pyrogram.types import Message
from pyrogram.methods.messages.download_media import DEFAULT_DOWNLOAD_DIR
from pyrogram.errors.exceptions.bad_request_400 import ChatAdminRequired
from pyrogram.errors.exceptions.flood_420 import FloodWait
from pytgcalls import GroupCall
import ffmpeg

group_call = GroupCall(None, path_to_log_file='')
playlist = []
track_starttime = None

USERBOT_HELP = f"""{emoji.LABEL}  **Common Commands**:
__available to group members of current voice chat__
__starts with / (slash) or ! (exclamation mark)__

/play  reply with an audio to play/queue it, or show playlist
/current  show current playing time of current track
!help  show help for commands


{emoji.LABEL}  **Admin Commands**:
__available to userbot account itself and its contacts__
__starts with ! (exclamation mark)__

`!skip` [n] ...  skip current or n where n >= 2
`!join`  join voice chat of current group
`!leave`  leave current voice chat
`!vc`  check which VC is joined
`!stop`  stop playing
`!replay`  play from the beginning
`!clean`  remove unused RAW PCM files
`!mute`  mute the VC userbot
`!unmute`  unmute the VC userbot
"""

# - Pyrogram filters

main_filter = (
    filters.group
    & filters.text
    & ~filters.edited
    & ~filters.via_bot
)
self_or_contact_filter = filters.create(
    lambda
    _,
    __,
    message:
    (message.from_user and message.from_user.is_contact) or message.outgoing
)


async def current_vc_filter(_, __, m: Message):
    if not group_call.is_connected:
        return False
    chat_id = int("-100" + str(group_call.full_chat.id))
    if m.chat.id == chat_id:
        return True
    return False

current_vc = filters.create(current_vc_filter)


def init_client_for_group_call(func):
    async def wrapper(client, message: Message):
        group_call.client = client

        return await func(client, message)

    return wrapper


# - pytgcalls handlers

@group_call.on_network_status_changed
async def network_status_changed_handler(gc: GroupCall, is_connected: bool):
    if is_connected:
        await send_text(f"{emoji.CHECK_MARK_BUTTON}  Joined the voice chat")


@group_call.on_playout_ended
async def playout_ended_handler(group_call, filename):
    await skip_current_playing()


# - Pyrogram handlers


@Client.on_message(main_filter & current_vc & filters.regex("^(\\/|!)play$"))
@init_client_for_group_call
async def play_track(client, m: Message):
    # show playlist
    if not m.reply_to_message or not m.reply_to_message.audio:
        await send_playlist()
        return
    # check already added
    m_reply = m.reply_to_message
    if playlist and playlist[-1].audio.file_unique_id \
            == m_reply.audio.file_unique_id:
        await m.reply_text(f"{emoji.ROBOT} already added")
        return
    # add to playlist
    playlist.append(m_reply)
    if len(playlist) == 1:
        m_status = await m.reply_text(
            f"{emoji.INBOX_TRAY} downloading and transcoding..."
        )
        await download_audio(playlist[0])
        group_call.input_filename = os.path.join(
            client.workdir,
            DEFAULT_DOWNLOAD_DIR,
            f"{playlist[0].audio.file_unique_id}.raw"
        )
        global track_starttime
        track_starttime = datetime.utcnow().replace(microsecond=0)
        await m_status.delete()
        print(f"- START PLAYING: {playlist[0].audio.title}")
        await pin_current_audio()
    await send_playlist()
    for track in playlist[:2]:
        await download_audio(track)


@Client.on_message(main_filter
                   & current_vc
                   & filters.regex("^(\\/|!)current$"))
@init_client_for_group_call
async def show_current_playing_time(client, m: Message):
    global track_starttime
    if not track_starttime:
        await m.reply_text(f"{emoji.PLAY_BUTTON} unknown")
        return
    utcnow = datetime.utcnow().replace(microsecond=0)
    await playlist[0].reply_text(
        f"{emoji.PLAY_BUTTON}  {utcnow - track_starttime} / "
        f"{timedelta(seconds=playlist[0].audio.duration)}",
        disable_notification=True
    )


@Client.on_message(main_filter
                   & (self_or_contact_filter | current_vc)
                   & filters.regex("^(\\/|!)help$"))
@init_client_for_group_call
async def show_help(client, m: Message):
    await m.reply_text(USERBOT_HELP)


@Client.on_message(main_filter
                   & self_or_contact_filter
                   & current_vc
                   & filters.command("skip", prefixes="!"))
@init_client_for_group_call
async def skip_track(client, m: Message):
    if len(m.command) == 1:
        await skip_current_playing()
    else:
        try:
            items = list(dict.fromkeys(m.command[1:]))
            items = [int(x) for x in items if x.isdigit()]
            items.sort(reverse=True)
            text = []
            for i in items:
                if 2 <= i <= (len(playlist) - 1):
                    audio = f"[{playlist[i].audio.title}]({playlist[i].link})"
                    playlist.pop(i)
                    text.append(f"{emoji.WASTEBASKET} {i}. **{audio}**")
                else:
                    text.append(f"{emoji.CROSS_MARK} {i}")
            await m.reply_text("\n".join(text))
            await send_playlist()
        except (ValueError, TypeError):
            await m.reply_text(f"{emoji.NO_ENTRY} invalid input",
                               disable_web_page_preview=True)


@Client.on_message(main_filter
                   & self_or_contact_filter
                   & filters.regex("^!join$"))
@init_client_for_group_call
async def join_group_call(client, m: Message):
    if group_call.is_connected \
            and m.chat.id == int("-100" + str(group_call.full_chat.id)):
        await m.reply_text(f"{emoji.ROBOT} already joined the voice chat")
        return
    await group_call.start(m.chat.id)


@Client.on_message(main_filter
                   & self_or_contact_filter
                   & current_vc
                   & filters.regex("^!leave$"))
@init_client_for_group_call
async def leave_voice_chat(client, m: Message):
    global playlist
    await group_call.stop()
    playlist = []
    await m.reply_text(f"{emoji.ROBOT} left the voice chat")


@Client.on_message(main_filter
                   & self_or_contact_filter
                   & filters.regex("^!vc$"))
@init_client_for_group_call
async def list_voice_chat(client, m: Message):
    if group_call.is_connected:
        chat_id = int("-100" + str(group_call.full_chat.id))
        chat = await client.get_chat(chat_id)
        await m.reply_text(
            f"{emoji.MUSICAL_NOTES} **currently in the voice chat**:\n"
            f"- **{chat.title}**"
        )
        return
    await m.reply_text(f"{emoji.NO_ENTRY} didn't join any voice chat yet")


@Client.on_message(main_filter
                   & self_or_contact_filter
                   & current_vc
                   & filters.regex("^!stop$"))
@init_client_for_group_call
async def stop_playing(_, m: Message):
    global track_starttime, playlist
    group_call.stop_playout()
    await m.reply_text(f"{emoji.STOP_BUTTON} stopped playing")
    track_starttime = None
    playlist = []


@Client.on_message(main_filter
                   & self_or_contact_filter
                   & current_vc
                   & filters.regex("^!replay$"))
@init_client_for_group_call
async def restart_playing(client, m: Message):
    if not playlist:
        return
    group_call.restart_playout()
    global track_starttime
    track_starttime = datetime.utcnow().replace(microsecond=0)
    await m.reply_text(
        f"{emoji.COUNTERCLOCKWISE_ARROWS_BUTTON}  "
        "playing from the beginning..."
    )


@Client.on_message(main_filter
                   & self_or_contact_filter
                   & current_vc
                   & filters.regex("^!clean$"))
async def clean_raw_pcm(client, m: Message):
    download_dir = os.path.join(client.workdir, DEFAULT_DOWNLOAD_DIR)
    all_fn = os.listdir(download_dir)
    for track in playlist[:2]:
        track_fn = f"{track.audio.file_unique_id}.raw"
        if track_fn in all_fn:
            all_fn.remove(track_fn)
    count = 0
    if all_fn:
        for fn in all_fn:
            if fn.endswith(".raw"):
                count += 1
                os.remove(os.path.join(download_dir, fn))
    await m.reply_text(f"{emoji.WASTEBASKET} cleaned {count} files")


@Client.on_message(main_filter
                   & self_or_contact_filter
                   & current_vc
                   & filters.regex("^!mute$"))
@init_client_for_group_call
async def mute(_, m: Message):
    group_call.set_is_mute(True)
    await m.reply_text(f"{emoji.MUTED_SPEAKER} muted")


@Client.on_message(main_filter
                   & self_or_contact_filter
                   & current_vc
                   & filters.regex("^!unmute$"))
@init_client_for_group_call
async def unmute(_, m: Message):
    group_call.set_is_mute(False)
    await m.reply_text(f"{emoji.SPEAKER_MEDIUM_VOLUME} unmuted")


# - Other functions


async def send_text(text):
    client = group_call.client
    chat_id = int("-100" + str(group_call.full_chat.id))
    await client.send_message(
        chat_id,
        text,
        disable_web_page_preview=True,
        disable_notification=True
    )


async def send_playlist():
    if not playlist:
        pl = f"{emoji.NO_ENTRY} empty playlist"
    else:
        if len(playlist) == 1:
            pl = f"{emoji.REPEAT_SINGLE_BUTTON} **Playlist**:\n"
        else:
            pl = f"{emoji.PLAY_BUTTON} **Playlist**:\n"
        pl += "\n".join([
            f"**{i}**. **[{x.audio.title}]({x.link})**"
            for i, x in enumerate(playlist)
        ])
    await send_text(pl)


async def skip_current_playing():
    global track_starttime
    if not playlist:
        return
    if len(playlist) == 1:
        track_starttime = datetime.utcnow().replace(microsecond=0)
        return
    client = group_call.client
    download_dir = os.path.join(client.workdir, DEFAULT_DOWNLOAD_DIR)
    group_call.input_filename = os.path.join(
        download_dir,
        f"{playlist[1].audio.file_unique_id}.raw"
    )
    track_starttime = datetime.utcnow().replace(microsecond=0)
    # remove old track from playlist
    old_track = playlist.pop(0)
    print(f"- START PLAYING: {playlist[0].audio.title}")
    await pin_current_audio()
    await send_playlist()
    os.remove(os.path.join(
        download_dir,
        f"{old_track.audio.file_unique_id}.raw")
    )
    if len(playlist) == 1:
        return
    await download_audio(playlist[1])


async def download_audio(m: Message):
    client = group_call.client
    raw_file = os.path.join(client.workdir, DEFAULT_DOWNLOAD_DIR,
                            f"{m.audio.file_unique_id}.raw")
    if not os.path.isfile(raw_file):
        original_file = await m.download()
        ffmpeg.input(original_file).output(
            raw_file,
            format='s16le',
            acodec='pcm_s16le',
            ac=2,
            ar='48k',
            loglevel='error'
        ).overwrite_output().run()
        os.remove(original_file)


async def pin_current_audio():
    client = group_call.client
    chat_id = int("-100" + str(group_call.full_chat.id))
    try:
        async for m in client.search_messages(chat_id,
                                              filter="pinned",
                                              limit=1):
            if m.audio:
                await m.unpin()
        await playlist[0].pin(True)
    except ChatAdminRequired:
        pass
    except FloodWait:
        pass
