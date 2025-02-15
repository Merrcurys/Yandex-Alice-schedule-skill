import datetime
import re

from schedule_list import schedule


def handler(event, context):
    response = {
        "version": event.get("version", "1.0"),
        "session": event.get("session", {}),
        "response": {
            "text": "На какой день недели вам нужно расписание?",
            "end_session": False
        },
    }

    def get_current_week_type():
        now_utc_plus3 = datetime.datetime.utcnow() + datetime.timedelta(hours=3)
        today = now_utc_plus3.date()
        week_number = today.isocalendar()[1]
        return 'числитель' if week_number % 2 == 0 else 'знаменатель'

    def get_current_day():
        now_utc_plus3 = datetime.datetime.utcnow() + datetime.timedelta(hours=3)
        days = ['понедельник', 'вторник', 'среда',
                'четверг', 'пятница', 'суббота', 'воскресенье']
        return days[now_utc_plus3.weekday()]

    def get_day_by_offset(offset):
        now_utc_plus3 = datetime.datetime.utcnow() + datetime.timedelta(hours=3)
        target_day = now_utc_plus3.date() + datetime.timedelta(days=offset)
        days = ['понедельник', 'вторник', 'среда',
                'четверг', 'пятница', 'суббота', 'воскресенье']
        return days[target_day.weekday()]

    def get_current_pair(day, week_type):
        now_utc_plus3 = datetime.datetime.utcnow() + datetime.timedelta(hours=3)
        current_time = now_utc_plus3.time()
        pairs = schedule[day][week_type]

        for pair in pairs:
            start_time = datetime.datetime.strptime(
                pair['начало'], '%H:%M').time()
            end_time = datetime.datetime.strptime(
                pair['конец'], '%H:%M').time()

            if start_time <= current_time <= end_time:
                end_datetime = datetime.datetime.combine(
                    now_utc_plus3.date(), end_time)
                time_left = end_datetime - now_utc_plus3
                minutes_left = int(time_left.total_seconds() // 60)
                return f"Сейчас идет {pair['номер']}-я пара: {pair['пара']}. До конца {minutes_left} минут."

        return "В данный момент никакая пара не идет."

    def find_day_regex(user_input):
        days = ['понедельник', 'вторник', 'среда',
                'четверг', 'пятница', 'суббота', 'воскресенье']
        for day in days:
            if re.search(r'\b{}'.format(re.escape(day[:4])), user_input):
                return day
        return None

    if "request" in event and "original_utterance" in event["request"]:
        user_input = event["request"]["original_utterance"].lower().strip()
        week_type = get_current_week_type()

        if user_input == "":
            response["response"]["text"] = f"Привет! Это навык умное расписание. На какой день недели вам нужно расписание?"
            return response

        if re.search(r'\b(сейчас|какая)\b.*\b(числитель|знаменатель|неделя)\b', user_input):
            response["response"]["text"] = f"Сейчас {week_type}."
            return response

        if re.search(r'\b(какая сейчас пара|сейчас идет пара)\b', user_input):
            day = get_current_day()
            response["response"]["text"] = get_current_pair(day, week_type)
            return response

        day = None
        if "сегодня" in user_input:
            day = get_current_day()
        elif "завтра" in user_input:
            day = get_day_by_offset(1)
        elif "вчера" in user_input:
            day = get_day_by_offset(-1)
        else:
            day = find_day_regex(user_input)

        if day:
            if day in schedule:
                pairs = schedule[day][week_type]
                if pairs:
                    response_text = f"Расписание на {day}. День начинается с {pairs[0]['номер']} пары.\n" + "\n".join(
                        [f"{p['номер']} пара - {p['пара']}" for p in pairs])
                else:
                    response_text = f"Ура-ура! На этот день пар нет. Хорошо отдохните."
                response["response"]["text"] = response_text
            else:
                response["response"]["text"] = "День не найден в расписании."
        else:
            response["response"]["text"] = "Ой-ой, что-то я вас не поняла. Давайте попробуем снова."

    return response
