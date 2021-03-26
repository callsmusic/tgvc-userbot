from os import environ
import logging
from pyrogram import Client, idle

api_id = int(environ["API_ID"])
api_hash = environ["API_HASH"]
session_name = environ["SESSION_NAME"]

plugins = dict(
    root="plugins",
    include=[
        "vc.player",
        "ping",
        "sysinfo"
    ]
)
logging.basicConfig(level=logging.INFO)
AnonyBot = Client('Anonymous-Sender',
                  api_id=var.API_ID,
                  api_hash=var.API_HASH,
                  bot_token=var.BOT_TOKEN,
                  plugins=dict(root="plugins"))

AnonyBot.run()
# 
print('>>> USERBOT STARTED')
