# Telegram Voice Chat UserBot

A Telegram UserBot to Play Audio in Voice Chats.

This is also the source code of the userbot which is being used for playing
DJ/Live Sets music in [VC DJ/Live Sets](https://t.me/VCSets) group.

Made with [tgcalls](https://github.com/MarshalX/tgcalls)
and [Pyrogram Smart Plugin](https://docs.pyrogram.org/topics/smart-plugins)

It's recommended to use [tgmusicbot](https://github.com/callsmusic/tgmusicbot)
along with this userbot.

## Deploy to Heroku

[![Deploy](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy?template=https://github.com/callsmusic/tgvc-userbot/tree/smart-plugins)

- Generate Pyrogram session string by
  running [generate-pyrogram-session-string.py](generate-pyrogram-session-string.py)
  by yourself or
  through [Replit](https://replit.com/@dashezup/generate-pyrogram-session-string)
- Enable the worker after deploy the project to Heroku
- send `!ping`, `!uptime`, or `!sysinfo` from userbot account itself or its
  contacts to check if the userbot is running
- Send `!join` to a voice chat enabled group chat from userbot account itself
  or its contacts
- Reply to an audio with `/play` to start playing it in the voice chat, every
  member of the group can use the `!play` and other common commands now,
  check `!help` for more commands

Check [smart-plugins](https://github.com/callsmusic/tgvc-userbot/tree/smart-plugins)
branch If you want to use `radio` or `recorder` plugin.

## Introduction

**Features**

- Playlist, queue
- Loop one track when there is only one track in the playlist
- Automatically downloads audio for the first two tracks in the playlist to
  ensure smooth playing
- Automatically pin the current playing track
- Show current playing position of the audio

**How to Use**

You can't play and listen in the same voice chat at the same time, it's
recommended to run the userbot with your alt account and control the userbot
with your main account by adding your main account as a contact of the alt
account.

1. Start the userbot, try `!ping`, `!uptime` or `!sysinfo` command to check if
   the bot was running.
2. send `!join` to a voice chat enabled group chat from userbot account itself
   or its contacts, be sure to make the userbot account as group admin and give
   it at least the following permissions:
    - Delete messages
    - Manage voice chats (optional)
3. reply to an audio with `/play` to start playing it in the voice chat, every
   member of the group can use common commands such like `/play`, `/current`
   and `!help` now.
4. check `!help` for more commands

## Requirements

- Python 3.6 or higher
- One or two Telegram accounts, better to have one for the userbot and another
  one as a contact of the userbot account to control it
-
A [Telegram API key](https://docs.pyrogram.org/intro/quickstart#enjoy-the-api)
and a Telegram account
- Choose plugins you need, install dependencies which listed above and
  run `pip install -U -r requirements.txt` to install python package
  dependencies as well
- [FFmpeg](https://www.ffmpeg.org/)

## Run

Choose one of the two methods and run the userbot with
`python userbot.py`, stop with <kbd>CTRL+c</kbd>. The following example assume
that you were going to use `vc.player` and `ping` plugin, replace
`api_id`, `api_hash` to your own value.

### Method 1: use config.ini

Create a `config.ini` file

```
[pyrogram]
api_id = 1234567
api_hash = 0123456789abcdef0123456789abcdef

[plugins]
root = plugins
include =
    vc.player
    ping
    sysinfo
```

### Method 2: write your own userbot.py

Replace the file content of `userbot.py`

```
from pyrogram import Client, idle

api_id = 1234567
api_hash = "0123456789abcdef0123456789abcdef"

plugins = dict(
    root="plugins",
    include=[
        "vc.player",
        "ping"
    ]
)

app = Client("tgvc", api_id, api_hash, plugins=plugins)
app.start()
print('>>> USERBOT STARTED')
idle()
app.stop()
print('\n>>> USERBOT STOPPED')
```

# License

AGPL-3.0-or-later

```
tgvc-userbot, Telegram Voice Chat Userbot
Copyright (C) 2021  Dash Eclipse

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
```
