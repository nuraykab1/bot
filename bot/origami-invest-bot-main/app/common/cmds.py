from aiogram.types import BotCommand


private = [
    BotCommand(command="/start", description="🚀 (пере)запустить бота"),
    BotCommand(command="/contact", description="👤 наши контакты"),
    BotCommand(
        command="/cancel",
        description="🛑 отменить текущее действие"
    )
]
