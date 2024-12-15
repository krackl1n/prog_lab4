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
    version = "0.0.1"

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

    async def schedule_start(self, message: Message, state: FSMContext):
        """Начало выбора расписания: выбор типа группы."""
        keyboard_builder = InlineKeyboardBuilder()

        types_group = sorted(set(group.type for group in self.schedule_service.GROUPS))
        for group_type in types_group:
            keyboard_builder.add(InlineKeyboardButton(text=group_type, callback_data=f"group_type_{group_type}"))
        keyboard_builder.adjust(6)

        await message.answer("Выберите тип группы:", reply_markup=keyboard_builder.as_markup())
        await state.set_state(ScheduleStates.SELECT_GROUP_TYPE)

    async def select_group_type(self, callback: types.CallbackQuery, state: FSMContext):
        """Выбор года группы после выбора типа."""
        group_type = callback.data.split("_")[2]
        await state.update_data(group_type=group_type)

        year_groups = sorted(set(group.year for group in self.schedule_service.GROUPS if group.type == group_type))
        keyboard_builder = InlineKeyboardBuilder()

        for year in year_groups:
            keyboard_builder.add(InlineKeyboardButton(text=year, callback_data=f"year_{year}"))

        await callback.message.edit_text("Выберите год группы:", reply_markup=keyboard_builder.as_markup())
        await state.set_state(ScheduleStates.SELECT_YEAR_GROUP)

    async def select_year_group(self, callback: types.CallbackQuery, state: FSMContext):
        """Выбор номера группы после выбора года."""
        year_group = callback.data.split("_")[1]
        data = await state.get_data()
        group_type = data["group_type"]
        await state.update_data(year_group=year_group)

        number_groups = sorted(set(
            group.number for group in self.schedule_service.GROUPS 
            if group.type == group_type and group.year == year_group
        ))
        keyboard_builder = InlineKeyboardBuilder()

        for number in number_groups:
            keyboard_builder.add(InlineKeyboardButton(text=number, callback_data=f"number_{number}"))

        await callback.message.edit_text("Выберите номер группы:", reply_markup=keyboard_builder.as_markup())
        await state.set_state(ScheduleStates.SELECT_NUMBER_GROUP)

    async def select_number_group(self, callback: types.CallbackQuery, state: FSMContext):
        """Показать расписание и предложить навигацию."""
        number_group = callback.data.split("_")[1]
        data = await state.get_data()

        group_name = f"{data['group_type']}-{data['year_group']}-{number_group}"
        await state.update_data(group_name=group_name)

        keyboard_builder = InlineKeyboardBuilder()
        keyboard_builder.row(
            InlineKeyboardButton(text="<", callback_data="navigate_-1"),
            InlineKeyboardButton(text="Сегодня", callback_data="navigate_0"),
            InlineKeyboardButton(text=">", callback_data="navigate_1")
        )

        schedule_text = self.generate_text_schedule(group_name)

        try:
            
            response_text = f"Расписание для группы {group_name}:\n{schedule_text}"
        except Exception as e:
            response_text = f"Ошибка при получении расписания для группы {group_name}: {e}"

        await callback.message.edit_text(response_text, reply_markup=keyboard_builder.as_markup())
        await state.set_state(ScheduleStates.NAVIGATE_SCHEDULE)

    async def navigate_schedule(self, callback: types.CallbackQuery, state: FSMContext):
        """Навигация по расписанию (вперед, назад, сегодня)."""
        action = int(callback.data.split("_")[1])
        data = await state.get_data()
        group_name = data["group_name"]

        schedule = self.generate_text_schedule(group_name, action)

        try:
            
            response_text = f"Расписание для группы {group_name}:\n{schedule}"
        except Exception as e:
            response_text = f"Ошибка при навигации по расписанию для группы {group_name}: {e}"

        keyboard_builder = InlineKeyboardBuilder()
        keyboard_builder.row(
            InlineKeyboardButton(text="<", callback_data=f"navigate_{action-1}"),
            InlineKeyboardButton(text="Сегодня", callback_data="navigate_0"),
            InlineKeyboardButton(text=">", callback_data=f"navigate_{action+1}")
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
        