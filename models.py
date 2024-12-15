from dataclasses import asdict, dataclass
from datetime import datetime
import json
from aiogram.fsm.state import StatesGroup, State
from typing import List

@dataclass
class ScheduleTime:
    start: str
    end: str

@dataclass
class ScheduleDate:
    frequency: str
    date: str

@dataclass
class ScheduleItem:
    title: str
    lecturer: str
    type: str
    subgroup: str
    classroom: str
    time: ScheduleDate
    dates: List[ScheduleTime]

@dataclass
class Schedule:
    timestamp: datetime
    group: str
    items: List[ScheduleItem]

@dataclass
class ScheduleCategory:
    name: str
    year: int

@dataclass
class ScheduleDescription:
    last_update: str
    last_category: ScheduleCategory
    categories: List[ScheduleCategory]

@dataclass
class Group:
    full_name: str
    type: str
    year: str
    number: str

class ScheduleStates(StatesGroup):
    SELECT_GROUP_TYPE = State()
    SELECT_YEAR_GROUP = State()
    SELECT_NUMBER_GROUP = State()
    NAVIGATE_SCHEDULE = State()