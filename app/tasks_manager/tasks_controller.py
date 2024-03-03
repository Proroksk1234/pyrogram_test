import re
from datetime import datetime, UTC

import pytz
from pyrogram import types
from sqlalchemy import text

from app.db.db_config import Session
from app.db.models import UserTasks
from app.utils import TelegramUtils


def get_all_tasks(
        owner_telegram_id: int, current_tasks: bool = False, overdue_tasks: bool = False, completed_tasks: bool = False
) -> list[UserTasks]:
    """
        Получает список задач пользователя в зависимости от указанных параметров.

        Параметры:
        - owner_telegram_id (int): ID пользователя в Telegram.
        - current_tasks (bool): Флаг для получения текущих задач (не начатых и не завершенных).
        - overdue_tasks (bool): Флаг для получения просроченных задач.
        - completed_tasks (bool): Флаг для получения завершенных задач.

        Возвращает:
        - list[UserTasks]: Список объектов задач пользователя.
    """
    condition_text = "WHERE owner_telegram_id =:owner_telegram_id"
    with Session() as session:
        if current_tasks:
            condition_text += (" AND start_time AT TIME ZONE 'UTC' < current_timestamp AT TIME ZONE "
                               "'UTC' AND end_time AT TIME ZONE 'UTC' > current_timestamp AT TIME ZONE 'UTC'"
                               " AND status = false;")
        elif overdue_tasks:
            condition_text += (" AND end_time AT TIME ZONE 'UTC' < current_timestamp AT TIME ZONE 'UTC'"
                               " AND status = false;")
        elif completed_tasks:
            condition_text += " AND status = true;"
        query = text(
            "SELECT id_task, owner_telegram_id, task_name, start_time, end_time, completion_time, status, description "
            "FROM user_tasks "
            f"{condition_text}"
        )
        user_tasks_list: list[UserTasks] = session.execute(query, {"owner_telegram_id": owner_telegram_id}).all()
    return user_tasks_list


def get_task_by_id(id_task: int, owner_telegram_id: int) -> UserTasks | None:
    """
        Получает конкретную задачу пользователя по её ID.

        Параметры:
        - id_task (int): ID задачи.
        - owner_telegram_id (int): ID пользователя в Telegram.

        Возвращает:
        - Union[UserTasks, None]: Объект задачи пользователя или None, если задача не найдена.
    """
    with Session() as session:
        query = text(
            "SELECT id_task, owner_telegram_id, task_name, start_time, end_time, completion_time, status, "
            "description FROM user_tasks WHERE id_task =:id_task AND owner_telegram_id = :owner_telegram_id")
        user_task: UserTasks = session.execute(
            query, {"id_task": id_task, "owner_telegram_id": owner_telegram_id}).first()
    return user_task


def set_task(owner_telegram_id: int, task_name: str, start_time: datetime, end_time: datetime, description: str,
             completion_time: datetime = None, status: bool = False) -> None:
    """
        Добавляет новую задачу в базу данных.

        Параметры:
        - owner_telegram_id (int): ID пользователя в Telegram.
        - task_name (str): Название задачи.
        - start_time (datetime): Время начала задачи.
        - end_time (datetime): Время завершения задачи.
        - description (str): Описание задачи.
        - completion_time (datetime): Время завершения задачи (по умолчанию None).
        - status (bool): Статус завершения задачи (по умолчанию False).
    """
    with Session() as session:
        query = text(
            "INSERT INTO user_tasks (owner_telegram_id, task_name, start_time, end_time, completion_time, status, "
            "description) "
            "VALUES (:owner_telegram_id, :task_name, :start_time, :end_time, :completion_time, :status, :description);")
        session.execute(query, {
            "owner_telegram_id": owner_telegram_id, "task_name": task_name, "start_time": start_time,
            "end_time": end_time, "completion_time": completion_time, "status": status, "description": description})
        session.commit()


