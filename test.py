from pyrogram import Client
import asyncio

from sqlalchemy import select

from config import API_ID, API_HASH
from db.models import Session, Accaunt
from bot import bot as botsender

# Настройки сессии (можно изменить название)
SESSION_NAME = "my_userbot"


async def main():
    app = Client(
        name=SESSION_NAME,
        api_id=API_ID,
        api_hash=API_HASH,
        device_model="UserBot",
        system_version="1.0",
        app_version="1.0.0"
    )
    tg_id = 7715104509
    async with app:
        async for dialog in app.get_dialogs():
            print(1)
            if dialog.chat.id == tg_id:
                print(dialog.chat.username)
                print(dialog.chat.id)



if __name__ == '__main__':
    asyncio.run(main())