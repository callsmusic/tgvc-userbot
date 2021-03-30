import os
import socket
import asyncio
from pyrogram import Client, filters, emoji
from pyrogram.types import Message

DELETE_DELAY = 8


@Client.on_message(filters.chat("VCSets")
                   & filters.text
                   & ~filters.edited
                   & filters.regex('^/paste$'))
async def upload_paste_to_ezup_pastebin(_, m: Message):
    reply = m.reply_to_message
    if not reply:
        return
    paste_content = await _get_paste_content(reply)
    if not paste_content:
        response = await m.reply_text(f"{emoji.ROBOT} ezpaste: invalid")
        await _delay_delete_messages([response, m])
        return
    url = await _netcat('ezup.dev', 9999, paste_content)
    await reply.reply_text(f"{emoji.ROBOT} ezpaste: {url}")
    await m.delete()


async def _get_paste_content(m: Message):
    if m.text:
        return m.text
    elif m.document:
        if m.document.file_size > 4096 \
                or m.document.mime_type.split('/')[0] != 'text':
            return None
        filename = await m.download()
        with open(filename) as f:
            return f.read()
        os.remove(filename)
    else:
        return None


async def _delay_delete_messages(messages: list):
    await asyncio.sleep(DELETE_DELAY)
    for m in messages:
        await m.delete()


async def _netcat(host, port, content):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((host, int(port)))
    s.sendall(content.encode())
    s.shutdown(socket.SHUT_WR)
    while True:
        data = s.recv(4096).decode('utf-8').strip('\n\x00')
        if not data:
            break
        return data
    s.close()
