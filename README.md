# Запуск приложения PYROGRAM_TEST

Все операции по запуску проводились на ОС Linux Ubuntu 22.04

# Запуск приложения через консоль

- Клонируем ссылку
```bash
git clone https://github.com/Proroksk1234/pyrogram_test
```
- Переходим в папку с локальным проектом
```bash
cd pyrogram_test
```
- Устанавливаем виртуальное окружение. Используем Python 3. Активируем окружение:
```bash
python3 -m venv venv
source venv/bin/activate
```
- Для виртуального окружения принимаем зависимости:
```bash
pip install -r requirements.txt
```
- Копируем файл example.env в новый файл .env и адаптируем значения под конфигурацию вашей машины или сервера.
- Обязательно прописываем все параметры, находящиеся в .env

```bash
cp example.env .env
```
- Запускаем локальный сервер:
```bash
python3 main.py
```

# Запуск приложения через docker
- Клонируем ссылку
```bash
git clone https://github.com/Proroksk1234/pyrogram_test
```
- Переходим в папку с локальным проектом
```bash
cd pyrogram_test
```
- Копируем файл example.env в новый файл .env и адаптируем значения под конфигурацию вашей машины или сервера.
- Обязательно прописываем все параметры, находящиеся в .env кроме DATABASE_CONNECTION_STRING

```bash
cp example.env .env
```
- Запускаем docker-compose файл
```bash
docker-compose up --build
```
