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
    
    def _date_range(self, schedule_date: ScheduleDate, check_date: date = datetime.now().date()) -> bool:
        return False


