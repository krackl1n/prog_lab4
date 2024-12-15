from aiogram import Dispatcher, F
from aiogram.types import Message, InlineKeyboardButton, KeyboardButton, ReplyKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from schedule_repository import ScheduleRepository
from schedule_service import ScheduleService

class BotHandlers:
    version = "0.0.1"

    def __init__(self, schedule_service: ScheduleRepository):
        self.schedule_service = schedule_service

    async def start(self, message: Message):
        """Приветственное сообщение."""
        builder = InlineKeyboardBuilder()
        builder.row(InlineKeyboardButton(text='Расписание', url="t.me/splash_schedule_bot/schedule", callback_data='app'))
        await message.answer(f'Приложение для просмотра расписания, дз, отметки посещаемости и много другого\n\n- Бот может работать очень медленно и выдавать некорректные ответы\n- Бот работает в тестовом режиме (многие функции не доступны обычным пользователям)\n\nВерсия: {self.version} by splash team', reply_markup=self._installKeyboardStart())

    
    async def schedule_start(self, message: Message):
        keyboard_builder = InlineKeyboardBuilder()

        types_group = set([group.type for group in self.schedule_service.GROUPS])
        
        for type in types_group:
            keyboard_builder.add(InlineKeyboardButton(text=type, callback_data=(f"name_group_{type}")))
        keyboard_builder.adjust(5, 6)

        message_to_send = """Выбор группы для получения расписания. Выберите первые буквы группы"""
        await message.answer(message_to_send, reply_markup=keyboard_builder.as_markup())
    
    async def schedule(self, message: Message):
        group = "ИДБ-23-14"
        try:
            schedule = self.schedule_service.get_schedule(group)
            
            await message.answer(self.schedule_service.api.fetch_schedule_description().last_category.name)
        except Exception as e:
            await message.answer(f"Ошибка при получении расписания: {e}")

    def _installKeyboardStart(self):
        keyboard = [
            [KeyboardButton(text='Расписание'), ], 
            [KeyboardButton(text='Новости'), ],
            [KeyboardButton(text='Вход'), KeyboardButton(text='GPT'), KeyboardButton(text='Настройки')] # , web_app=WebAppInfo(url="https://core.telegram.org/bots/webapps")
        ]
        return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)

