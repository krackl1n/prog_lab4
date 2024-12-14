from datetime import date, datetime
import sys
from typing import List
import httpx
from urllib.parse import quote
from datetime import datetime

from models import Group, Schedule, ScheduleCategory, ScheduleDate, ScheduleDescription, ScheduleItem, ScheduleTime

class StankinAPI:
    BASE_URL = "https://firebasestorage.googleapis.com/v0/b/stankinschedule.appspot.com/o"

    def fetch_schedule_description(self) -> ScheduleDescription:
        url = f"{self.BASE_URL}/schedules%2Fdescription.json?alt=media"

        response_data = None

        try:
            response = httpx.get(url)
            response.raise_for_status()
            response_data = response.json()
        except httpx.HTTPError as e:
            print(f"HTTP error occurred: {e}")
        except Exception as e:
            print(f"An error occurred: {e}")

        schedule_description = ScheduleDescription(
            last_update=response_data['last_update'],
            last_category=ScheduleCategory(
                name=response_data['categories'][0],
                year=0
            ),
            categories=[]
        )

        schedule_description.categories = [
            ScheduleCategory(
                name=scheduleCategory['name'],
                year=int(scheduleCategory['year'])
            )
            for scheduleCategory in response_data['categories_ext']
        ]

        return schedule_description
    
    def fetch_groups(self, category: str) -> List[Group]:
        url = f"{self.BASE_URL}?prefix=schedules%2F{quote(category)}%2F&delimiter=/"
        
        response_data = None

        try:
            response = httpx.get(url)
            response.raise_for_status()
            response_data = response.json()
        except httpx.HTTPError as e:
            print(f"HTTP error occurred: {e}")
        except Exception as e:
            print(f"An error occurred: {e}")

        groups = []
        for item in response_data['items']:
            name_parts = item['name'].split("/")[-1].split("-")
            group = Group(
                full_name=item['name'].split("/")[-1].split(".")[0],
                type=name_parts[0],
                year=name_parts[1],
                number=name_parts[2].split(".")[0],
            )
            groups.append(group)

        return groups

    def fetch_schedule(self, category: str, group: str) -> Schedule:
        url = f"{self.BASE_URL}/schedules%2F{quote(category)}%2F{quote(group)}.json?alt=media"

        response_data = None

        try:
            response = httpx.get(url)
            response.raise_for_status()
            response_data = response.json()
        except httpx.HTTPError as e:
            print(f"HTTP error occurred: {e}")
        except Exception as e:
            print(f"An error occurred: {e}")

        items = []

        for lesson in response_data:
            time = ScheduleTime(
                start=lesson["time"]["start"],
                end=lesson["time"]["end"]
            )

            dates = [ScheduleDate(frequency=d["frequency"], date=d["date"]) for d in lesson["dates"]]

            item = ScheduleItem(
                title=lesson["title"],
                lecturer=lesson.get("lecturer", "Unknown"),
                type=lesson["type"],
                subgroup=lesson["subgroup"],
                classroom=lesson.get("classroom", "Not specified"),
                time=time,
                dates=dates
            )

            items.append(item)

        return Schedule(timestamp=datetime.now(), group=group, items=items)


# api = StankinAPI()
# data = api.fetch_schedule(category=api.fetch_schedule_description().last_category.name, group="ИДБ-23-14")
# print(data, "\n")