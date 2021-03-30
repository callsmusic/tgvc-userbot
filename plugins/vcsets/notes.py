"""Pyrogram Smart Plugin for notes in t.me/VCSets

Required chat permission:
- Delete messages
"""
import json
import pathlib
from pyrogram import Client, filters
from pyrogram.types import Message

response = {}
parent_path = pathlib.Path(__file__).parent.absolute()
json_file = pathlib.PurePath.joinpath(parent_path, 'notes.json')
with open(json_file) as f:
    notes = json.load(f)


@Client.on_message(
    filters.chat("VCSets")
    & filters.text
    & ~filters.edited
    & (filters.command(list(notes.keys()), prefixes="#")
       | filters.command("notes", prefixes="/"))
)
async def show_notes(_, m: Message):
    if len(m.command) != 1:
        return
    m_target, quote = (m.reply_to_message or m), bool(m.reply_to_message)
    m_response = await m_target.reply_text(
        notes[m.command[0]],
        quote=quote,
        disable_web_page_preview=True
    )
    await m.delete()
    key = 'list' if m.command[0] == 'notes' else 'note'
    if response.get(key) is not None:
        await response[key].delete()
    response[key] = m_response
