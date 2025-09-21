import datetime
import re
from schedule_list import schedule, config

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
        """Определяет текущий тип недели (числитель/знаменатель) по учебным неделям"""
        now_utc_plus3 = (datetime.datetime.utcnow() +
                         datetime.timedelta(hours=config['timezone_offset_hours']))
        current_date = now_utc_plus3.date()

        # Определяем начало учебного года
        current_year = current_date.year
        academic_year_start = datetime.date(
            current_year,
            config['academic_year_start_month'],
            config['academic_year_start_day']
        )

        # Если сейчас до начала учебного года, то берем предыдущий учебный год
        if current_date < academic_year_start:
            academic_year_start = datetime.date(
                current_year - 1,
                config['academic_year_start_month'],
                config['academic_year_start_day']
            )

        # Вычисляем количество недель с начала учебного года
        days_since_start = (current_date - academic_year_start).days
        academic_week_number = (days_since_start // 7) + 1

        # Четные учебные недели - числитель, нечетные - знаменатель
        return 'числитель' if academic_week_number % 2 == 0 else 'знаменатель'

    def get_academic_week_info(date=None):
        """Возвращает информацию об учебной неделе для отладки"""
        if date is None:
            now_utc_plus3 = (datetime.datetime.utcnow() +
                             datetime.timedelta(hours=config['timezone_offset_hours']))
            current_date = now_utc_plus3.date()
        else:
            current_date = date

        current_year = current_date.year
        academic_year_start = datetime.date(
            current_year,
            config['academic_year_start_month'],
            config['academic_year_start_day']
        )

        if current_date < academic_year_start:
            academic_year_start = datetime.date(
                current_year - 1,
                config['academic_year_start_month'],
                config['academic_year_start_day']
            )

        days_since_start = (current_date - academic_year_start).days
        academic_week_number = (days_since_start // 7) + 1
        week_type = 'числитель' if academic_week_number % 2 == 0 else 'знаменатель'

        # ISO неделя для сравнения
        iso_week = current_date.isocalendar()[1]

        return {
            'date': current_date,
            'academic_week': academic_week_number,
            'week_type': week_type,
            'iso_week': iso_week,
            'academic_year_start': academic_year_start
        }

    def get_current_day():
        """Возвращает текущий день недели на московском времени"""
        now_utc_plus3 = (datetime.datetime.utcnow() +
                         datetime.timedelta(hours=config['timezone_offset_hours']))
        return DAYS[now_utc_plus3.weekday()]

    def get_day_by_offset(offset):
        """Возвращает день недели через смещение дней от текущей даты"""
        now_utc_plus3 = (datetime.datetime.utcnow() +
                         datetime.timedelta(hours=config['timezone_offset_hours']))
        target_day = now_utc_plus3.date() + datetime.timedelta(days=offset)
        return DAYS[target_day.weekday()]

    def get_current_pair(day, week_type):
        """Возвращает текущую пару или время до конца пары"""
        now_utc_plus3 = (datetime.datetime.utcnow() +
                         datetime.timedelta(hours=config['timezone_offset_hours']))
        current_time = now_utc_plus3.time()
        pairs = schedule.get(day, {}).get(week_type, [])

        # Проверяем каждую пару в расписании
        for pair in pairs:
            start = datetime.datetime.strptime(pair['начало'], '%H:%M').time()
            end = datetime.datetime.strptime(pair['конец'], '%H:%M').time()

            # Если текущее время попадает в интервал пары
            if start <= current_time <= end:
                minutes_left = (datetime.datetime.combine(datetime.date.today(), end) -
                                datetime.datetime.combine(datetime.date.today(), current_time)).seconds // 60
                return f"Сейчас {pair['номер']}-я пара: {pair['пара']}. До конца {minutes_left} мин."

        return "Сейчас пар нет."

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
            response["response"]["text"] = f"На какой день нужно расписание?"
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
            response["response"]["text"] = "Я вас не поняла. Повторите еще раз."
            return response

        # Формирование ответа с расписанием
        pairs = schedule[day][week_type]
        if not pairs:
            response["response"]["text"] = "Ура! На этот день пар нет. Хорошо отдохните."
            return response

        # Формируем расписание с разным форматом для первой и остальных пар
        schedule_lines = []
        for i, p in enumerate(pairs):
            if i == 0:  # Первая пара
                schedule_lines.append(f"{p['номер']}-я пара {p['пара']}")
            else:  # Остальные пары
                schedule_lines.append(f"{p['номер']}-я {p['пара']}")

        response_text = f"Расписание на {day}.\n" + "\n".join(schedule_lines)
        response["response"]["text"] = response_text

    return response
