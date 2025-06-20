import asyncio
import logging
import os
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, types
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage

from misc.utils import SQLiter
from app.handlers.user_private import user_private_router
from app.handlers.user_group import user_group_router
from app.handlers.admin_messaging import setup_admin_messaging_handlers
from app.common.cmds import private


load_dotenv()
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(name)s - %(message)s")

ADMIN_ID = int(os.getenv('TG_ADMIN_BOT'))
TG_TOKEN = os.getenv('TG_TOKEN')
DB_NAME = os.getenv('DB_NAME')

bot = Bot(token=TG_TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher(storage=MemoryStorage())
db = SQLiter(DB_NAME)

dp.include_router(user_private_router)
dp.include_router(user_group_router)
setup_admin_messaging_handlers(dp, bot, db, ADMIN_ID)

async def main():
    logger.info("Starting bot")
    await bot.delete_webhook(drop_pending_updates=True)
    await bot.set_my_commands(commands=private, scope=types.BotCommandScopeAllPrivateChats())
    await dp.start_polling(bot, allowed_updates=['message, edited_message'])

if __name__ == '__main__':
    asyncio.run(main())
