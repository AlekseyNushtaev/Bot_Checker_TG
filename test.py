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
    tg_id = -1003139656688
    async with app:
        await botsender.send_message(1012882762, 'новый цикл юзербота')
        try:
            bot = await app.get_chat(tg_id)
            print(bot.title)
        except Exception as e:
            print(e)



if __name__ == '__main__':
    asyncio.run(main())