from aiogram import Router, F
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from sqlalchemy import select, delete
from sqlalchemy.exc import IntegrityError

from db.models import Session, User, Accaunt
from config import ADMIN_IDS, USER_PASS

router = Router()


async def get_active_users():
    users = []
    async with Session() as session:
        result = await session.execute(select(User).where(User.is_active == True))
        active_users = result.scalars().all()

        for user in active_users:
            users.append(user.user_id)

    for admin_id in ADMIN_IDS:
        users.append(admin_id)
    return users



# Клавиатура для администраторов
def get_admin_keyboard():
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📥 Добавить аккаунт"), KeyboardButton(text="🗑️ Удалить аккаунт")],
            [KeyboardButton(text="📊 Все аккаунты")]
        ],
        resize_keyboard=True
    )
    return keyboard


# Состояния FSM
class AdminStates(StatesGroup):
    waiting_for_account_identifier = State()
    waiting_for_account_remove = State()


@router.message(Command("start"))
async def start_command(message: Message, state: FSMContext):
    # Сброс любых активных состояний
    await state.clear()
    users = await get_active_users()
    if message.from_user.id in users:
        # Администраторы получают специальную клавиатуру
        await message.answer(
            "Добро пожаловать, администратор!",
            reply_markup=get_admin_keyboard()
        )
    else:
        # Обычные пользователи
        async with Session() as session:
            result = await session.execute(
                select(User).where(User.user_id == message.from_user.id)
            )
            user = result.scalar_one_or_none()

            if not user:
                user = User(user_id=message.from_user.id)
                session.add(user)
                await session.commit()

            if user.is_active:
                await message.answer("Вы уже активированы!")
            else:
                await message.answer("Введите пароль для активации:")


@router.message(F.text == "📥 Добавить аккаунт")
async def add_acc_start(message: Message, state: FSMContext):
    users = await get_active_users()
    if message.from_user.id not in users:
        return
    await message.answer(
        "Введите на выбор:\n"
        "1. Юзернейм бота (начинается с @)\n"
        "2. ID канала (начинается с -100, юзербот должен быть в канале)\n"
        "3. ID аккаунта (все цифры, положительное число)",
        reply_markup=ReplyKeyboardRemove()
    )
    await state.set_state(AdminStates.waiting_for_account_identifier)


@router.message(AdminStates.waiting_for_account_identifier)
async def add_acc_finish(message: Message, state: FSMContext):
    try:
        identifier = message.text
        if identifier.startswith('@'):
            async with Session() as session:
                accaunt = Accaunt(tg_username=identifier, account_type='bot')
                session.add(accaunt)
                await session.commit()
                await message.answer(f"Бот {identifier} добавлен", reply_markup=get_admin_keyboard())
        elif identifier.startswith('-100'):
            async with Session() as session:
                accaunt = Accaunt(tg_id=int(identifier), account_type='chanel')
                session.add(accaunt)
                await session.commit()
                await message.answer(f"Канал с id {identifier} добавлен", reply_markup=get_admin_keyboard())
        elif identifier.isdigit():
            async with Session() as session:
                accaunt = Accaunt(tg_id=int(identifier), account_type='user')
                session.add(accaunt)
                await session.commit()
                await message.answer(f"Аккаунт юзера с id {identifier} добавлен", reply_markup=get_admin_keyboard())
        else:
            await message.answer("Имя аккаунта не валидно", reply_markup=get_admin_keyboard())

    except IntegrityError:
        await message.answer("Этот аккаунт уже существует в базе", reply_markup=get_admin_keyboard())
    finally:
        await state.clear()


@router.message(F.text == "🗑️ Удалить аккаунт")
async def remove_acc_start(message: Message, state: FSMContext):
    users = await get_active_users()
    if message.from_user.id not in users:
        return
    await message.answer(
        "Введите аккаунт для удаления.",
        reply_markup=ReplyKeyboardRemove()
    )
    await state.set_state(AdminStates.waiting_for_account_remove)


@router.message(AdminStates.waiting_for_account_remove)
async def remove_acc_finish(message: Message, state: FSMContext):
    try:
        account = message.text
        if account.startswith('@'):
            async with Session() as session:
                result = await session.execute(
                    delete(Accaunt).where(Accaunt.tg_username == account)
                )

                await session.commit()

                if result.rowcount > 0:
                    await message.answer(f"Бот {account} удален из базы", reply_markup=get_admin_keyboard())
                else:
                    await message.answer(f"Бот {account} не найден в базе", reply_markup=get_admin_keyboard())
        elif account.startswith('-100'):
            async with Session() as session:
                result = await session.execute(
                    delete(Accaunt).where(Accaunt.tg_id == int(account))
                )

                await session.commit()

                if result.rowcount > 0:
                    await message.answer(f"Канал с id {account} удален из базы", reply_markup=get_admin_keyboard())
                else:
                    await message.answer(f"Канал с id {account} не найден в базе", reply_markup=get_admin_keyboard())
        elif account.isdigit():
            async with Session() as session:
                result = await session.execute(
                    delete(Accaunt).where(Accaunt.tg_id == int(account))
                )

                await session.commit()

                if result.rowcount > 0:
                    await message.answer(f"Аккаунт юзера с id {account} удален из базы", reply_markup=get_admin_keyboard())
                else:
                    await message.answer(f"Аккаунт юзера с id {account} не найден в базе", reply_markup=get_admin_keyboard())
        else:
            await message.answer("Имя аккаунта не валидно", reply_markup=get_admin_keyboard())
    except:
        pass
    finally:
        await state.clear()


@router.message(F.text == "📊 Все аккаунты")
async def all_accs(message: Message, state: FSMContext):
    users = await get_active_users()
    print(users)
    if message.from_user.id not in users:
        return
    async with Session() as session:
        result = await session.execute(select(Accaunt))
        accounts = result.scalars().all()
        mes_ = []
        for account in accounts:
            if account.account_type == 'bot':
                text = f'Бот {account.tg_username}'
                mes_.append(text)
            elif account.account_type == 'chanel':
                text = f'Канал c id {account.tg_id} {account.title}'
                mes_.append(text)
            elif account.account_type == 'chanel':
                text = f'Аккаунт юзера c id {account.tg_id} {account.username}'
                mes_.append(text)
    if mes_:
        await message.answer('\n'.join(mes_), reply_markup=get_admin_keyboard())


@router.message(F.text, ~F.from_user.id.in_(ADMIN_IDS))
async def handle_password(message: Message):
    async with Session() as session:
        result = await session.execute(
            select(User).where(User.user_id == message.from_user.id)
        )
        user = result.scalar_one_or_none()

        if user and not user.is_active:
            if message.text == USER_PASS:
                user.is_active = True
                await session.commit()
                await message.answer("Пароль верный! Вы активированы.", reply_markup=get_admin_keyboard())
            else:
                await message.answer("Неверный пароль. Попробуйте еще раз.")
