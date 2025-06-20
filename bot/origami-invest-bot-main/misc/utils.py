import sqlite3
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import os
import requests
import json
from aiogram import types


class SQLiter:
    def __init__(self, database) -> None:
        self.connection = sqlite3.connect(database, check_same_thread=False)
        self.cursor = self.connection.cursor()
        self.init_db()

    def init_db(self):
        """Создаёт таблицы, если их нет"""
        with self.connection:
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    username TEXT,
                    fullname TEXT,
                    message TEXT NOT NULL,
                    status TEXT DEFAULT 'pending'
                )
            """)
        self.connection.commit()

    def add_message(self, user_id, username, fullname, message):
        """Добавляет сообщение пользователя в БД"""
        with self.connection:
            self.cursor.execute(
                "INSERT INTO messages (user_id, username, fullname, message) VALUES (?, ?, ?, ?)",
                (user_id, username, fullname, message)
            )
        self.connection.commit()

    def get_next_message(self):
        """Получает следующее необработанное сообщение"""
        with self.connection:
            message = self.cursor.execute(
                "SELECT id, user_id, username, fullname, message FROM messages WHERE status IN ('pending', 'in_progress') LIMIT 1"
            ).fetchone()
        return message

    def update_message_status(self, message_id, status):
        """Обновляет статус сообщения"""
        with self.connection:
            self.cursor.execute(
                "UPDATE messages SET status = ? WHERE id = ?", (status, message_id)
            )
        self.connection.commit()

    def count_pending_messages(self):
        """Подсчитывает количество сообщений со статусом 'pending'"""
        with self.connection:
            count = self.cursor.execute(
                "SELECT COUNT(*) FROM messages WHERE status IN ('pending', 'in_progress')"
            ).fetchone()[0]
        return count

    def close(self):
        self.connection.close()


class Statisticer:

    def __init__(self) -> None:
        self.api_key = os.getenv('METRIC_API_KEY')
        self.url = os.getenv('METRIC_URL')

    def send_log(self, user_id: int, event: str, properties: dict) -> None:
        """
        Send metrics to amplitude.com for agregate information.
        """
        payload = {"api_key": self.api_key, "events": [
            {
                "user_id": user_id,
                "event_type": event,
                "user_properties": properties,
                "country": None,
            }
        ]}
        requests.post(self.url, data=json.dumps(payload))


class Mailer:

    def __init__(self) -> None:
        self.server = os.getenv('MAIL_SERVER', 'smtp.server.com')
        self.port = os.getenv('MAIL_PORT', '465')
        self.sender = os.getenv('MAIL_SENDER', 'sender@mail.com')
        self.password = os.getenv('MAIL_SENDER_PWD', 'pa$$w0rd')
        self.receiver = os.getenv('MAIL_RECEIVER', 'receiver@mail.com')
        self.subject = os.getenv('MAIL_SUBJECT', 'Origami bot notice')

    def send_notify(self, message) -> dict:
        msg = MIMEMultipart()
        msg['From'] = self.sender
        msg['To'] = self.receiver
        msg['Subject'] = self.subject
        msg.attach(MIMEText(message, 'plain'))

        try:
            srv = smtplib.SMTP_SSL(self.server, self.port)
            srv.login(self.sender, self.password)
            srv.send_message(msg)

            return {
                'status': True,
                'msg': 'Email sent successfully',
            }
        except Exception as e:
            return {
                'status': False,
                'msg': f'An error occurred while sending the email: {str(e)}'
            }
        finally:
            srv.quit()


def get_user_info(message: types.Message):
    return {
        "user_id": message.from_user.id,
        "uname": message.from_user.username,
        "fullname": message.from_user.full_name,
        "is_bot": message.from_user.is_bot,
        "locale": message.from_user.language_code,
    }


if __name__ == '__main__':
    pass
