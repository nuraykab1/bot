import os
from aiogram import F, Dispatcher, types
from aiogram.fsm.context import FSMContext
from aiogram.filters.state import State, StatesGroup
from dataclasses import dataclass, asdict

from misc.utils import SQLiter, Mailer, Statisticer
from misc.texts import RU, BUTTONS, BACK_BUTTON, FORM_BUTTON, \
    SOCIAL_BUTTON

HOLLY_WORDS = [
    'holly',
    'holy',
    'holi',
    'holli',
    'холли',
    'холи',
]
HOLLY_DOC = os.getenv("HOLLY_DOC")

db_worker = SQLiter(os.getenv('DB_NAME', 'db.sqlite3'))
metrics_worker = Statisticer()


@dataclass
class User:
    user_id: int
    uname: str
    fullname: str
    is_bot: bool
    locale: str


class Review(StatesGroup):
    waiting = State()


async def cmd_start(message: types.Message):
    await welcome_text(message)
    user = get_user_info(message)
    metrics_worker.send_log(
        user.user_id,
        'start bot',
        asdict(user),
    )


async def cmd_contact(message: types.Message):
    await message.answer(RU['contact'])


async def call_contact(call: types.CallbackQuery):
    await cmd_contact(call.message)
    user = get_user_info(call)
    metrics_worker.send_log(
        user.user_id,
        'get contacts',
        asdict(user),
    )
    await call.answer()


async def welcome_text(message: types.Message):
    user = get_user_info(message)
    db_worker.add_user(user)
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    keyboard.add(*BUTTONS)
    await message.answer(RU['start'], reply_markup=keyboard)


async def begin(call: types.CallbackQuery, state: FSMContext):
    await state.finish()
    await welcome_text(call.message)
    await call.message.delete()
    await call.answer()


async def cmd_cancel(message: types.Message, state: FSMContext):
    await state.finish()
    await message.answer("Действие отменено")
    await welcome_text(message)


def get_user_info(message: types.Message):
    return User(
        user_id=message.from_user.id,
        uname=message.from_user.username,
        fullname=message.from_user.full_name,
        is_bot=message.from_user.is_bot,
        locale=message.from_user.language_code
    )


async def first_button(call: types.CallbackQuery):
    await show_msg(
        call, RU['first_answer'],
        (FORM_BUTTON + SOCIAL_BUTTON + BACK_BUTTON)
    )
    user = get_user_info(call)
    db_worker.add_action(user, 'Часто задаваемые вопросы')
    metrics_worker.send_log(
        user.user_id,
        'faq',
        asdict(user),
    )


async def second_button(call: types.CallbackQuery):
    await Review.waiting.set()
    await show_msg(call, RU['second_answer'], (BACK_BUTTON))
    user = get_user_info(call)
    db_worker.add_action(user, 'Хочу оставить отзыв')
    metrics_worker.send_log(
        user.user_id,
        'review',
        asdict(user),
    )


async def show_msg(call: types.CallbackQuery, text, buttons):
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    keyboard.add(*buttons)
    await call.message.answer(
        text,
        parse_mode=types.ParseMode.HTML,
        reply_markup=keyboard
    )
    await call.message.delete()
    await call.answer()


async def get_review(message: types.Message, state: FSMContext):
    await message.answer(RU['thanx'])
    await state.finish()
    user = get_user_info(message)
    user_info = f'\n\nПользователь: \
        {user.fullname} @{user.uname} {user.user_id}'
    mailer_worker = Mailer()
    result = mailer_worker.send_notify(message.text + user_info)
    if not result['status']:
        await message.answer(RU['err_send_msg'])
        await message.bot.send_message(
            os.getenv('TG_ADMIN_BOT'),
            f"{RU['admin_notify']} {result['msg']} "
            f"{user_info} {RU['text_review']} {message.text}"
        )
    await welcome_text(message)


async def cmd_holly(message: types.Message):
    if HOLLY_DOC:
        await message.answer_document(HOLLY_DOC)
    user = get_user_info(message)
    metrics_worker.send_log(
        user.user_id,
        'holly',
        asdict(user),
    )


def register_handlers_common(dp: Dispatcher):
    dp.register_message_handler(cmd_start, commands="start", state="*")
    dp.register_message_handler(cmd_contact, commands="contact", state="*")
    dp.register_message_handler(cmd_cancel, commands="cancel", state="*")
    dp.register_message_handler(
        cmd_cancel, F.text(equals="отмена", ignore_case=True), state="*"
    )
    dp.register_callback_query_handler(
        first_button, F.text(startswith="first_button"), state="*"
    )
    dp.register_callback_query_handler(
        second_button, F.text(startswith="second_button"), state="*"
    )
    dp.register_callback_query_handler(
        begin, F.text(startswith="welcome"), state="*"
    )
    dp.register_callback_query_handler(
        call_contact, F.text(startswith="social"), state="*"
    )
    dp.register_message_handler(get_review, state=Review.waiting)
    dp.register_message_handler(
        cmd_holly,
        lambda message: message.text.lower().strip() in HOLLY_WORDS,
        state="*"
    )
