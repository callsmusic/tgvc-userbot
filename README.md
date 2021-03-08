# Telegram Voice Chat UserBot

A Telegram UserBot to Play Audio in Voice Chats.

This is also the source code of the userbot which is being used for playing DJ/Live Sets music in [VC DJ/Live Sets](https://t.me/VCSets) group.

Made with [tgcalls](https://github.com/MarshalX/tgcalls) and [Pyrogram Smart Plugin](https://docs.pyrogram.org/topics/smart-plugins)

|              | vc.player               | vc.recorder                   | ping            |
|--------------|-------------------------|-------------------------------|-----------------|
| Description  | Voice Chat Audio Player | Voice Chat Audio Recorder     | ping and uptime |
| Dependencies | ffmpeg                  | ffmpeg, opus-tools, bpm-tools |                 |
| Conflict     | vc.recorder             | vc.player                     |                 |

## Deploy to Heroku

[![Deploy](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy?template=https://github.com/dashezup/tgvc-userbot)

- Session string can be exported [by using Pyrogram](https://github.com/ColinShark/Pyrogram-Snippets/blob/master/Snippets/generate_session.py)
- Go to "Resources - worker" and enable the worker on Heroku dashboard after deploy the project
- Reply to an audio with `!play` in a Voice Chat enabled Telegram group to start using it

## Requirements

- Python 3.6 or higher
- A [Telegram API key](https://docs.pyrogram.org/intro/quickstart#enjoy-the-api) and a Telegram account
- Choose plugins you need, install dependencies which listed above and run `pip install -U -r requirements.txt` to install python package dependencies as well

## Run

Choose one of the two methods and run the userbot with
`python userbot.py`, stop with <kbd>CTRL+c</kbd>. The following example
assume that you were going to use `vc.player` and `ping` plugin, replace
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

## Notes

- Read module docstrings of [plugins/](plugins) you are going to use at
  the beginning of the file for extra notes
- Commands are available to the UserBot account itself only to simplify
  the source code, it's easy for you to fork the project and make
  modification to fit your needs

# License

AGPL-3.0-or-later