def update_task_name(id_task: int, owner_telegram_id: int, task_name: str) -> None:
    """
        Обновляет название задачи.

        Параметры:
        - id_task (int): ID задачи.
        - owner_telegram_id (int): ID пользователя в Telegram.
        - task_name (str): Новое название задачи.
    """
    with Session() as session:
        query = text(
            "UPDATE user_tasks SET task_name =:task_name WHERE owner_telegram_id =:owner_telegram_id;")
        session.execute(query, {"id_task": id_task, "owner_telegram_id": owner_telegram_id, "task_name": task_name})
        session.commit()


def update_task_description(id_task: int, owner_telegram_id: int, description: str) -> None:
    """
        Обновляет описание задачи.

        Параметры:
        - id_task (int): ID задачи.
        - owner_telegram_id (int): ID пользователя в Telegram.
        - description (str): Новое описание задачи.
    """
    with Session() as session:
        query = text(
            "UPDATE user_tasks SET description =:description WHERE owner_telegram_id =:owner_telegram_id;")
        session.execute(query, {"id_task": id_task, "owner_telegram_id": owner_telegram_id, "description": description})
        session.commit()


def update_task_start_time(id_task: int, owner_telegram_id: int, start_time: str) -> None:
    """
        Обновляет время начала задачи.

        Параметры:
        - id_task (int): ID задачи.
        - owner_telegram_id (int): ID пользователя в Telegram.
        - start_time (str): Новое время начала задачи в формате DD.MM.YYYY HH:MM.
    """
    start_time = transform_utc_time(time=start_time)
    with Session() as session:
        query = text(
            "UPDATE user_tasks SET start_time =:start_time "
            "WHERE owner_telegram_id =:owner_telegram_id;")
        session.execute(query, {"id_task": id_task, "owner_telegram_id": owner_telegram_id, "start_time": start_time})
        session.commit()


def update_task_end_time(id_task: int, owner_telegram_id: int, end_time: str) -> None:
    """
        Обновляет время завершения задачи.

        Параметры:
        - id_task (int): ID задачи.
        - owner_telegram_id (int): ID пользователя в Telegram.
        - end_time (str): Новое время завершения задачи в формате DD.MM.YYYY HH:MM.
    """
    end_time = transform_utc_time(time=end_time)
    with Session() as session:
        query = text(
            "UPDATE user_tasks SET end_time =:end_time "
            "WHERE owner_telegram_id =:owner_telegram_id AND user_tasks.id_task = :id_task;")
        session.execute(query, {"id_task": id_task, "owner_telegram_id": owner_telegram_id, "end_time": end_time})
        session.commit()


def update_task_completion(id_task: int, owner_telegram_id: int) -> bool:
    """
        Обновляет статус и время завершения задачи.

        Параметры:
        - id_task (int): ID задачи.
        - owner_telegram_id (int): ID пользователя в Telegram.

        Возвращает:
        - bool: Статус завершения задачи (True - завершена, False - не завершена).
    """
    task: UserTasks = get_task_by_id(id_task=id_task, owner_telegram_id=owner_telegram_id)
    status = True if not task.status else False
    completion_time = datetime.now(UTC) if status else None
    with Session() as session:
        query = text(
            "UPDATE user_tasks SET completion_time =:completion_time, status=:status "
            "WHERE owner_telegram_id =:owner_telegram_id AND user_tasks.id_task = :id_task;")
        session.execute(query, {
            "id_task": id_task, "owner_telegram_id": owner_telegram_id,
            "completion_time": completion_time, "status": status})
        session.commit()
    return status


def delete_task(owner_telegram_id: int, id_task: int = None) -> None:
    """
        Удаляет задачу пользователя из базы данных.

        Параметры:
        - owner_telegram_id (int): ID пользователя в Telegram.
        - id_task (int): ID задачи (необязательно).
    """
    with Session() as session:
        if id_task:
            query = text("DELETE FROM user_tasks WHERE owner_telegram_id =:owner_telegram_id AND id_task = :id_task;")
            session.execute(query, {"owner_telegram_id": owner_telegram_id, "id_task": id_task})
        else:
            query = text("DELETE FROM user_tasks WHERE owner_telegram_id =:owner_telegram_id;")
            session.execute(query, {"owner_telegram_id": owner_telegram_id})
        session.commit()


