import os
from aiogram import types


RU = {
    "start": "Здравствуйте! Это Оригами-бот, я помогу вам сориентироваться по всем вопросам, связанным с нашей деятельностью.",
    "contact": "Мы в телеграме: @origami_invest \nМы в инстаграме: https://www.instagram.com/origami_invest \nПишите нам: origami_invest@mail.ru",
    "back_button": "↩️ Вернуться назад",
    "form": "Заполнить анкету",
    "social": "Наши соцсети и контакты",
    "faq_button": "Часто задаваемые вопросы",
    "guide_button": "Вопросы по дизайн-гайду",
    "faq_answer": "<b>💬 Как инвестировать?</b>\n \
К сожалению, мы пока не набираем инвесторов. Но обязательно будем выкладывать в своих соцсетях объявления обо всех изменениях.\n\n \
<b>💬 Хочу разместить свой товар в ваших проектах или хочу сотрудничать в соцсетях.</b>\n \
Напишите нам пожалуйста на <code>origami_invest@mail.ru</code> своё предложение и мы свяжемся с вами.\n\n \
<b>💬 Хоумстейджинг</b> \n \
Заполните пожалуйста анкету, мы свяжемся с вами.",
    "guide_answer": "Напишите свой вопрос по дизайн-гайду и мы свяжемся с вами в ближайшее время!",
    "review_button": "Хочу оставить отзыв",
    "review_answer": "Напишите свой отзыв или предложения по улучшению качества наших услуг текстом в сообщении. \n\nНе забудьте оставить контакт, если вам нужна обратная связь.",
    "thanx": "Спасибо за ваш отзыв/предложение.",
    "err_send_msg": "⛔️ Ошибка отправки отзыва/предложения. Попробуйте отправить позднее.",
    "admin_notify": "⛔️ Ошибка отправки отзыва: \n\n",
}

START_BUTTONS = [
    [
        types.InlineKeyboardButton(
            text=RU['faq_button'], callback_data="faq_button",
        ),
    ],
    [
        types.InlineKeyboardButton(
            text=RU['guide_button'], callback_data="guide_button",
        ),
    ],
    # [
    #     types.InlineKeyboardButton(
    #         text=RU['review_button'], callback_data="review_button"
    #     )
    # ]
]

FAQ_BUTTONS = [
    [
        types.InlineKeyboardButton(
            text=RU['form'],
            url=os.getenv('FORM_URL'),
        ),
    ],
    [
        types.InlineKeyboardButton(
            text=RU['social'],
            callback_data="social",
        ),
    ],
    [
        types.InlineKeyboardButton(
            text=RU['back_button'],
            callback_data="welcome",
        ),
    ]
]

REVIEW_BUTTONS = [
    [
        types.InlineKeyboardButton(
                text=RU['back_button'],
                callback_data="welcome",
            )
    ]
]
