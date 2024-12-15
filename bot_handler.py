from datetime import datetime, timedelta
from typing import List
from aiogram import Bot, Router, types, Dispatcher, F
from aiogram.types import InlineKeyboardButton, Message, KeyboardButton, ReplyKeyboardMarkup
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.fsm.storage.memory import MemoryStorage

from models import Schedule, ScheduleStates
from schedule_service import ScheduleService

days_of_week_names = ['Понедельник', 'Вторник', 'Среда', 'Четверг', 'Пятница', 'Суббота', 'Воскресенье']
types_schedule = {"Lecture": "Лекция", "Seminar": "Семинар", "Laboratory": "Лаб. работа / подгруппа: ",}
class BotHandlers:
    version = "0.0.2"

    def __init__(self, bot: Bot, schedule_service: ScheduleService):
        self.bot = bot
        self.schedule_service = schedule_service

    async def start(self, message: Message):
        """Приветственное сообщение с выбором опций."""
        keyboard = [
            [KeyboardButton(text='Расписание'), ], 
            [KeyboardButton(text='Новости'), ],
            [KeyboardButton(text='Вход'), KeyboardButton(text='GPT'), KeyboardButton(text='Настройки')] # , web_app=WebAppInfo(url="https://core.telegram.org/bots/webapps")
        ]
        markup = ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True) 
        await message.answer(
            f"Добро пожаловать в расписание mood stankin!\nВерсия: {self.version} by splash team / krackl1n",
            reply_markup=markup
        )

    async def schedule_start(self, message: Message):
        """Начало выбора расписания: выбор типа группы."""
        keyboard_builder = InlineKeyboardBuilder()

        types_group = sorted(set(group.type for group in self.schedule_service.GROUPS))
        for group_type in types_group:
            keyboard_builder.add(InlineKeyboardButton(text=group_type, callback_data=f"group_{group_type}"))
        keyboard_builder.adjust(5, 6)

        await message.answer("Выберите тип группы:", reply_markup=keyboard_builder.as_markup())

    async def callback_schedule(self, callback_query: types.CallbackQuery):
        await self.bot.answer_callback_query(callback_query.id)
        callback_data = callback_query.data.split('_')
        keyboard_builder = InlineKeyboardBuilder()

        try:
            match len(callback_data):
                case 2:
                    await self._select_group_type(callback_query, keyboard_builder)

                case 3:
                    await self._select_year_group(callback_query, keyboard_builder)

                case 4:
                    await self._select_number_group(callback_query, keyboard_builder)

                case 5:
                    await self._navigate_schedule(callback_query, keyboard_builder)

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
                text=f"Произошла ошибка: {str(e)}\n{callback_query.data}"
            )

    async def _select_group_type(self, callback: types.CallbackQuery, keyboard_builder: InlineKeyboardBuilder):
        """Выбор года группы после выбора типа."""
        group_type = callback.data.split("_")[1]
        year_groups = sorted(set(group.year for group in self.schedule_service.GROUPS if group.type == group_type))

        for year in year_groups:
            keyboard_builder.add(InlineKeyboardButton(text=year, callback_data=f"{callback.data}_{year}"))

        await callback.message.edit_text("Выберите год группы:", reply_markup=keyboard_builder.as_markup())

    async def _select_year_group(self, callback: types.CallbackQuery, keyboard_builder: InlineKeyboardBuilder):
        """Выбор номера группы после выбора года."""
        group_type, year_group = callback.data.split("_")[1:]

        number_groups = sorted(set(
            group.number for group in self.schedule_service.GROUPS 
            if group.type == group_type and group.year == year_group
        ))

        for number in number_groups:
            keyboard_builder.add(InlineKeyboardButton(text=number, callback_data=f"{callback.data}_{number}"))

        await callback.message.edit_text("Выберите номер группы:", reply_markup=keyboard_builder.as_markup())

    async def _select_number_group(self, callback: types.CallbackQuery, keyboard_builder: InlineKeyboardBuilder):
        """Показать расписание и предложить навигацию."""
        group_type, year_group, number_group = callback.data.split("_")[1:]
        group_name = f"{group_type}-{year_group}-{number_group}"

        keyboard_builder.row(
            InlineKeyboardButton(text="<", callback_data=f"{callback.data}_-1"),
            InlineKeyboardButton(text="Сегодня", callback_data=f"{callback.data}_0"),
            InlineKeyboardButton(text=">", callback_data=f"{callback.data}_1")
        )

        try:
            schedule_text = self.generate_text_schedule(group_name)
            response_text = f"Расписание для группы {group_name}:\n{schedule_text}"
        except Exception as e:
            response_text = f"Ошибка при получении расписания для группы {group_name}: {e}"

        await callback.message.edit_text(response_text, reply_markup=keyboard_builder.as_markup())

    async def _navigate_schedule(self, callback: types.CallbackQuery, keyboard_builder: InlineKeyboardBuilder):
        """Навигация по расписанию (вперед, назад, сегодня)."""
        group_type, year_group, number_group, delta = callback.data.split("_")[1:]
        action = int(delta)

        group_name = f"{group_type}-{year_group}-{number_group}"
        
        try:
            schedule = self.generate_text_schedule(group_name, action)
            response_text = f"Расписание для группы {group_name}:\n{schedule}"
        except Exception as e:
            response_text = f"Ошибка при навигации по расписанию для группы {group_name}: {e}"

        callback_mess = "_".join(map(str, callback.data.split("_")[:-1]))

        keyboard_builder.row(
            InlineKeyboardButton(text="<", callback_data=f"{callback_mess}_{action-1}"),
            InlineKeyboardButton(text="Сегодня", callback_data=f"{callback_mess}_0"),
            InlineKeyboardButton(text=">", callback_data=f"{callback_mess}_{action+1}")
        )

        await callback.message.edit_text(response_text, reply_markup=keyboard_builder.as_markup())

    def generate_text_schedule(self, group: str, action: int = 0):
        schedule_to_day = self.schedule_service.get_schedule_to_day(group, action)
        checkDate = datetime.now().date() + timedelta(days=action)
        
        message = f"📅Расписание {group}\n{checkDate} ({days_of_week_names[checkDate.weekday()]})\n\n"
        
        for item in schedule_to_day.items:
            message += f"[{item.time.start} - {item.time.end}] {types_schedule[item.type]} {item.subgroup}:\
            \n{item.title}.\
            \nКабинет {item.classroom}.\
            \nПреподаватель: {item.lecturer}\n\n"
        return message
        