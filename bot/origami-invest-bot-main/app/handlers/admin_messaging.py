from aiogram import types, Bot, Dispatcher
from aiogram.enums.parse_mode import ParseMode
import logging
from misc.utils import SQLiter

logger = logging.getLogger(__name__)


def setup_admin_messaging_handlers(dp: Dispatcher, bot: Bot, db: SQLiter, admin_id: int):
    """Регистрируем обработчики сообщений для администратора."""

    @dp.message(lambda message: message.from_user.id != admin_id and not message.text.startswith('/'))
    async def forward_to_admin(message: types.Message):
        """Добавляет сообщение пользователя в БД и уведомляет администратора"""
        db.add_message(message.from_user.id, message.from_user.username, message.from_user.full_name, message.text)

        pending_count = db.count_pending_messages()

        user_info = (
            f"👤 <b>{message.from_user.full_name}</b>\n"
            f"🔗 <a href='tg://user?id={message.from_user.id}'>Профиль</a>\n"
            f"🆔 ID: {message.from_user.id}\n"
        )

        if message.from_user.username:
            user_info += f"📌 Username: @{message.from_user.username}\n"

        text_to_admin = (
            f"📩 <b>Новое сообщение в очереди!</b>\n\n"
            f"От пользователя:\n"
            f"{user_info}\n\n"
            f"💬 {message.text}\n\n"
            f"<i>Чтобы ответить или пропустить новое сообщение отправьте /next </i>\n\n"
            f"📊 Всего необработанных сообщений: <b>{pending_count}</b>"
        )

        await bot.send_message(admin_id, text_to_admin, parse_mode=ParseMode.HTML)
        await message.reply("✅ Ваше сообщение отправлено администратору.")

    @dp.message(lambda message: message.from_user.id == admin_id and message.text == "/next")
    async def get_next_admin_message(message: types.Message):
        """Выдаёт админу следующее сообщение из БД"""
        msg = db.get_next_message()
        if msg:
            msg_id, user_id, username, fullname, text = msg

            user_info = (
                f"👤 <b>{fullname}</b>\n"
                f"🔗 <a href='tg://user?id={user_id}'>Профиль</a>\n"
                f"🆔 ID: {user_id}\n"
            )

            if username:
                user_info += f"📌 Username: @{username}\n"

            await bot.send_message(
                admin_id,

                f"📬 Сообщение {msg_id} от:\n"
                f"{user_info}\n\n"
                f"💬 {text}\n\n"

                f"<i>Чтобы отправить ответ ответьте на это сообщение.</i>"
                f"<i>Чтобы удалить сообщение без ответа, отправьте /skip</i>",
                parse_mode=ParseMode.HTML
            )
            db.update_message_status(msg_id, 'in_progress')
        else:
            await message.reply("✅ Очередь пуста.")

    @dp.message(lambda message: message.from_user.id == admin_id and message.text == "/skip")
    async def skip_message(message: types.Message):
        """Позволяет администратору пропустить сообщение без ответа"""
        msg = db.get_next_message()
        if msg:
            msg_id = msg[0]
            db.update_message_status(msg_id, 'ignored')
            pending_count = db.count_pending_messages()

            await message.reply(
                f"🗑 Сообщение №{msg_id} удалено из очереди.\n"
                f"📊 Осталось необработанных сообщений: <b>{pending_count}</b>",
                parse_mode=ParseMode.HTML
            )
        else:
            await message.reply("✅ Очередь пуста.")

    @dp.message(lambda message: message.from_user.id == admin_id and message.reply_to_message)
    async def answer_to_user(message: types.Message):
        """Пересылает ответ администратора пользователю"""
        try:
            lines = message.reply_to_message.text.split("\n")

            # Получаем user_id и msg_id
            msg_id_line = lines[0]  # Первая строка содержит msg_id
            user_id_line = next((line for line in lines if "🆔 ID:" in line), None)

            if not user_id_line:
                await message.reply("❌ Ошибка: Не удалось определить пользователя.")
                return

            user_id = int(user_id_line.split(":")[1].strip())
            msg_id = int(msg_id_line.split(" ")[2])
            pending_count = db.count_pending_messages() - 1

            await bot.send_message(user_id, f"📩 <b>Ответ от администратора:</b>\n\n{message.text}", parse_mode=ParseMode.HTML)
            await message.reply(
                f"<i>Пользователь получил сообщение ✅</i>\n\n"
                f"📊 Осталось необработанных сообщений: <b>{pending_count}</b>\n\n"
                f"<i>Чтобы посмотреть новое сообщение, отправьте /next</i>",
                parse_mode=ParseMode.HTML
            )
            db.update_message_status(msg_id, 'done')
        except Exception as e:
            logger.error(f"Ошибка отправки сообщения: {e}")
            await message.reply("<i>Ошибка отправки сообщения ❌</i>", parse_mode=ParseMode.HTML)
