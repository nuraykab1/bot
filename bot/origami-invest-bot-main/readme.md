# Origami invest bot

Telegram бот для ответа на частые вопросы и получения обратной связи. 

Возможности бота: 
- отправка FAQ
- получение обратной связи от клиентов

## Environment Variables

Нужно получить токен от BotFather и записать в файл .env

`TG_TOKEN=<secret telegram token>`

`TG_ADMIN_BOT=<id admin>`

`DB_NAME=path/to/database.sqlite3`

`MAIL_SERVER=smtp.server.com`

`MAIL_PORT=465`

`MAIL_SENDER=sender@server.com`

`MAIL_SENDER_PWD=password`

`MAIL_RECEIVER=receiver@server.com`

`MAIL_SUBJECT='Уведомление от Origami bot'`


## Run Locally

Клонируйте проект

```bash
  git clone git@github.com:Stryukov/origami-invest-bot.git
```

Переходи в каталог проекта

```bash
  cd origami_invest_bot
```

Создай и активируй виртуальное окружение

```bash
  python3 -m venv venv && source venv/bin/activate
```


Установи зависимости

```bash
  pip install -r requirements.txt
```

Запусти бота

```bash
  python3 main.py
```

## Tech Stack

**Server:** aiogram


## License

[MIT](https://choosealicense.com/licenses/mit/)
