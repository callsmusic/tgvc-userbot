# Telegram Voice Chat UserBot

A Telegram UserBot to Play Audio in Voice Chats.

This is also the source code of the userbot which is being used for playing DJ/Live Sets music in [VC DJ/Live Sets](https://t.me/VCSets) group.

Made with [tgcalls](https://github.com/MarshalX/tgcalls) and [Pyrogram Smart Plugin](https://docs.pyrogram.org/topics/smart-plugins)

## Requirements

- Python 3.6 or higher
- A [Telegram API key](https://docs.pyrogram.org/intro/quickstart#enjoy-the-api) and a Telegram account
- FFmpeg

## Run

1. prepare python and pip, optionally use `virtualenv`, a `Dockerfile` is
   provided in the repo as well
2. `pip install -U -r requirements.txt` to install the requirements
3. Create a new `config.ini` file, copy-paste the following and replace the
   values with your own. Exclude or include plugins to fit your needs.
   Create `config.py` and add constants that are specified in module
   docstrings of enabled plugins.
   ```
   [pyrogram]
   api_id = 1234567
   api_hash = 0123456789abcdef0123456789abcdef

   [plugins]
   root = plugins
   include = vc.player
   ```
4. Run with `python userbot.py`
5. Stop with <kbd>CTRL+C</kbd>

# License

AGPL-3.0-or-later
