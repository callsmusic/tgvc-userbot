from pyrogram import Client, idle

api_id = 7097917
api_hash = "f48294d395134512a2963d4315d21296"

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
