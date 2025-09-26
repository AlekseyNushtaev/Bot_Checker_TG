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
    async with app:
        while True:
            await botsender.send_message(1012882762, 'новый цикл юзербота')
            async with Session() as session:
                result = await session.execute(select(Accaunt))
                accounts = result.scalars().all()
                for account in accounts:
                    if account.account_type == 'bot':
                        try:
                            bot = await app.get_chat(account.tg_username)
                            account.is_deleted = False
                            account.tg_id = bot.id
                            print(bot.username)
                        except Exception as e:
                            print(e)
                            account.is_deleted = True
                    elif account.account_type == 'chanel':
                        try:
                            account.is_deleted = True
                            async for dialog in app.get_dialogs():
                                if dialog.chat.id == account.tg_id:
                                    account.is_deleted = False
                                    account.title = dialog.chat.title
                                    break
                        except:
                            print(e)
                            account.is_deleted = True
                    await session.commit()
                    await asyncio.sleep(2)
            await asyncio.sleep(60)


if __name__ == '__main__':
    asyncio.run(main())
