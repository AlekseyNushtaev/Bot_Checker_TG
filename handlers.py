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

    if message.from_user.id in ADMIN_IDS:
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
                await message.answer("Пароль верный! Вы активированы.")
            else:
                await message.answer("Неверный пароль. Попробуйте еще раз.")


@router.message(F.text == "📥 Добавить аккаунт", F.from_user.id.in_(ADMIN_IDS))
async def add_acc_start(message: Message, state: FSMContext):
    await message.answer(
        "Введите юзернейм бота (начинается с @)",
        reply_markup=ReplyKeyboardRemove()
    )
    await state.set_state(AdminStates.waiting_for_account_identifier)


@router.message(AdminStates.waiting_for_account_identifier, F.from_user.id.in_(ADMIN_IDS))
async def add_acc_finish(message: Message, state: FSMContext):
    try:
        identifier = message.text
        if identifier.startswith('@'):
            async with Session() as session:
                accaunt = Accaunt(tg_username=identifier, account_type='bot')
                session.add(accaunt)
                await session.commit()
                await message.answer(f"Бот {identifier} добавлен", reply_markup=get_admin_keyboard())
        else:
            await message.answer("Имя бота должно начинается с @", reply_markup=get_admin_keyboard())

    except IntegrityError:
        await message.answer("Этот аккаунт уже существует в базе", reply_markup=get_admin_keyboard())
    finally:
        await state.clear()


@router.message(F.text == "🗑️ Удалить аккаунт", F.from_user.id.in_(ADMIN_IDS))
async def remove_acc_start(message: Message, state: FSMContext):
    await message.answer(
        "Введите юзернейм бота для удаления (начинается с @).",
        reply_markup=ReplyKeyboardRemove()
    )
    await state.set_state(AdminStates.waiting_for_account_remove)


@router.message(AdminStates.waiting_for_account_remove, F.from_user.id.in_(ADMIN_IDS))
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
        else:
            await message.answer("Имя бота должно начинается с @", reply_markup=get_admin_keyboard())
    except:
        pass
    finally:
        await state.clear()


@router.message(F.text == "📊 Все аккаунты", F.from_user.id.in_(ADMIN_IDS))
async def all_accs(message: Message, state: FSMContext):
    async with Session() as session:
        result = await session.execute(select(Accaunt))
        accounts = result.scalars().all()
        mes_ = []
        for account in accounts:
            if account.account_type == 'bot':
                text = f'Бот {account.tg_username}'
                mes_.append(text)

    await message.answer('\n'.join(mes_), reply_markup=get_admin_keyboard())

