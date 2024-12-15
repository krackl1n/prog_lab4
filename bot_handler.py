from aiogram import Bot, Dispatcher, F, types
from aiogram.types import Message, InlineKeyboardButton, KeyboardButton, ReplyKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from schedule_repository import ScheduleRepository
from schedule_service import ScheduleService

class BotHandlers:
    version = "0.0.1"

    def __init__(self, bot: Bot, schedule_service: ScheduleRepository):
        self.bot = bot
        self.schedule_service = schedule_service

    async def start(self, message: Message):
        builder = InlineKeyboardBuilder()
        builder.row(InlineKeyboardButton(text='Расписание', url="t.me/splash_schedule_bot/schedule", callback_data='app'))
        await message.answer(f'Приложение для просмотра расписания, дз, отметки посещаемости и много другого\n\n- Бот может работать очень медленно и выдавать некорректные ответы\n- Бот работает в тестовом режиме (многие функции не доступны обычным пользователям)\n\nВерсия: {self.version} by splash team', reply_markup=self._installKeyboardStart())

    async def schedule_start(self, message: Message):
        keyboard_builder = InlineKeyboardBuilder()

        types_group = sorted(set([group.type for group in self.schedule_service.GROUPS]))
        
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

    async def callback_schedule(self, callback_query: types.CallbackQuery):
        await self.bot.answer_callback_query(callback_query.id)
        callback_data = callback_query.data.split('_')
        keyboard_builder = InlineKeyboardBuilder()

        try:
            match len(callback_data):
                case 3:
                    await self._handle_group_type_selection(callback_query, callback_data, keyboard_builder)

                case 4:
                    await self._handle_year_group_selection(callback_query, callback_data, keyboard_builder)

                case 5:
                    await self._handle_group_schedule_navigation(callback_query, callback_data, keyboard_builder)

                case 7:
                    await self._handle_schedule_pagination(callback_query, callback_data, keyboard_builder)

                case _:
                    await self.bot.edit_message_text(
                        chat_id=callback_query.message.chat.id,
                        message_id=callback_query.message.message_id,
                        text="Некорректный запрос. Пожалуйста, попробуйте снова."
                    )
        except Exception as e:
            await self.bot.edit_message_text(
                chat_id=callback_query.message.chat.id,
                message_id=callback_query.message.message_id,
                text=f"Произошла ошибка: {str(e)}"
            )

    async def _handle_group_type_selection(self, callback_query, callback_data, keyboard_builder):
        message_to_send = """Выбор группы для получения расписания.\n\nВыберите год группы"""
        type_group = callback_data[2]

        year_groups = sorted(set(
            group.year for group in self.schedule_service.GROUPS if type_group == group.type
        ))

        for year_group in year_groups:
            keyboard_builder.add(
                InlineKeyboardButton(
                    text=year_group, 
                    callback_data=f"name_group_{type_group}_{year_group}"
                )
            )

        await self.bot.edit_message_text(
            chat_id=callback_query.message.chat.id,
            message_id=callback_query.message.message_id,
            text=message_to_send,
            reply_markup=keyboard_builder.as_markup()
        )

    async def _handle_year_group_selection(self, callback_query, callback_data, keyboard_builder):
        message_to_send = """Выбор группы для получения расписания.\n\nВыберите номер группы"""
        type_group = callback_data[2]
        year_group = callback_data[3]

        number_groups = sorted(set(
            group.number for group in self.schedule_service.GROUPS 
            if type_group == group.type and year_group == group.year
        ))

        for number_group in number_groups:
            keyboard_builder.add(
                InlineKeyboardButton(
                    text=number_group, 
                    callback_data=f"name_group_{type_group}_{year_group}_{number_group}"
                )
            )

        await self.bot.edit_message_text(
            chat_id=callback_query.message.chat.id,
            message_id=callback_query.message.message_id,
            text=message_to_send,
            reply_markup=keyboard_builder.as_markup()
        )

    async def _handle_group_schedule_navigation(self, callback_query, callback_data, keyboard_builder):
        name_group = callback_data[2]
        year_group = callback_data[3]
        number_group = callback_data[4]

        keyboard_builder.row(
            InlineKeyboardButton(text="<", callback_data=f"name_group_{name_group}_{year_group}_{number_group}_0_<"),
            InlineKeyboardButton(text="Сегодня", callback_data=f"name_group_{name_group}_{year_group}_{number_group}_0_-"),
            InlineKeyboardButton(text=">", callback_data=f"name_group_{name_group}_{year_group}_{number_group}_0_>")
        )

        schedule_text = self.schedule_service.api.fetch_schedule_description().last_category.name

        await self.bot.edit_message_text(
            chat_id=callback_query.message.chat.id,
            message_id=callback_query.message.message_id,
            text=schedule_text,
            reply_markup=keyboard_builder.as_markup()
        )

    async def _handle_schedule_pagination(self, callback_query, callback_data, keyboard_builder):
        name_group = callback_data[2]
        year_group = callback_data[3]
        number_group = callback_data[4]
        delta = int(callback_data[5])
        action = callback_data[6]

        delta = delta - 1 if action == "<" else delta + 1 if action == ">" else 0

        keyboard_builder.row(
            InlineKeyboardButton(text="<", callback_data=f"name_group_{name_group}_{year_group}_{number_group}_{delta}_<"),
            InlineKeyboardButton(text="Сегодня", callback_data=f"name_group_{name_group}_{year_group}_{number_group}_{delta}_-"),
            InlineKeyboardButton(text=">", callback_data=f"name_group_{name_group}_{year_group}_{number_group}_{delta}_>")
        )

        schedule_text = self.schedule_service.api.fetch_schedule_description().last_category.name

        await self.bot.edit_message_text(
            chat_id=callback_query.message.chat.id,
            message_id=callback_query.message.message_id,
            text=schedule_text,
            reply_markup=keyboard_builder.as_markup()
        )


    def _installKeyboardStart(self):
        keyboard = [
            [KeyboardButton(text='Расписание'), ], 
            [KeyboardButton(text='Новости'), ],
            [KeyboardButton(text='Вход'), KeyboardButton(text='GPT'), KeyboardButton(text='Настройки')] # , web_app=WebAppInfo(url="https://core.telegram.org/bots/webapps")
        ]
        return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)

