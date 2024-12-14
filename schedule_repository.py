import os
import json
from datetime import datetime, timedelta
from typing import Dict

from models import Schedule
from stankin_api import StankinAPI


class ScheduleRepository():
    CACHE_FILE = "schedules_cache.json"
    CACHE_TTL = timedelta(days=1)

    def __init__(self, api: StankinAPI):
        self.api = api
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

    def get_schedule(self, category: str, group: str) -> Schedule:

        if self.is_cache_valid(group):
            return self.cache[group]
        
        # Если кэш устарел, обновляем расписание
        schedule = api.fetch_schedule(category, group)
        self.cache[group] = schedule
        self._save_cache()
        return schedule


# Инициализация и использование
api = StankinAPI()
repository = ScheduleRepository(api)


# Получение расписания для группы "GroupA"
group_name = "ИДБ-23-14"
schedule = repository.get_schedule(api.fetch_schedule_description().last_category.name, group_name)
print(f"Schedule for {group_name}: {schedule}\n")

# Получение расписания для группы "GroupB"
group_name = "ИДБ-23-13"
schedule = repository.get_schedule(api.fetch_schedule_description().last_category.name, group_name)
print(f"Schedule for {group_name}: {schedule}\n")