def check_valid_date(start_time: str, end_time: str = None) -> bool:
    """
        Проверяет корректность указанных дат и времени.

        Параметры:
        - start_time (str): Время начала задачи в формате DD.MM.YYYY HH:MM.
        - end_time (str): Время завершения задачи в формате DD.MM.YYYY HH:MM (по умолчанию None).

        Возвращает:
        - bool: True, если даты и время указаны корректно, иначе False.
    """
    datetime_regex = r'^(0[1-9]|[12][0-9]|3[01])\.(0[1-9]|1[0-2])\.20([0-9][0-9]) ([0-1][0-9]|2[0-3])\:([0-5][0-9])'
    is_true_match_check = re.match(datetime_regex, start_time) if not end_time else re.match(datetime_regex, end_time)
    if not is_true_match_check:
        return False
    start_date = (datetime.strptime(start_time, '%d.%m.%Y %H:%M')).astimezone(UTC)
    if end_time:
        end_date = (datetime.strptime(end_time, '%d.%m.%Y %H:%M')).astimezone(UTC)
        if end_date <= start_date:
            return False
    return True


def transform_utc_time(time: str) -> datetime:
    """
        Преобразует время в формате DD.MM.YYYY HH:MM в объект datetime с учетом времени в UTC.

        Параметры:
        - time (str): Время в формате DD.MM.YYYY HH:MM.

        Возвращает:
        - datetime: Объект datetime с учетом времени в UTC.
    """
    return datetime.strptime(time, '%d.%m.%Y %H:%M').astimezone(UTC)


def get_text_set_time(start_time: datetime | str = None, is_error: bool = False) -> str:
    """
        Генерирует текстовое сообщение для установки времени задачи.

        Параметры:
        - start_time (datetime | str): Время начала задачи (по умолчанию None).
        - is_error (bool): Флаг ошибки в формате времени (по умолчанию False).

        Возвращает:
        - str: Текстовое сообщение с инструкцией для установки времени задачи.
    """
    text_message = (
        f"{('Вы ввели неверный формат даты и времени!!!' if is_error else '')}\n"
        f"Введите дату и время {('старта' if not start_time else 'завершения')} "
        "вашей новой задачи в формате DD.MM.YYYY HH:MM. Ввод в таком формате обязателен.\n"
        f"{(f'Дата не должна быть меньше, чем {(start_time.strftime("%d.%m.%Y %H:%M") if isinstance(
            start_time, datetime) else start_time)}' if start_time else '')}"
    )
    return text_message


async def send_messages_get_all_tasks(list_tasks: list[UserTasks], message: types.CallbackQuery) -> None:
    """
        Асинхронно отправляет сообщения с информацией о задачах.

        Параметры:
        - list_tasks (list[UserTasks]): Список объектов задач пользователя.
        - message (types.CallbackQuery) -> None: Объект сообщения в Telegram.
    """
    list_text_messages = list()
    if not list_tasks:
        list_text_messages.append("Задачи данного типа у вас отсутствуют")
    else:
        for count, task in enumerate(list_tasks):
            message_text = (
                f"*                                 Задача {task.task_name} № {task.id_task}                     *\n\n"
                f"Описание задачи:\n{task.description}\n\n"
                f"Время старта данной задачи по Гринвичу:\n{task.start_time.astimezone(pytz.timezone('UTC'))}\n\n"
                f"Время завершения данной задачи по Гринвичу:\n{task.end_time.astimezone(pytz.timezone('UTC'))}\n\n"
                f"Статус завершения задачи:\nЗадача {(
                    'завершена' if task.status else 'просрочена' if 
                    task.end_time < datetime.now(UTC) else 'выполняется')}\n\n"
                f"{(f'Время завершения задачи по Гринвичу:\n{task.completion_time.astimezone(pytz.timezone('UTC'))}\n\n' 
                    if task.status else '')}"
            )
            list_text_messages.append(message_text)
    for count, text_message in enumerate(list_text_messages):
        telegram_utils = TelegramUtils(text=text_message, message=message)
        await telegram_utils.send_messages()
