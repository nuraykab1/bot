from aiogram.types import InlineKeyboardMarkup

from misc.texts import START_BUTTONS, FAQ_BUTTONS, REVIEW_BUTTONS


start_kb = InlineKeyboardMarkup(inline_keyboard=START_BUTTONS)
faq_kb = InlineKeyboardMarkup(inline_keyboard=FAQ_BUTTONS)
feedback_kb = InlineKeyboardMarkup(inline_keyboard=REVIEW_BUTTONS)
