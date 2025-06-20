import os
from aiogram import types, Router, F, Bot
from aiogram.filters import CommandStart, Command, or_f
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from app.filters.chat_types import ChatTypeFilter
from app.kbs import reply

from misc.texts import RU
from misc.utils import get_user_info, Statisticer, Mailer


user_private_router = Router()
user_private_router.message.filter(ChatTypeFilter(["private"]))

metrics_worker = Statisticer()
mail_worker = Mailer()


class Review(StatesGroup):
    waiting_text = State()


@user_private_router.message(CommandStart())
async def start_cmd(message: types.Message):
    await message.answer(RU["start"], reply_markup=reply.start_kb)


@user_private_router.message(
        or_f(Command("contact"), F.text.lower().contains("контакты"))
)
async def contact_cmd(message: types.Message):
    await message.answer(RU["contact"])


@user_private_router.callback_query(F.data == "social")
async def get_contact_callback(callback: types.CallbackQuery):
    await callback.message.answer(RU["contact"])
    await callback.answer()
    user = get_user_info(callback)
    metrics_worker.send_log(
        user["user_id"],
        'get contacts',
        user,
    )


@user_private_router.callback_query(F.data == "welcome")
async def get_back_callback(callback: types.CallbackQuery, state: FSMContext):
    await state.clear()
    await start_cmd(callback.message)
    await callback.message.delete()
    await callback.answer()


@user_private_router.callback_query(F.data == "faq_button")
async def get_faq_callback(callback: types.CallbackQuery):
    await callback.message.answer(
        RU['faq_answer'],
        reply_markup=reply.faq_kb
    )
    await callback.message.delete()
    await callback.answer()
    user = get_user_info(callback)
    metrics_worker.send_log(
        user["user_id"],
        'faq',
        user,
    )


@user_private_router.callback_query(F.data == "guide_button")
async def get_guide_callback(callback: types.CallbackQuery):
    await callback.message.answer(
        RU['guide_answer'],
        reply_markup=reply.feedback_kb
    )
    await callback.message.delete()
    await callback.answer()
    user = get_user_info(callback)
    metrics_worker.send_log(
        user["user_id"],
        'guide',
        user,
    )


@user_private_router.callback_query(F.data == "review_button")
async def get_feedback_callback(callback: types.CallbackQuery, state: FSMContext):
    await state.set_state(Review.waiting_text)
    await callback.message.answer(
        RU['review_answer'],
        reply_markup=reply.feedback_kb
    )
    await callback.message.delete()
    await callback.answer()
    user = get_user_info(callback)
    metrics_worker.send_log(
        user["user_id"],
        'feedback',
        user,
    )


@user_private_router.message(Review.waiting_text)
async def send_feedback(message: types.Message, state: FSMContext, bot: Bot):
    await message.answer(RU["thanx"])
    await state.clear()
    user = get_user_info(message)
    user_info = f'\n\nПользователь: \
        {user["fullname"]} @{user["uname"]} {user["user_id"]}'
    result = mail_worker.send_notify(
        f"Отзыв из telegram бота:\n {message.text} \n {user_info}"
    )
    if not result['status']:
        await message.answer(RU['err_send_msg'])
        await bot.send_message(
            os.getenv('TG_ADMIN_BOT'),
            f"{RU['admin_notify']} {result['msg']} "
            f"{user_info} {RU['text_review']} {message.text}"
        )
    await start_cmd(message)
