# Умное расписание для Яндекс.Алисы

<p align="center">
      <img src="https://github.com/user-attachments/assets/d3476f53-fb1f-4f91-84aa-765c46a9c858" alt="Project Logo" width="720">
</p>

Этот навык для Яндекс.Алисы помогает студентам отслеживать расписание занятий с автоматическим определением типа недели (числитель/знаменатель) и показывает актуальные пары на любой день.

## Особенности
- Автоматическое определение текущей недели по ISO стандарту
- Поддержка только по Московскому времени
- Определение текущей пары и времени до ее конца
- Гибкая настройка расписания
- Работа с относительными датами (сегодня/завтра/вчера)

## Установка и настройка

1. **Создайте функцию в Yandex.Cloud**
   - Перейдите в [Yandex Cloud Console](https://console.cloud.yandex.ru/)
   - Создайте новую функцию в разделе "Cloud Functions"
   - Скопируйте код из `index.py` в редактор
     
2. **Настройте расписание**
   - Отредактируйте словарь `schedule` в файле `schedule_list.py`

3. **Опубликуйте навык в Яндекс.Диалогах**
   - Создайте новый навык в [Яндекс.Диалоги](https://dialogs.yandex.ru/developer/)
   - В Backend выбериите "Функция в Яндекс Облаке" и потом выберите саму функцию
   - Настройте интерфейс: Добавьте иконку и описание
   - Опубликуйте приватную версию для тестирования (доступ к навыку будите иметь только ваш аккаунт и все кто взаимодействует с вашей колонкой)

## Кастомизация
Вы можете:
- Менять названия предметов в `schedule`
- Добавлять/удалять дни недели
- Изменять временные интервалы пар

Не рекомендуется:
- Менять структуру словаря `schedule`

## Примеры запросов
- "Какие пары в пятницу?"
- "Какая пара сейчас идет?"
- "Сейчас числитель или знаменатель?"
- "Расписание на завтра"
- "Какие пары были вчера?"

<p align="center">
      <img src="https://github.com/user-attachments/assets/1255e87f-bc9d-4129-b4a9-1dc83ffe9080" alt="Example" width="720">
</p>

## Логика работы
1. Определение текущего дня и времени с поправкой +3 часа к UTC
2. Расчет типа недели: четные ISO недели → числитель
3. Поиск совпадений по первым 4 буквам дней недели
4. Форматирование ответа с нумерацией пар
