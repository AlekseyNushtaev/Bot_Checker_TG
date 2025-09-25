import asyncio
from sqlalchemy import select

from bot import bot
from config import ADMIN_IDS
from db.models import Session, Accaunt, User
from handlers import get_admin_keyboard


async def account_checker():
    while True:
        await asyncio.sleep(5)
        print('новый цикл')
        async with Session() as session:
            result = await session.execute(select(Accaunt).where(Accaunt.is_deleted == True))
            accounts = result.scalars().all()
            text = []
            print(len(accounts))
            for account in accounts:
                print(account.is_deleted)
                text_ = f"Бот {account.tg_username} не существует"
                text.append(text_)
            msg = '\n'.join(text)
            for admin_id in ADMIN_IDS:
                try:
                    await bot.send_message(admin_id, msg, reply_markup=get_admin_keyboard())
                except:
                    pass

            result = await session.execute(select(User).where(User.is_active == True))
            active_users = result.scalars().all()

            for user in active_users:
                try:
                    await bot.send_message(user.user_id, msg)
                except:
                    pass

        await asyncio.sleep(1000)  # Ожидание до следующего цикла