# Telegram Voice Chat UserBot

A Telegram UserBot to Play Audio in Voice Chats.

This is also the source code of the userbot which is being used for playing
DJ/Live Sets music in [VC DJ/Live Sets](https://t.me/VCSets) group.

Made with [tgcalls](https://github.com/MarshalX/tgcalls)
and [Pyrogram Smart Plugin](https://docs.pyrogram.org/topics/smart-plugins)

It's recommended to use [tgmusicbot](https://github.com/callsmusic/tgmusicbot)
along with this userbot.

## Deploy to Heroku

[![Deploy](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy?template=https://github.com/callsmusic/tgvc-userbot/tree/dev)

- Generate Pyrogram session string by
  running [generate-pyrogram-session-string.py](generate-pyrogram-session-string.py)
  by yourself or
  through [Replit](https://replit.com/@dashezup/generate-pyrogram-session-string)
- Enable the worker after deploy the project to Heroku

Change the value of `PLUGIN` variable if you want to try other voice chat
plugins.

## Deploy to Railway

[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/new/template?template=https%3A%2F%2Fgithub.com%2Fcallsmusic%2Ftgvc-userbot&envs=API_ID%2CAPI_HASH%2CSESSION_NAME%2CPLUGIN&API_IDDesc=api_id+part+of+your+Telegram+API+Key+from+my.telegram.org%2Fapps&API_HASHDesc=api_hash+part+of+your+Telegram+API+Key+from+my.telegram.org%2Fapps&SESSION_NAMEDesc=Session+string%2C+read+the+README+to+learn+how+to+export+it+with+Pyrogram&PLUGINDesc=Voice+Chat+Smart+Plugin+to+enable%2C+must+be+one+of%3A+player%2Fchannel%2Frecorder%2Fradio&PLUGINDefault=player)

- Generate Pyrogram session string by running [generate-pyrogram-session-string.py](generate-pyrogram-session-string.py) by yourself or through [Replit](https://replit.com/@dashezup/generate-pyrogram-session-string)

Change the value of `PLUGIN` variable if you want to try other voice chat
plugins.

## Introduction

**Features**

- Playlist, queue
- Loop one track when there is only one track in the playlist
- Automatically downloads audio for the first two tracks in the playlist to
  ensure smooth playing
- Automatically pin the current playing track
- Show current playing position of the audio

**Plugin**: vc.`player`

Commands only works in groups, userbot account itself and contacts can use any
commands, all members can use common commands after the userbot join the VC

1. Start the userbot, try `!ping`, `!uptime` or `!sysinfo` command to check if
   the bot was running
2. send `!join` to a voice chat enabled group chat from userbot account itself
   or its contacts, be sure to make the userbot account as group admin and give
   it at least the following permissions:
    - Delete messages
    - Manage voice chats (optional)
3. reply to an audio with `/play` to start playing it in the voice chat, every
   member of the group can use common commands such like `/play`, `/current`
   and `!help` now.
4. check `!help` for more commands

**Plugin**: vc.`channel`

Almost same as `player` plugin but commands only works in Saved Messages,
`!join` takes arguments to be able to join group or channel voice chats.

**Plugin**: `ping` and `sysinfo`

Commands only works for userbot account itself and its contacts.

## Requirements

- Python 3.6 or higher
- A
  [Telegram API key](https://docs.pyrogram.org/intro/quickstart#enjoy-the-api)
  and a Telegram account
- Choose plugins you need, install dependencies which listed above and run
  `pip install -U -r requirements.txt` to install Python package dependencies
  as well
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
        "ping",
        "sysinfo"
    ]
)

app = Client("tgvc", api_id, api_hash, plugins=plugins)
app.start()
print('>>> USERBOT STARTED')
idle()
app.stop()
print('\n>>> USERBOT STOPPED')
```

## Notes

- Read module docstrings of [plugins/](plugins) you are going to use at the
  beginning of the file for extra notes

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
