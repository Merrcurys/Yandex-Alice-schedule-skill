""" Консольный тестер для навыка Алисы "Умное расписание" """

from index import handler


def create_test_event(user_input):
    """Создает тестовое событие для навыка Алисы"""
    return {
        "version": "1.0",
        "session": {
            "session_id": "test_session",
            "user_id": "test_user",
            "new": False
        },
        "request": {
            "command": user_input,
            "original_utterance": user_input,
            "type": "SimpleUtterance"
        }
    }


def main():
    """Основная функция для интерактивного тестирования"""
    print("=== Тестер навыка 'Умное расписание' ===")
    print("Введите команду для Алисы (или 'exit' для выхода):")
    print("Примеры команд:")
    print("- 'понедельник' - расписание на понедельник")
    print("- 'сегодня' - расписание на сегодня")
    print("- 'завтра' - расписание на завтра")
    print("- 'какая неделя' - узнать тип недели")
    print("- 'какая пара' - узнать текущую пару")
    print()

    while True:
        try:
            user_input = input("Вы: ").strip()

            if user_input.lower() in ['exit', 'выход', 'quit']:
                print("До свидания!")
                break

            if not user_input:
                continue

            # Создаем тестовое событие
            event = create_test_event(user_input)

            # Вызываем обработчик навыка
            response = handler(event, {})

            # Выводим ответ Алисы
            alice_response = response.get("response", {}).get(
                "text", "Ошибка: нет ответа")
            print(f"Алиса: {alice_response}")
            print()

        except KeyboardInterrupt:
            print("\nДо свидания!")
            break
        except Exception as e:
            print(f"Ошибка: {e}")
            print()


if __name__ == "__main__":
    main()
