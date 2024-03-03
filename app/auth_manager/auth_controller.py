"""
Модуль для работы с базой данных и управления пользователями.

Этот модуль содержит функции для взаимодействия с базой данных и управления пользователями.

"""

from sqlalchemy import text

from app.db.db_config import Session
from app.db.models import Users


def update_is_login(owner_telegram_id: int, is_login: bool) -> None:
    """
    Обновляет статус входа пользователя в систему.

    Параметры:
        owner_telegram_id (int): Идентификатор владельца аккаунта.
        is_login (bool): Новый статус входа пользователя.

    Возвращает:
        None

    """
    with Session() as session:
        query = text("UPDATE users SET is_login=:is_login WHERE owner_telegram_id=:owner_telegram_id")
        session.execute(query, {"owner_telegram_id": owner_telegram_id, "is_login": is_login})
        session.commit()


def update_username(owner_telegram_id: int, username: str) -> None:
    """
    Обновляет имя пользователя в базе данных.

    Параметры:
        owner_telegram_id (int): Идентификатор владельца аккаунта.
        username (str): Новое имя пользователя.

    Возвращает:
        None

    """
    with Session() as session:
        query = text("UPDATE users SET username=:username WHERE owner_telegram_id=:owner_telegram_id")
        session.execute(query, {"owner_telegram_id": owner_telegram_id, "username": username})
        session.commit()


def update_login_name(owner_telegram_id: int, login_name: str) -> None:
    """
    Обновляет уникальный логин пользователя в базе данных.

    Параметры:
        owner_telegram_id (int): Идентификатор владельца аккаунта.
        login_name (str): Новый уникальный логин.

    Возвращает:
        None

    """
    with Session() as session:
        query = text("UPDATE users SET login_name=:login_name WHERE owner_telegram_id=:owner_telegram_id")
        session.execute(query, {"owner_telegram_id": owner_telegram_id, "login_name": login_name})
        session.commit()


def update_password(owner_telegram_id: int, password: str) -> None:
    """
    Обновляет пароль пользователя в базе данных.

    Параметры:
        owner_telegram_id (int): Идентификатор владельца аккаунта.
        password (str): Новый пароль.

    Возвращает:
        None

    """
    with Session() as session:
        query = text("UPDATE users SET password=:password WHERE owner_telegram_id=:owner_telegram_id")
        session.execute(query, {"owner_telegram_id": owner_telegram_id, "password": password})
        session.commit()


def set_user(login_name: str, owner_telegram_id: int, username: str, password: str, is_login: bool = True) -> None:
    """
    Добавляет нового пользователя в базу данных.

    Параметры:
        login_name (str): Уникальный логин пользователя.
        owner_telegram_id (int): Идентификатор владельца аккаунта.
        username (str): Имя пользователя.
        password (str): Пароль пользователя.
        is_login (bool, optional): Статус входа пользователя (по умолчанию True).

    Возвращает:
        None

    """
    with Session() as session:
        query = text(
            "INSERT INTO users (login_name, owner_telegram_id, password, username, is_login) VALUES ("
            ":login_name, :owner_telegram_id, :password, :username, :is_login)")
        session.execute(query, {"owner_telegram_id": owner_telegram_id, "password": password,
                                "login_name": login_name, "username": username, "is_login": is_login})
        session.commit()


def get_user(owner_telegram_id: int = None, login_name: str = None) -> Users | None:
    """
    Получает пользователя из базы данных по идентификатору владельца аккаунта или уникальному логину.

    Параметры:
        owner_telegram_id (int, optional): Идентификатор владельца аккаунта.
        login_name (str, optional): Уникальный логин пользователя.

    Возвращает:
        Users | None: Объект пользователя или None, если пользователь не найден.

    """
    user = None
    with Session() as session:
        if owner_telegram_id:
            query = text("SELECT owner_telegram_id, password, login_name, username, is_login FROM users WHERE "
                         "owner_telegram_id = :owner_telegram_id")
            user: Users | None = session.execute(query, {"owner_telegram_id": owner_telegram_id}).first()
        elif login_name:
            query = text("SELECT owner_telegram_id, password, login_name, username, is_login FROM users WHERE "
                         "login_name = :login_name")
            user: Users | None = session.execute(query, {"login_name": login_name}).first()
    return user


def delete_user(owner_telegram_id: int) -> None:
    """
    Удаляет пользователя из базы данных.

    Параметры:
        owner_telegram_id (int): Идентификатор владельца аккаунта.

    Возвращает:
        None

    """
    with Session() as session:
        query = text("DELETE FROM users WHERE owner_telegram_id = :owner_telegram_id")
        session.execute(query, {"owner_telegram_id": owner_telegram_id})
        session.commit()


def check_user_is_owner(user_telegram_id: int, owner_telegram_id: int) -> bool:
    """
    Проверяет, является ли пользователь владельцем аккаунта.

    Параметры:
        user_telegram_id (int): Идентификатор пользователя.
        owner_telegram_id (int): Идентификатор владельца аккаунта.

    Возвращает:
        bool: True, если пользователь является владельцем аккаунта, в противном случае False.

    """
    return user_telegram_id == owner_telegram_id
