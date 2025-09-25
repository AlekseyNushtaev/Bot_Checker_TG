# models.py
from sqlalchemy import Column, Integer, String, DateTime, Boolean, BigInteger, ForeignKey, Float
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncAttrs
from sqlalchemy.orm import DeclarativeBase, relationship
from datetime import datetime

# Настройка асинхронного подключения к SQLite3
DB_URL = "sqlite+aiosqlite:///db/database.db"
engine = create_async_engine(DB_URL)  # Асинхронный движок SQLAlchemy
Session = async_sessionmaker(expire_on_commit=False, bind=engine)  # Фабрика сессий


class Base(DeclarativeBase, AsyncAttrs):
    """Базовый класс для декларативных моделей с поддержкой асинхронных атрибутов"""
    pass


class Accaunt(Base):
    """Модель для хранения данных по кошелькам"""
    __tablename__ = "wallet"

    id = Column(Integer, primary_key=True)
    tg_id = Column(BigInteger, unique=True)
    tg_username = Column(String, unique=True)
    title = Column(String)
    account_type = Column(String, nullable=False)
    is_deleted = Column(Boolean, default=False)


class User(Base):
    """Модель для хранения данных пользователей"""
    __tablename__ = "user"

    id = Column(Integer, primary_key=True)
    user_id = Column(BigInteger, unique=True, nullable=False)
    is_active = Column(Boolean, default=False)
    time_add = Column(DateTime, default=datetime.utcnow)


async def create_tables():
    """Создает таблицы в базе данных"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
