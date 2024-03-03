"""
Модуль с Data-классами для представления пользователей, состояния конечного автомата (FSM) и задач пользователей.

Data-классы:
    1. Users: Представляет информацию о пользователе.
        Параметры:
            - owner_telegram_id: int - идентификатор владельца (в данном случае, Telegram ID).
            - login_name: str - имя для входа.
            - username: str - имя пользователя.
            - password: str - пароль пользователя.
            - is_login: bool - флаг, указывающий на статус входа пользователя.

    2. FSMContext: Представляет контекст конечного автомата (FSM) для пользователя.
        Параметры:
            - telegram_id: int - идентификатор пользователя в Telegram.
            - state: str - текущее состояние FSM.
            - data: dict - дополнительные данные контекста FSM.

    3. UserTasks: Представляет задачу пользователя.
        Параметры:
            - id_task: int - идентификатор задачи.
            - user: Users - объект, представляющий пользователя.
            - task_name: str - название задачи.
            - description: str - описание задачи.
            - start_time: datetime - время начала задачи.
            - end_time: datetime - время окончания задачи.
            - completion_time: datetime | None - время завершения задачи (может быть None, если задача не завершена).
            - status: bool - статус выполнения задачи (True, если выполнена, False в противном случае).

Примечание:
    - В данных классах используются типовые аннотации, предоставляющие информацию о типах переменных.
    - Data-классы предоставляют неизменяемые объекты с автоматической генерацией методов, таких как __init__ и __repr__.
"""

from dataclasses import dataclass
from datetime import datetime


@dataclass
class Users:
    owner_telegram_id: int
    login_name: str
    username: str
    password: str
    is_login: bool


@dataclass
class FSMContext:
    telegram_id: int
    state: str
    data: dict


@dataclass
class UserTasks:
    id_task: int
    user: Users
    task_name: str
    description: str
    start_time: datetime
    end_time: datetime
    completion_time: datetime | None
    status: bool
