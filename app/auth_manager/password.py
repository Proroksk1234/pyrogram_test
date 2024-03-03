import re
from cryptography.fernet import Fernet
from app.config import SECRET_KEY

FERNET = Fernet(SECRET_KEY)


def validation_password(password: str) -> bool:
    """
    Проверяет, соответствует ли предоставленный пароль заданным критериям.

    Параметры:
    - password (str): Пароль для валидации.

    Возвращает:
    - bool: True, если пароль соответствует критериям, False в противном случае.
    """
    regex_pattern = r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&#])[A-Za-z\d@$!%*?&#]{8,}$"
    return bool(re.match(regex_pattern, password))


def encrypt_password(password: str) -> str:
    """
    Шифрует предоставленный пароль с использованием шифрования Fernet.

    Параметры:
    - password (str): Пароль для шифрования.

    Возвращает:
    - str: Зашифрованный пароль.
    """
    encrypted_password = FERNET.encrypt(password.encode()).decode()
    return encrypted_password


def descript_password(password: str) -> str:
    """
    Дешифрует предоставленный пароль с использованием расшифровки Fernet.

    Параметры:
    - password (str): Зашифрованный пароль для расшифровки.

    Возвращает:
    - str: Расшифрованный пароль.
    """
    decrypted_password = FERNET.decrypt(password.encode()).decode()
    return decrypted_password


def verify_password(password: str, encrypted_password: str) -> bool:
    """
    Проверяет, соответствует ли предоставленный пароль расшифрованному зашифрованному паролю.

    Параметры:
    - password (str): Обычный текст пароля.
    - encrypted_password (str): Зашифрованный пароль для сравнения.

    Возвращает:
    - bool: True, если пароли совпадают, False в противном случае.
    """
    return password == descript_password(encrypted_password)


def text_set_password_message(is_error: bool = False) -> str:
    """
    Генерирует сообщение, указывающее пользователю на установку нового пароля.

    Параметры:
    - is_error (bool): Флаг, указывающий, должно ли включаться сообщение об ошибке.

    Возвращает:
    - str: Инструкционное текстовое сообщение.
    """
    text_message = (
        f"{('Вы ввели пароль, не соответствующий критериям!!!\n' if is_error else '')}" 
        "Введите ваш новый пароль.\n\n"
        "Он должен соответствовать следующим критериям:\n\n"
        "1) Более 8 символов\n"
        "2) Должен содержать 1 спец.символ, число, большой и маленький символ\n"
        "3) Разрешено использовать только латиницу"
    )
    return text_message
