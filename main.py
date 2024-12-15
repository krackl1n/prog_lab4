import asyncio
import logging
import os
import sys
from aiogram import F, Bot, Dispatcher
from aiogram.filters import CommandStart
from dotenv import load_dotenv

from bot_handler import BotHandlers
from schedule_service import ScheduleService
from stankin_api import StankinAPI


load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")

if not TOKEN:
    raise ValueError("BOT_TOKEN не найден в .env файле")

dp = Dispatcher()

async def main() -> None:
    bot = Bot(token=TOKEN)

    api = StankinAPI()
    schedule_service = ScheduleService(api)
    handlers = BotHandlers(bot, schedule_service)

    dp.message.register(handlers.start, CommandStart())
    dp.message.register(handlers.schedule_start, F.text == 'Расписание')
    dp.callback_query.register(handlers.callback_schedule, F.data.startswith("group_"))

    await dp.start_polling(bot)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())