import os
import json
from datetime import date, datetime, timedelta
from typing import Dict, List

from models import Group, Schedule, ScheduleDate, ScheduleItem
from stankin_api import StankinAPI


class ScheduleService():
    CACHE_FILE = "schedules_cache.json"
    CACHE_TTL = timedelta(days=1)

    def __init__(self, api: StankinAPI):
        self.api = api
        print("init repo")
        # todo Сделать обновление каждый день
        self.CATEGORY = api.fetch_schedule_description().last_category.name
        self.GROUPS: Group = api.fetch_groups(self.CATEGORY)
        self.cache = {}

    def _load_cache(self) -> Dict[str, dict]:
        """Загружает кэш из файла."""
        pass

    def _save_cache(self):
        """Сохраняет кэш в файл."""
        pass

    def is_cache_valid(self, group: str) -> bool:
        if group not in self.cache:
            return False
        return datetime.now() - self.cache[group].timestamp < self.CACHE_TTL

    def get_schedule(self, group: str, category: str = None) -> Schedule:
        if not category:
            category = self.CATEGORY

        if self.is_cache_valid(group):
            return self.cache[group]
        
        # Если кэш устарел, обновляем расписание
        schedule = self.api.fetch_schedule(category, group)
        self.CATEGORY = self.api.fetch_schedule_description().last_category.name
        self.GROUPS: Group = self.api.fetch_groups(self.CATEGORY)
        self.cache[group] = schedule
        self._save_cache()
        return schedule
    
    def get_schedule_to_day(self, group: str, delta: int, category: str = None) -> Schedule:
        schedule = self.get_schedule(group, category)
        check_date = datetime.now().date() + timedelta(days=delta)

        schedule_to_day_items: List[ScheduleItem] = []
        
        for item in schedule.items:
            if self._date_range(item.dates, check_date):
                schedule_to_day_items.append(item)

        return Schedule(schedule.timestamp, group, schedule_to_day_items)
    
    def _parse_date_range(self, date_str):
        """
        Парсит строку с датой или диапазоном дат и возвращает дату или кортеж дат.
        """
        if "-" in date_str:
            start_date_str, end_date_str = date_str.split("-")
            return datetime.strptime(start_date_str.strip(), "%Y.%m.%d").date(), datetime.strptime(end_date_str.strip(), "%Y.%m.%d").date()
        return datetime.strptime(date_str.strip(), "%Y.%m.%d").date()

    def _date_range(self, schedule_dates: List[ScheduleDate], check_date: date = datetime.now().date()) -> bool:
        """
        Проверяет, попадает ли заданная дата (check_date) в расписание (schedule_date).
        """
        for schedule_date in schedule_dates: 

            frequency = schedule_date.frequency

            if frequency == "once":
                event_date = self._parse_date_range(schedule_date.date)
                if event_date == check_date: return True

            elif frequency == "every":
                start_date, end_date = self._parse_date_range(schedule_date.date)
                # Событие происходит каждую неделю в указанный день недели
                if start_date <= check_date <= end_date and (check_date - start_date).days % 7 == 0: return True

            elif frequency == "throughout":
                start_date, end_date = self._parse_date_range(schedule_date.date)
                # Событие происходит раз в две недели
                delta_weeks = (check_date - start_date).days // 7
                if start_date <= check_date <= end_date and delta_weeks % 2 == 0 and (check_date - start_date).days % 7 == 0: return True
        return False


