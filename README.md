# Исключительные предложения для разработчиков и стартапов - Dealsbe

Telegram-бот для предоставления программного обеспечения и поддержки. Пользователи могут просматривать предложения и публиковать сделки.
## Возможности
- Рекомендации по ПО.
- Публикация сделок.
- Роли: Пользователь, Оператор, Администратор.
- База данных и многоязычная поддержка (по умолчанию русский).
## Требования
- Python 3.8+
- Установите зависимости: `pip install -r requirements.txt`
- Telegram Bot Token
## Установка

1. Клонируйте репозиторий:
```bash  
git clone https://github.com/pyadrus/SupportManagerBot-Telegram.git  cd dealsbe
```

2. Создайте .env:
```plaintext
TOKEN=ваш_токен  LOG_TYPE=file  ADMIN=@ваш_админ  DB_NAME=src/core/database/database.db  GROUP_ID=ваш_группа_id
``` 

3. Установите зависимости:
```bash
pip install -r requirements.txt
```

4. Запустите:
```bash
python main.py  
```

## Использование

- /start - начать работу.
- Публикуйте сделки через /post_deal.
- Например, Админ (@PythonDEV1) управляет, оператор (@OlgaSmir123) проверяет.

## Документация

[Подробности](https://github.com/pyadrus/SupportManagerBot-Telegram/blob/master/doc/doc.md).

## Участие

1. Форкните репозиторий.
2. Создайте ветку, внесите изменения, отправьте PR.

## Лицензия

GNU GENERAL PUBLIC LICENSE - см. LICENSE.
## Контакты

- Telegram: @PyAdminRU