"""
Настройка и инициализация клиента бота.

Этот модуль содержит код для конфигурации и инициализации клиента бота, использующего библиотеку Pyrogram.

Параметры:
    api_id (int): Идентификатор API, предоставленный Telegram.
    api_hash (str): Секретный хеш, предоставленный Telegram.
    bot_token (str): Токен бота Telegram.
    client_bot (Client): Объект клиента бота Pyrogram.

"""

from pyrogram import Client
from app import config

api_id = config.API_ID
api_hash = config.API_HASH
bot_token = config.TELEGRAM_BOT_TOKEN
client_bot = Client(
    name=f"{config.CLIENT_SESSION_PATH}/pyrogram_bot",
    api_id=api_id, api_hash=api_hash,
    bot_token=bot_token
)
