import os
from string import punctuation

from aiogram import types, Router

from app.filters.chat_types import ChatTypeFilter

user_group_router = Router()
user_group_router.message.filter(ChatTypeFilter(['group', 'supergroup']))
user_group_router.edited_message.filter(
    ChatTypeFilter(['group', 'supergroup'])
)

TARGET_WORDS = os.getenv("HOLLY_WORDS", "").split(" ")


def clean_text(text: str):
    return text.translate(str.maketrans('', '', punctuation))


@user_group_router.edited_message()
@user_group_router.message()
async def parse_comment(message: types.Message):
    if message.reply_to_message:
        if message.reply_to_message.from_user.id == 777000:
            if TARGET_WORDS.intersection(
                clean_text(message.text.lower()).split()
            ):
                await message.reply_document(os.getenv("HOLLY_DOC", ""))
