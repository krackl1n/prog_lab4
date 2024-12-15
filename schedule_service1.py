from collections import defaultdict
from datetime import datetime, timedelta

# from stankin_api import fetch_description_schedules, fetch_groups, fetch_schedule


days_of_week_names = ['Понедельник', 'Вторник', 'Среда', 'Четверг', 'Пятница', 'Суббота', 'Воскресенье']
name_of_classes = {"Lecture": "Лекция", "Seminar": "Семинар", "Laboratory": "Лаб. работа / подгруппа: ",}

class ScheduleService1():
    def __init__(self, schedule_repository):
        self.schedule_repository = schedule_repository
        

# def get_categories():
#     categories = []
#     for category in fetch_description_schedules()['categories_ext']:
#         categories.append(category['name'])
#     return categories

# # Сравнивает день недели у дат. На вход принимает дату в формате datetime
# def compare_weekday(first_date, second_date):
#     return first_date.weekday() == second_date.weekday()

# def date_range(date_info):
#     date_range = date_info.split("-")
#     start_date = datetime.strptime(date_range[0], "%Y.%m.%d")
#     data = {
#         "start": start_date,
#         "end": datetime.strptime(date_range[1], "%Y.%m.%d") if len(date_range) > 1 else start_date,
#     }
#     return data

# def get_schedule_to_day(category, group, delta):
#     schedule = fetch_schedule(category, group)
#     checkDate = datetime.now().date() + timedelta(days=delta)
#     schedule_to_day = []
#     for entry in schedule:
#         for date_info in entry["dates"]:
#             date_schedule = date_range(date_info["date"])
#             if (date_schedule["start"].date() <= checkDate <= date_schedule["end"].date()) and compare_weekday(date_schedule["start"], checkDate):
#                 if(entry["subgroup"] == "Common"):
#                     entry["subgroup"] = ""
#                 schedule_to_day.append(entry)
#                 break
#     return schedule_to_day

# async def get_message_with_schedule(category, group, delta):
#     schedule_to_day = get_schedule_to_day(category, group, delta)
#     checkDate = datetime.now().date() + timedelta(days=delta)
#     message = f"📅Расписание {group}\n{checkDate} ({days_of_week_names[checkDate.weekday()]})\n\n"
#     for entry in schedule_to_day:
#         message += f"[{entry['time']['start']} - {entry['time']['end']}] {name_of_classes[entry['type']]} {entry['subgroup']}:\n{entry['title']}.\nКабинет {entry['classroom']}.\nПреподаватель: {entry['lecturer']}\n\n"
#         #message += (f"[{entry['time']['start']} - {entry['time']['end']}] {entry['title'] } - {name_of_classes[entry['type']]}{entry['subgroup']}. Кабинет {entry['classroom']}.\n Преподаватель: {entry['lecturer']}\n\n")
#     return message

# def set_groups(groups, category):
#     group_items = fetch_groups(category)
#     groups.clear()
#     for path_group in group_items["items"]:
#         group = path_group["name"].split('/')[-1].split('.')[0]
#         groups.append(group)

# def get_dict_groups(groups, category):
#     set_groups(groups, category)
#     group_dict = defaultdict(lambda: defaultdict(list))
#     for group in groups:
#         parts = group.split('-')
#         name = parts[0]
#         year = parts[1]
#         number = parts[2]
#         group_dict[name][year].append(number)
#     result = {name: {year: [number for number in groups[year]] for year in groups} for name, groups in group_dict.items()}
#     return result
