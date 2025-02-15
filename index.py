import datetime
import re
from schedule_list import schedule

DAYS = ['понедельник', 'вторник', 'среда',
        'четверг', 'пятница', 'суббота', 'воскресенье']


def handler(event, context):
    # Базовая структура ответа навыка Алисы
    response = {
        "version": event.get("version", "1.0"),
        "session": event.get("session", {}),
        "response": {
            "text": "На какой день недели вам нужно расписание?",
            "end_session": False
        },
    }

    # Вспомогательные функции для работы с датами и расписанием
    def get_current_week_type():
        """Определяет текущий тип недели (числитель/знаменатель) по ISO номеру недели"""
        now_utc_plus3 = datetime.datetime.utcnow(
        ) + datetime.timedelta(hours=3)  # Московское время
        week_number = now_utc_plus3.date().isocalendar()[1]
        return 'числитель' if week_number % 2 == 0 else 'знаменатель'

    def get_current_day():
        """Возвращает текущий день недели на московском времени"""
        now_utc_plus3 = datetime.datetime.utcnow() + datetime.timedelta(hours=3)
        return DAYS[now_utc_plus3.weekday()]

    def get_day_by_offset(offset):
        """Возвращает день недели через смещение дней от текущей даты"""
        now_utc_plus3 = datetime.datetime.utcnow() + datetime.timedelta(hours=3)
        target_day = now_utc_plus3.date() + datetime.timedelta(days=offset)
        return DAYS[target_day.weekday()]

    def get_current_pair(day, week_type):
        """Возвращает текущую пару или время до конца пары"""
        now_utc_plus3 = datetime.datetime.utcnow() + datetime.timedelta(hours=3)
        current_time = now_utc_plus3.time()
        pairs = schedule[day][week_type]

        # Проверяем каждую пару в расписании
        for pair in pairs:
            start_time = datetime.datetime.strptime(
                pair['начало'], '%H:%M').time()
            end_time = datetime.datetime.strptime(
                pair['конец'], '%H:%M').time()

            # Если текущее время попадает в интервал пары
            if start_time <= current_time <= end_time:
                time_left = end_time - now_utc_plus3.time()
                minutes_left = int(time_left.total_seconds() // 60)
                return f"Сейчас идет {pair['номер']}-я пара: {pair['пара']}. До конца {minutes_left} минут."

        return "В данный момент никакая пара не идет."

    def find_day_regex(user_input):
        """Поиск дня недели во вводе пользователя с использованием регулярных выражений"""
        for day in DAYS:
            # Проверка первых 4 символов дня недели для устойчивости к опечаткам
            if re.search(r'\b{}'.format(re.escape(day[:4])), user_input):
                return day
        return None

    # Основная логика обработки запроса
    if "request" in event and "original_utterance" in event["request"]:
        user_input = event["request"]["original_utterance"].lower().strip()
        week_type = get_current_week_type()

        # Обработка при запуске навыка
        if user_input == "":
            response["response"]["text"] = f"Привет! Это навык умное расписание. На какой день недели вам нужно расписание?"
            return response

        # Определение типа недели по запросу
        if re.search(r'\b(сейчас|какая)\b.*\b(числитель|знаменатель|неделя)\b', user_input):
            response["response"]["text"] = f"Сейчас {week_type}."
            return response

        # Проверка текущей пары
        if re.search(r'\b(какая)\b.*\b(пара)\b', user_input):
            day = get_current_day()
            response["response"]["text"] = get_current_pair(day, week_type)
            return response

        # Определение запрашиваемого дня
        if "сегодня" in user_input:
            day = get_current_day()
        elif "завтра" in user_input:
            day = get_day_by_offset(1)
        elif "вчера" in user_input:
            day = get_day_by_offset(-1)
        else:
            # Поиск по частичному совпадению
            day = find_day_regex(user_input)

        # Если день не найден
        if not day:
            response["response"]["text"] = "Ой-ой, что-то я вас не поняла. Давайте попробуем снова."
            return response

        # Формирование ответа с расписанием
        pairs = schedule[day][week_type]
        if not pairs:
            response["response"]["text"] = "Ура-ура! На этот день пар нет. Хорошо отдохните."
            return response

        response_text = f"Расписание на {day}. День начинается с {pairs[0]['номер']} пары.\n" + "\n".join(
            [f"{p['номер']} пара - {p['пара']}" for p in pairs])
        response["response"]["text"] = response_text

    return response
