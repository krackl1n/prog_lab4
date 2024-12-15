import asyncio
import logging
import sys
from aiogram import F, Bot, Dispatcher
from aiogram.filters import CommandStart

from bot_handler import BotHandlers
from schedule_repository import ScheduleRepository
from schedule_service import ScheduleService
from stankin_api import StankinAPI


TOKEN = "7974861219:AAEOduwvVDcpxGivNA5hxQcFhYDaLKTxd4Y"

dp = Dispatcher()

async def main() -> None:
    bot = Bot(token=TOKEN)

    api = StankinAPI()
    schedule_repository = ScheduleRepository(api)
    schedule_service = ScheduleService(api)
    handlers = BotHandlers(bot, schedule_repository)

    dp.message.register(handlers.start, CommandStart())
    dp.message.register(handlers.schedule_start, F.text == 'Расписание')
    dp.callback_query.register(handlers.callback_schedule, lambda c: c.data.startswith('name_group_'))

    await dp.start_polling(bot)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())